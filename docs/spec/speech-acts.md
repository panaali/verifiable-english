# Speech acts (`speech-acts@0`): commands and questions over `norms@0` and `ve-document@2`

> Status: item-1 specification, draft 4 (2026-09-28), written from [speech-acts-PLAN.md](speech-acts-PLAN.md) draft 5, the
> plan as revised by the converged Astra/Fable design debate (`manage-agents/debates/design-speech-acts/{astra,fable}.md`,
> CONVERGED after round 2, verdict BUILD with exact edits; the plan's section 5 maps each edit). Draft 2 applied, as
> written, the combined edit list of the converged Astra + Fable item-1 statement review
> (`manage-agents/debates/speech-acts-spec/{astra,fable}.md`, CONVERGED after round 2, verdict FIX: Astra's nine
> findings in the forms agreed at round 2 plus Fable's unopposed edits 4 to 7); section 13 maps each edit. The
> edit-verification pass on draft 2 (`manage-agents/speech-acts-p3ver1.final.md`) found two edits incomplete, Astra 3
> (the decoded-source wrapper dropped W2's identity payload and the structure of reading candidates and narrowings) and
> Astra 8 (the `intended-reading` open term was not expressible in W2's frozen open-term schema); draft 3 completes
> exactly those two edits and changes nothing else (section 14). The second pass (`manage-agents/speech-acts-p3ver2.final.md`)
> found one defect that the Astra 3 completion introduced: `source_retained` demanded that a re-encoding of the
> structured reading sets reproduce W2's front-matter bytes, which W2's optional `models` field (omitted or `{}` for a
> singleton reading) makes impossible; draft 4 restates that theorem over the front-matter fields the identity payload
> already retains verbatim and changes nothing else (section 15). The review gates items 2, 3 and 4 (PLAN-EXPAND2
> rule 10) and any implementation: a bounded edit-verification pass by both reviewers on each draft (each checks the
> listed edits are applied as written; new findings are admissible only where an edit introduces a defect), then items
> 2 to 4 start.
> Sections 4 to 6 and 8 are the statements; section 12 lists every point where this draft chose between readings of
> the plan. Theorem statements and fixtures are implementation obligations, not claims of completed proofs or tests.
> Inputs: [norms.md](norms.md) (W1, cited `norms.md n`), [document.md](document.md) (W2), the W3
> [definitions statements](../../lean/VE/Definitions/STATEMENTS.md), [debate-protocol.md](debate-protocol.md) (the
> judgments `follows`, `gap`, `unresolved`), [VISION.md](../../VISION.md), `lean/VE/Norms/*` and
> [lean/NORMS.md](../../lean/NORMS.md) (the W1 Lean names this spec reuses), [INTEGRATION-GAPS.md](../INTEGRATION-GAPS.md)
> (the W1/W3/W5 combinations still closed), the [natural view](../natural-view.md) (`ve.prose@1`). Nothing here changes a
> frozen contract, a `norms@0` or `ve-document@1` hash, a W1 theorem statement or a checker function.

## 0. Scope, one paragraph

A **command** is a scoped demand on a named addressee; a **question** is a request for a response that satisfies a
typed answer contract. Neither asserts its embedded proposition, and reading or checking either never executes anything.
An active authored command elaborates, deterministically and mechanically, into one W1 rule whose consequence atom is
the declared act's regulated predicate and whose guard binds the situation variables to the scope's constants by
equality (norms.md 3.3); W1's applicability, completion and conflict semantics then say what the document's policy
requires, and W1's route theorems carry proof and countermodel results. A question carries a wording-derived response
mode, a closed presupposition formula `H(Q)` and one closed correctness formula `F(a)` per response token; an answer is
supported by a replayed certificate for `H(Q) ∧ F(a)` over the pinned premises, or evaluated in one explicitly supplied
valid model, and lack of proof is UNKNOWN, never "no". Consequence questions and proof tasks reuse the certificate and
countermodel checkers under the debate protocol's `follows`, `gap` and `unresolved`. The report keeps four things apart:
the meaning admitted, the norm outcome and conflict status, the answer evidence and its scope, and the compliance
evidence. Exactly one scope per document, rendered as a writable legend, binds "you", every definite object and the task;
a command with an unbound slot is a repair case; documents with different scopes are never merged into one policy.

In this specification: the scope, commands, questions and queries (1), the English (2), the wire form and identity (3),
the semantics (4), the report (5), the coverage projection (6), diagnostics (7), the Lean definitions and every item-2
theorem as a statement (8), the item-1 acceptance fixtures (9), limits (10), the review checklist (11), the resolved
choices (12), the statement-review response table (13) and the edit-verification response table (14).

Out of scope, by the plan: temporal, causal, epistemic or execution logic in any action name; deadlines, fulfilment over
time, ability and authority; requests, advice, invitations and permission-granting utterances as commands; open-domain
"which" questions, explanations and unrestricted mathematical solutions (they need declared rubrics or richer profiles);
adoption of a quoted command into a policy (no norm bridge exists in W1; 12.8); the English parsing and rendering
implementation, W8 replay/approval and the human fidelity gate (plan items 3 and 5); any coverage number (plan item 5).

## 1. What a speech-act document is

A speech-act document is a `ve-document@2` (3.5) over an environment that enables `speech-acts@0` and `norms@0`, whose
units may be, beside W2's existing kinds, active commands (kind `instruction` with command content), questions (kind
`question` with question content) and authored bindings (kind `binding`). Its policy is a W1 tree (norms.md 1) made of the
document's active norm units and the elaborated active commands; everything W1 requires of that tree holds unchanged.

### 1.1 Scope: task, addressee, definite objects (the legend)

```text
scope(E)     := one per environment, in the `speech_acts` block (3.1), identity-bound like `regulated`:
  task         a token naming the task or session every command and question of the document is about
  addressee    optional: (sort, constant) bound to the word "you"; mandatory when any command or any unit
               mentioning "you" is present (UnboundSlot: you otherwise)
  definites    a finite map from a definite phrase ("the token", "the writing desk") to a declared constant of E;
               the phrase passes the existing template linter (finite word grammar, 80 bytes); a phrase equal to a
               declared constant name, a sort noun or an existing English keyword is InvalidInput
queries(D)   := named pinned premise/target pairs (1.4), in the document front matter
```

The scope is rendered as the **legend** (2.1), exactly as W1 renders the completion defaults as `By default, ...`
(norms.md 2.1, 13.4): legend sentences are not document units, sit outside the byte partition and take no status. The
same sentences are writable: a source may contain them as units of kind `binding` (3.2), in which case each must agree
with the environment block (`BindingConflict` otherwise) or, when the block omits that entry, supplies it; an authored
binding is a typed declaration unit with admitted meaning and is counted like any other unit (6). The environment's
`speech_acts` block is part of the canonical environment bytes, so two documents with different tasks, addressees or
definite bindings have different `environment_id`s (3.5); this is how "one pinned semantic scope per policy evaluation"
is realised at `@0` (4.8).

### 1.2 Commands

```text
command c    := unit id u (the rule name is cmd-<u>); force ∈ {require, forbid}; the declared act (norms.md 3.1 identity:
                ordered argument sorts and canonical act phrase); the predicate realising the force: the act's obligation
                predicate for require, its permission predicate for forbid; args: one bound constant per act slot after
                slot 0 (slot 0 is the addressee, bound by the scope); an optional closed guard G_c over E ("if ...");
                issuer: the document's author, or the attributed agent when the unit is quoted (provenance, not a field)
active       := kind exactly `instruction`, meaning `specified`, command content present, every slot bound, and the
                unit not inside a pending (open) reading set; every other command unit is dormant (1.5)
demand(c)    := the W1 node  name cmd-<u>; pred the realising predicate; sign (force = require); guard
                (x̄ = (you, args)) ∧ G_c written with equality atoms in the predicate's context; no carve-outs; no
                precedence edges (4.2)
policy(D)    := the W1 tree over E: the validated regulated declarations of 3.1 (stored with the document's semantic
                core, 8.1: the frozen `VE.Environment` holds only sorts, symbol signatures and constants, so roles,
                defaults, acts and duals cannot be recovered from it); no definitions (1.6); nodes = the active author
                norm units in document order ++ demand(c) for every active command c in document order
```

A `require` on an act with no declared obligation role is `MissingObligationRole: <act>`; a `forbid` on an act with no
declared permission role is `MissingPermissionRole: <act>`: a prohibition is `¬permitted_act(ā)`, **never**
`¬required_act(ā)` (norms.md 2.1: `must not` is the permission role, `need not` the obligation role), and the checker
does not choose a substitute. When both roles describe one act, W1's mandatory dual link (norms.md 3.1) already holds.
Every realising predicate and its default is declared in the environment as norms.md 3.1 requires, so the W1 legend
(`By default, a user need not click a control.`) renders beside the scope legend; nothing here replaces a default.

The issuer's authority is provenance (the unit's kind and the document's provenance record) or a named assumption; it is
not a theorem and the checker never derives it. Norm checking establishes what the policy requires and whether it can
conflict; it never establishes that the act was done, could be done, by when, or by whose authority (5.4).

### 1.3 Questions and response modes

```text
question q   := unit id u; mode ∈ {polar, which_all, which_one, follows, reading}, derived from the wording (2.1) and
                never authored (a stored mode field is derived content: ModeMismatch when it disagrees, 3.2);
                body: a closed formula (polar, follows) or a formula with one free variable of the alternatives' sort
                (which_all, which_one); domain: for which modes, the listed alternatives, distinct declared constants of
                one sort, in wording order (2 to 16); for follows, a query id (1.4); for reading, a reading-set id and
                version (document.md); asker: the author or the attributed agent (provenance); addressee: the scope's,
                when the wording mentions "you"
tokens(q)    := polar: {yes, no}; which_one: the domain; which_all: every subset S of the domain, including ∅;
                follows: {follows, gap, unresolved} (report outcomes, not answer tokens: 4.6); reading: an index into the
                bound reading set (a nomination, 4.6)
H(q)         := the presupposition, one closed formula:
                polar, which_all, follows:  ⊤
                which_one over {a₁..aₙ}:    (⋁ᵢ P(aᵢ)) ∧ ⋀_{i<j} ¬(P(aᵢ) ∧ P(aⱼ))        exactly one alternative
                reading:                     no formula; the W2 open term named `intended-reading.<u>` and displayed
                                             `intended-reading:<set>@<version>` (4.6): "exactly one intended reading",
                                             decided by the addressee
F(q, a)      := the correctness formula of a token, closed:
                polar:      F(yes) = P,  F(no) = ¬P
                which_one:  F(a) = P(a)
                which_all:  F(S) = ⋀_{a∈S} P(a) ∧ ⋀_{a∈dom∖S} ¬P(a)
```

`P(a)` is W1's capture-avoiding instantiation `inst` of the body at the constant. "Which of Atlas and Beacon" is a
**deliberately restricted named domain**: it presupposes nothing about other services. An open-domain "which" ("Which
services are reviewed?") is outside `@0`: it carries the empirical claim that the names an answer lists exhaust a wider
domain, and the IDE's rewrite to a restricted domain records that domain closure as a named assumption in translation
(2.3, 12.2). Existence and uniqueness for single mode are in `H(q)`, shown in the residual, never inferred from asking.

### 1.4 Queries: pinned premise/target pairs

A consequence question and a proof task are about a **query** `(B_q, P)`: `P` is the target sentence embedded in the
wording; `B_q` is "these premises", which at `@0` denotes the asserted units earlier in the document, in document order,
the `ve.prose@1` convention that a conclusion's dependencies are all earlier unmarked premises (12.3). The query record
(`queries` in the front matter, 3.2) lists the premise unit ids and the target by meaning id; it is derived content,
regenerated from the document at every site and compared (`QueryMismatch` on disagreement). The checked premise list of a
query is `Background(E) ++ elaborate(policy(D)) ++ B_q` (4.6). The target is never added to `B_q`; if the target is
itself an earlier asserted unit, the report says so (`TrivialQuery`, a warning) and the task stands.

A proof task ("Prove that ... using these premises.") is a **command** on the declared act `{0} submit a proof of
{1}` whose second slot has the sort `query` and is bound to the query's constant (the query id is declared as a constant
of that sort in E). It is the one act whose completion the checker itself can witness: a replayed certificate for exactly
`(B_q, P)` is compliance evidence of kind `certificate` (5.4). It establishes certificate validity, not understanding.
The phrase passes W1's frozen act linter unchanged (norms.md 3.1: `for` is a reserved word, so the earlier
`{0} submit a certificate for {1}` was rejected by every checker); no route relaxes that linter (16).

### 1.5 Active and dormant units; what supplies a premise

Only an active command (1.2) and an active author norm unit contribute a W1 rule. A quoted, hedged, attributed or
example command, a command in a pending reading set, a command with an unbound slot, every question, every answer record
and every binding contribute **no premise**. The premises a speech-act document is checked against are exactly

```text
premises(D) := Background(E) ++ elaborate(policy(D)) ++ asserted(D)
```

with `asserted(D)` W2's fixed asserted premises (document.md: fixed assertions and authored singleton choices) and the
layer premises regenerated at every site (norms.md 11.3). No embedded proposition of a command or question is a premise
through its occurrence there (4.7). `policy(D)` itself excludes every pending command: a command inside an open reading
set is dormant (1.2) and contributes no rule to `policy(D)` under any choice. It is W2's readings query (`ve document
readings`, document.md), not `policy(D)`, that checks a reading set over commands or questions per complete compatible
choice, up to W2's limit of 64, regenerating that choice's policy and premises for each; the assertion-disjunction
shortcut (`readings_all_iff`) is inapplicable to such sets.

### 1.6 Supported combinations at `@0`

The route admits an **allowlist** of profiles and nothing else: an environment used by this route enables exactly
`relational-fol@0`, `norms@0` and `speech-acts@0` among statement and checker profiles. `speech-acts@0` without
`norms@0` is `UnsupportedProfile: speech-acts@0 requires norms@0`; every other profile in the environment is
`UnsupportedProfile: speech-acts@0 with <profile>`, in particular `soft-norms@0` (its ranks, defeasible rules and
instruction authority compose with commands in no specified or proved way: the combination is rejected until it is
separately specified and proved, fixture φ), `closure@0`, `order@0` and `nary@0`. W3 `defined` declarations and W5
`functional`/`total` flags in an environment used by this route are `UnsupportedProfile: speech-acts@0 with
<declaration>` (INTEGRATION-GAPS: the norms route rejects them with norm constructs; this route inherits the gate whether
or not a command is present, 12.5). N-ary acts, temporal arguments and existential objects inside an act ("file some
report") follow norms.md 0 and 2.4: the object is inside the declared act phrase or the sentence is not a command.

## 2. The English (one reading each; rejected as today when `speech-acts@0` is off)

### 2.1 Wordings

Every wording has exactly one reading, conditional on the legend, which is itself the first thing the reader sees.
Imperatives are the declared act phrase (norms.md 2.4) with slot 0 dropped and the later slots filled by a declared
constant name or a bound definite phrase, so elaboration to `demand(c)` is mechanical. `<rest>` is the remainder of a
copular predicate wording `{0} is <rest>`; `<sentence>` is any closed sentence of the existing English surface.

| Wording | The one reading (the IDE's paraphrase) | Formal effect |
|---|---|---|
| `This document is task <task>.` (legend) | Every command and question below is about this task and no other. | `scope.task` |
| `In this task, you are <constant>.` (legend) | "You" names this addressee throughout. | `scope.addressee` |
| `In this task, the <noun phrase> is <constant>.` (legend) | This definite phrase names this object throughout. | `scope.definites` |
| `<Act phrase after slot 0, first word capitalised, later slots filled>.` e.g. `Click Check.` | In this task, you are required to click Check. Nothing is claimed about whether you did. | `demand`: `+` on the obligation predicate, guard `x0 = you ∧ x1 = Check` |
| `Do not <act phrase, same shape>.` e.g. `Do not share the token.` | In this task, you are not permitted to share the token. | `demand`: `−` on the permission predicate |
| `..., if <condition>.` on a command | The demand holds only in situations where the condition holds. | guard `G_c` |
| `Is <constant> <rest>?` e.g. `Is Atlas reviewed?` | Asks whether Atlas is reviewed; "yes" is correct exactly when it is, "no" exactly when it is not. | polar, `F(yes) = P`, `F(no) = ¬P` |
| `Is it the case that <sentence>?` | Asks whether the sentence holds; the same contract. | polar over any closed sentence |
| `Which of <A>, <B>[, <C>...] and <Z> are <rest>?` | Asks for the complete list of these named alternatives that are `<rest>`; "none" is a possible answer; nothing is presupposed about anything not named. | which_all, `H = ⊤` |
| `Which one of <A>, ... and <Z> is <rest>?` | Asks which single named alternative is `<rest>`; that exactly one is, is presupposed and shown in the residual. | which_one, `H` = exactly one |
| `Does it follow from these premises that <sentence>?` | Asks whether the sentence follows from the premises above; the answer is a checked proof, a checked counter-situation, or "not established". | follows over query `(B_q, P)` |
| `Prove that <sentence> using these premises.` | In this task, you are required to submit an accepted proof of the sentence from the premises above. The task may be impossible. | command on `{0} submit a proof of {1}` |
| `Which reading did you mean?` (after a reading set) | Asks the addressee which of the displayed readings, at the displayed version, was intended; the reply is testimony. | reading over `(set, version)` |
| `Answer question <n>.` | In this task, you are required to answer that question. | command on `{0} answer {1}` with the question's constant |

The paraphrases never show logic. `you` renders as the addressee's name in the inspector and as "you" in the text;
a definite phrase renders as written and means the bound constant; a constant not bound to a phrase renders by name.
Wordings not in this table are not speech-act wordings (2.3).

### 2.2 Synonyms and non-synonyms

Input synonyms, rendered canonically and shown in the paraphrase: `Please <command>` for `<command>` **only in authoring
after W8 approval** (plan item 3); in translation "please" makes the unit a reading set `{require, request}` whose request
reading is unsupported, so the unit is U (6). `Don't` for `Do not`. Nothing else.

Not synonyms: `Never <act>` (temporal); `You must <act>` and `You may <act>` (the first is a W1 rule with a constant
subject, rejected by W1 with the equality-guarded `Every <noun>` rewrite; the second grants a permission and is not a
command at all: the hint `PermissionNotCommand` offers the W1 rewrite of 2.3, the equality-guarded rule of norms.md 3.3
that keeps the addressee and the object bound, never the universal `Every <noun> may <act>.`, which would broaden one
bound permission to every member of the sort); `Could you <act>?`, `Would you <act>?` (requests; unsupported); `Should
<constant> <act>?` (a soft-norm question; outside this route, 1.6).

### 2.3 How the IDE resolves ambiguity, in English (norms.md 2.6 extended)

| The author wrote | Competing readings shown as paraphrases with an example situation | Rewrites offered |
|---|---|---|
| `Share the token.` with no binding for "the token" | none: the phrase is unbound (`UnboundSlot: the token`) | add the legend sentence `In this task, the token is <constant>.`; in translation the unit is `unformalised(unbound-slot)` |
| `Click Check and save.` | (a) two independent demands; (b) click, then save, in that order (an order the route cannot state) | two commands `Click Check.` `Save.` when no order is meant (authoring, after approval); in translation a reading set {(a), (b)} whose (b) is unsupported, hence U (`CoordinatedActs`) |
| `Must Alice open the desk?` | (a) duty: "Is Alice required to open the desk?" (polar over `open_required(Alice, Desk1)`); (b) necessity: "Does it follow from these premises that Alice opens the desk?" (follows over `done_open(Alice, Desk1)`) | pick (a) or (b); both are elaborated, so in translation the unit is R |
| `Can you open the desk?` | (a) permission: "Are you permitted to open the desk?"; (b) ability (unsupported); (c) request (unsupported) | (a) as `Is it the case that you are permitted to open the desk?`; in translation the set {a, b, c} is U with per-reading residuals |
| `Which services are reviewed?` | open domain: the answer would claim that the listed services are all the services | `Which of Atlas and Beacon are reviewed?` when the sort's constants are known; in translation the narrowing records the domain closure `Every service is Atlas or Beacon.` as a named assumption (`domain-closure:<unit>`) |
| `Did every sampled district report a drop?` | none at `@0`: the past-tense inversion needs an inflection the surface does not infer | `Is it the case that every sampled district reported a drop?` when `{0} reported a drop` is the declared wording |
| `Choose authoring or translation mode.` | none: a disjunction in object position is not a bound object, and no command wording expresses "either mode" | declare the act `{0} choose a mode` (object inside the act, norms.md 2.4) and write `Choose a mode.`, only when that is the meaning; otherwise the unit is U (`unformalised(disjunctive-object)`). Two commands are not offered: two demands are not a choice, so that rewrite would change the meaning |
| `Change example now?` | none: "now" is temporal; the sentence is not a polar wording | `Is it the case that ...` over a declared present-tense wording, without "now"; else `unformalised(temporal)` |
| `You may close the desk.` | not a command wording (`PermissionNotCommand`) | the W1 rule about the bound constants, with both bindings kept by equality guards (norms.md 3.3): `Every user may close each desk, if that user equals Alice and that desk equals Desk1.` (strict `if ((x0 equals @Alice) and (x1 equals @Desk1))`); never the universal `Every user may close each desk.`, which broadens one bound permission to every user and every desk |

The distinguishing situation is a checked finite model rendered in document terms (W8 de-elaboration), as W1.

### 2.4 The reader's checklist (norms.md 2.5 extended)

For every accepted command the assistant shows, in English only: the legend it depends on; the deterministic paraphrase
naming the addressee, the act, the object and the task; the W1 default of the realising predicate; whether the policy
can conflict at that demand and, if so, the witness situation; and the sentence "Nothing here records that the act was
done." For every accepted question: the mode in words ("a yes/no question", "a complete-list question over Atlas and
Beacon", "a single-choice question", "a does-it-follow question", "a which-reading question"); the presupposition in
words when there is one ("exactly one of Atlas and Beacon is reviewed"); the current answer line (5.3) with its evidence
kind and scope ("proved from the premises above", "true in the situation shown, and only there", "not established"); and,
for a question with no answer record, "no answer has been given". For a proof task: the pinned premises and target, and
"an accepted proof shows that the sentence follows from these premises; it does not show that anyone understood it".

## 3. Declarations, wire form, strict form and identity

### 3.1 The environment `speech_acts` block (identity-bound like `regulated`)

```json
"speech_acts": {"task": "tutorial-3",
                "addressee": {"sort": "user", "constant": "Alice"},
                "definites": {"the token": "Token1", "the writing desk": "Desk1", "the desk": "Desk1"}},
"predicates": {"click_required": {"arguments": ["user", "control"], "description": "...",
                                  "regulated": {"role": "obligation", "default": "deny", "act": "{0} click {1}",
                                                "permission": "click_permitted"}},
               "click_permitted": {"arguments": ["user", "control"], "description": "...",
                                   "regulated": {"role": "permission", "default": "allow", "act": "{0} click {1}"}},
               "share_permitted": {"arguments": ["user", "token"], "description": "...",
                                   "regulated": {"role": "permission", "default": "allow", "act": "{0} share {1}"}},
               "submit_required": {"arguments": ["user", "query"], "description": "...",
                                   "regulated": {"role": "obligation", "default": "deny",
                                                 "act": "{0} submit a proof of {1}",
                                                 "permission": "submit_permitted"}}, ...}
```

`task` is a token (`[A-Za-z0-9_.-]`, at most 64 bytes) and mandatory; `addressee.sort` is a declared sort and
`addressee.constant` a declared constant of that sort (`UnknownSymbol` otherwise); `definites` has at most 64 entries,
each phrase distinct after whitespace normalisation, each constant declared. Unknown fields are `InvalidInput:
speech_acts block`. The block is part of the canonical environment bytes, so `environment_id` changes when any of it
changes and is unchanged for every existing environment (none has the block). The `regulated` declarations are W1's
(norms.md 3.1) and unchanged. The sort `query` and one constant per query id are ordinary declarations when the document
uses proof tasks.

### 3.2 Unit contents (W2 units of kinds `instruction`, `question`, `binding`)

```json
{"id": "u1", "span": [0, 12], "kind": "instruction", "meaning": "specified", "support": "none",
 "content": {"command": {"force": "require", "act": "click_required", "args": ["Check"], "guard": ["top"]}}}

{"id": "u7", "span": [120, 138], "kind": "question", "meaning": "specified", "support": "none",
 "content": {"question": {"mode": "which_all", "sort": "service", "domain": ["Atlas", "Beacon"],
                          "body": ["unary", "reviewed", ["var", 0]]}}}

{"id": "u9", "span": [200, 258], "kind": "question", "meaning": "specified", "support": "none",
 "content": {"question": {"mode": "follows", "query": "q1"}}}

{"id": "u6", "span": [300, 327], "kind": "question", "meaning": {"open": ["intended-reading.u6"]}, "support": "none",
 "content": {"question": {"mode": "reading", "set": "rs1", "version": 2}}}   // the open term is declared in 4.6

{"id": "u0", "span": [0, 27], "kind": "binding", "meaning": "specified", "support": "none",
 "content": {"binding": {"you": "Alice"}}}          // or {"phrase": "the token", "constant": "Token1"} or {"task": "tutorial-3"}
```

Front matter additions: `"queries": [{"id": "q1", "premises": ["u3", "u4"], "target": {"ast": [...]}}]` (derived,
regenerated: `QueryMismatch`), `"answers"` and `"compliance"` (3.3); W2's own `open_terms` list carries every
`intended-reading.<u>` declaration (4.6). Command content: `force` ∈ `{require, forbid}`
(`InvalidInput: force` otherwise; permission-granting is not a force); `act` names the realising predicate, whose role
must match the force (`MissingObligationRole` / `MissingPermissionRole`, naming the act phrase); `args` are constants of
the predicate's later sorts, one per slot (`TypeMismatch`); `guard` is a closed formula in the P0 wire form (`["top"]`
when absent). Question content: `mode` is derived content and must equal the mode the wording determines (`ModeMismatch:
<unit>`); `domain` lists 2 to 16 distinct declared constants of `sort` (`UnknownAlternative`, `DuplicateAlternative`,
`AlternativeSort`); `body` is over the context `[sort]` for which modes and closed for polar; `query` names a query for
`follows`; `reading` mode carries `{"set": id, "version": n}`, and a reading question's `meaning` is not `specified`
but `{"open": ["intended-reading.<u>"]}`, naming the derived open-term declaration of 4.6 in the front matter's W2
`open_terms` list (`InvalidInput: invalid question fields for <u>` when the meaning or the declaration differs from
the regenerated form). Binding content is exactly one legend entry. Norm content
under a non-norm kind, command content under a non-instruction kind and question content under a non-question kind are
rejected, never discarded, as W1 rejects misplaced norm content; a quoted kind wrapping `instruction` keeps its command
content dormant and every single-unit check still applies (as W1's `checkQuoted`).

W2's `content` may also be an English or strict fence; the English fence goes through the all-derivations parser and
yields the same command or question object (2.1); the fence's surface and the object are the same unit.

**Binding units and P0.** The frozen P0 kind decoder (`lean/VE/Route/Admission.lean`, `atomicKind`) knows `instruction`
and `question` but not `binding`, and no frozen file changes. `binding` units are therefore **withheld from P0
`admit_document`**, exactly as W2 withholds unsupported non-assertion readings from that route (document.md): they
reach no P0 unit, no graph leaf and no premise. They enter only the route's decoded-source wrapper (8.5), whose report
identity binds them with the rest of the validated source (3.5), and the coverage projection (6), where each is
counted as a unit. Every other unit reaches P0 as W2 sends it today.

### 3.3 Answer and compliance records (document metadata, evidence, never premises)

```json
"answers": [{"question": "u7", "by": "checker", "support": "certificate",
             "answer": {"all": ["Atlas"]}, "evidence": {"certificate": {...}}},
            {"question": "u5", "by": "checker", "support": "certificate", "conditional": true,
             "answer": {"one": "Atlas"}, "evidence": {"certificate": {...}}},
            {"question": "u6", "by": "checker", "support": "model", "answer": "no", "evidence": {"model": {...}}},
            {"question": "u9", "by": "checker", "support": "certificate", "judgment": "follows",
             "evidence": {"certificate": {...}}},
            {"question": "u11", "by": "author", "support": "testimony", "nominate": 0}],
"compliance": [{"command": "u2", "evidence": {"certificate": {...}}},
               {"command": "u1", "evidence": {"unit": "u12"}}]
```

An answer record's `answer` is a token of the question's mode (`AnswerOutsideDomain` otherwise); its `support` is one of
W2's support kinds; the route recomputes the answer line from the evidence and rejects a record whose stated answer or
judgment the evidence does not establish (`AnswerMismatch`). A `judgment` is `follows` or `gap` only (`refuted` is not a
value: `InvalidInput: judgment`); `unresolved` is the absence of a record. A nomination names a candidate index of the
bound set at the bound version (`NominationOutsideSet`) and is recorded as a W2 narrowing with `support: testimony`
citing the question and the nomination unit; the checker never treats it as proof of intent. A compliance record names
either an asserted unit whose content is the act's `done` fact (norms.md 4.3: `done_click(Alice, Check)`, a base
predicate, with that unit's support kind), or, for a proof task, a certificate for exactly the pinned query.

### 3.4 Strict text (the fallback of P0 3.2)

```ebnf
legend     = "task ", token, "." | "you ", constant, "." | "the ", phrase, " is ", constant, "." ;
command    = "command ", name, ": ", ("require" | "forbid"), " (", ground-atom, ")", [ " if (", formula, ")" ], "." ;
question   = "question ", name, ": ", mode, "." ;
mode       = "polar (", formula, ")" | "which-all ", sort, " [", constant, { ", ", constant }, "] (", formula, ")"
           | "which-one ", sort, " [", constant, { ", ", constant }, "] (", formula, ")"
           | "follows ", query-id | "reading ", set-id, "@", version ;
```

The ground atom's arguments are the addressee constant then the bound constants in slot order (`@Alice click_required
@Check`); a which body uses `x0` for the alternative. `print(parse(s)) = s` on canonical text; English and strict forms
round-trip through the same objects with W1's preserved name metadata for rule names (norms.md 11.2).

### 3.5 Identity (`ve-document@2`)

`ve-document@2` is `ve-document@1` (document.md) plus: the `binding` kind, command and question content, `queries`,
`answers`, `compliance` and the `speech_acts` environment block. Its document identity is
`sha256("ve-document@2\n" + canonical(identity_payload))` with W2's payload (metadata without removable weights, source,
fences), so no `ve-document@1` identity moves and every `ve-document@1` document is a valid `ve-document@2` document with
the same units and, under the new domain string, a new document id. `environment_id` binds the `speech_acts` block beside
`regulated` (3.1). A command unit's `meaning_id` is `sha256("ve-meaning-<identity_version>\n" +
canonical({"environment_id", "ast"}))` with `ast` the command object; **a command whose act has a slot of sort
`query` (a proof task, 1.4) has, in its `ast`, beside the query constant, the query's regenerated premise meaning ids
and target meaning id**, so a proof task's meaning is bound to what it asks to be proved: retargeting `q1`, or changing
its premise set, while keeping the name `q1` changes the command's meaning id and stales its compliance certificate
(fixture ζ). A question's `meaning_id` is likewise over the question object including the derived mode, sort, domain,
body, query (with its premise meaning ids and target meaning id) and reading-set id and version; a binding's is over
the binding object. The objects are fixed JSON so that every checker digests the same bytes: a command is
`{"command": {"force", "act", "args", "guard"}}`, a proof task adding `"query": {"id", "premises": [<premise meaning
ids>], "target": <target meaning id>}` inside the command object; a question is `{"question": {"mode", ...}}` with
`body` (polar), `sort`, `domain` and `body` (which modes), `"query": {"id", "premises", "target"}` as above (follows),
or `set` and `version` (reading). The report identity is P0's
`{"environment_id", "document", "report"}` over the complete validated source document, `document` being the document
id above, recomputed from the identity payload that the decoded-source wrapper retains verbatim (`SpeechSource.metadata`,
`source`, `fences`, 8.5); every certificate in an answer,
compliance or consequence record is bound to the recomputed environment id, the regenerated premise list (1.5 or the
query's, 4.6) and the exact conclusion (`H(q) ∧ F(a)`, `F(a)` with `H(q)` as a premise, or the target); a replay against
a document whose scope block, regulated declaration, query premise set, active command set or asserted premise set
differs is stale. Removable weights and JSON layout are outside every identity, as in W2.

## 4. Semantics

### 4.1 Well-formedness (`WellFormedSpeech`)

A speech-act document `D` over `E` is well-formed when, in this order:

1. `E` enables exactly the allowlist `relational-fol@0`, `norms@0`, `speech-acts@0` among statement and checker
   profiles (1.6; any other profile, `soft-norms@0` included, is `UnsupportedProfile`); the `speech_acts` block
   decodes (3.1).
2. Every unit decodes under W2's rules with the kinds and contents of 3.2; spans partition the source; MIXED parts as W2.
3. Every command's act, role, args and guard type-check (3.2); every command has the addressee bound (`UnboundSlot: you`)
   and every definite phrase it uses bound (`UnboundSlot: <phrase>`); a command unit that fails this is rejected in
   authoring and is `unformalised(unbound-slot)` in translation, never active.
4. Every question's derived mode equals its stored mode; domains, sorts and bodies type-check; every `follows` question
   names a query whose premise ids are asserted units earlier in the document and whose target is closed and typed;
   every `reading` question names an existing set and version, has the meaning `{"open": ["intended-reading.<u>"]}`
   and the front matter declares that open term exactly as 4.6 derives it (both are derived content, 3.2).
5. `policy(D)` is W1 well-formed (norms.md 4.1) over `E`: the author norm units and the command rules together pass
   `Norms.WellFormed`, including both DAGs; a rule naming a command in `over` is `UnknownRule: rule cmd-<u>` (commands
   take no precedence and are taken precedence over by nothing at `@0`, 12.4); at most 256 rules in total.
6. Every answer, compliance and nomination record names an existing question or command of the right kind, a token of
   its mode, and evidence of a permitted kind (3.3).
7. Every authored binding agrees with the environment block or supplies a missing entry; two bindings of one phrase or
   of "you" are `DuplicateDeclaration: binding <phrase>`.

### 4.2 Command elaboration `demand(c)` and the regenerated policy

For a command `c` on the realising predicate `p` with sorts `(s₀, s₁, ..., sₖ)` (slot 0 the addressee), bound constants
`(you, a₁, ..., aₖ)` and guard `G_c`, in the predicate's context `[sₖ, ..., s₀]` (de Bruijn as norms.md 3.2: index 0 is
the last argument):

```text
eqGuard(c)   := (var k = @you) ∧ (var (k−1) = @a₁) ∧ ... ∧ (var 0 = @aₖ)         one equality per situation variable
demand(c)    := Node { name cmd-<u>, pred p, sign (force = require), guard eqGuard(c) ∧ G_c, carveOuts [], over [] }
```

This is exactly norms.md 3.3's "a rule about a constant writes `if (x0 equals @view)`", and W1's `ConsequenceArguments`
holds by construction: the consequence atom's arguments are the situation variables. `policy(D)` (1.2) is a `norms@0`
tree; W1's `elaborate`, `Value`, `holdsCatala`, conflict formulas, `ConflictFree`, `DocumentExpansion` and every route
theorem apply to it unchanged. The layer premise of `p` is regenerated at every site from the decoded active units and
the scope; a premise list on the wire is untrusted regression input for Rust only (norms.md 11.6).

### 4.3 The direct command semantics

Independently of the elaborator, a command means: *at the bound tuple, when its guard holds, the rule applies with its
sign; it applies nowhere else.* In W1's direct vocabulary (`AppliesD`, `Value`, `IntendedAt`):

```text
boundTuple(c, S)  := the tuple (you, a₁, ..., aₖ) denoted in S, in argument order (some tuple iff every constant denotes)
AppliesD (policy D).T S (tupleVal v̄) (demand c)   ⟺   boundTuple(c, S) = some v̄  ∧  S ⊨ G_c        (theorem demand_applies)
```

Hence, when the elaboration holds and no opposite-sign rule of the policy decides at that tuple, `p` holds there exactly
when the force is `require` (`demand_consequence`, 8.2): a `require` contributes `required_act(ā)` and a `forbid`
contributes `¬permitted_act(ā)`; and where an opposite rule also decides, the policy is a W1 CONFLICT at that tuple with
the witness situation, never a silent override. Defaults are W1's completions: a command never changes them; a
`require` on a deny-by-default obligation is what makes the act required at all.

### 4.4 Presuppositions, correctness and `Answers(Q, S)`

For a question `q` (1.3) and a structure `S` admissible for the complete environment:

```text
Answers(q, S) := { a ∈ tokens(q) | S ⊨ H(q) ∧ F(q, a) }
```

Facts about this set (theorems in 8.3): a polar question has at most one answer in `S`; a single-choice question has at
most one (from `H`); a complete-list question has exactly one, the subset of the domain that satisfies `P` in `S`, and
that subset may be empty. Where `S ⊭ H(q)`, `Answers(q, S) = ∅`: no token is correct, and in particular "no" is not.

### 4.5 Answer support: the proof path and the model path

Let `Π := premises(D)` (1.5) and `E_n` the complete environment.

```text
Supported(q, a)          := an accepted certificate  Π ⊢ H(q) ∧ F(q, a)                          (evidence kind: certificate)
SupportedGiven(q, a)     := an accepted certificate  Π ++ [H(q)] ⊢ F(q, a)                       (conditional; H(q) is a named
                            assumption in the residual, leaf speech:presupposition:<u>; the certificate supports the answer
                            conditional on that assumption and does not establish the presupposition)
PresuppositionFailed(q)  := an accepted certificate  Π ⊢ ¬H(q), or a validated finite model M of Π with M ⊭ H(q)
Evaluated(q, M)          := a validated finite model M of Π (Background validated, regulated tables computed as norms.md
                            11.3) with M ⊨ H(q): Answers(q, M) computed by the finite evaluator; evidence kind: model;
                            scope: that model only
UNKNOWN(q)               := none of the above within budget; the budget named
```

`Supported(q, a)` gives `a ∈ Answers(q, S)` in every admissible `S` satisfying `Π` (`support_sound`). Two opposite
polar answers (`support_exclusive`), or two distinct single-choice answers (`support_exclusive_one`), are both supported
only when `Π` is unsatisfiable; the report then shows the contradiction in the premises and marks every dependent
certificate `vacuous` (P0 3.8), as the debate protocol requires for coexisting `follows` and `refuted`. On the model
path, `M ⊭ H(q)` is reported as PRESUPPOSITION-FAILED and never as a negative answer; a countermodel to `Π ⇒ P` is
evidence about that model and establishes neither `Π ⇒ ¬P` nor "no" (`countermodel_not_negative`, whose second
conjunct needs a premise model satisfying `P`: over the premises `[¬P]` every premise model refutes `P`, and there "no"
is supported by certificate, not by the countermodel). Every answer line retains its assumptions (the certificate's used
leaves, including `speech:presupposition:<u>` when conditional), its evidence kind, P0's status of the premise list it
was checked over (a model, INCONSISTENT by certificate, or UNKNOWN within budget; 5.3) and the vacuity derived from that
status.

### 4.6 Consequence questions, proof tasks and reading questions

For a query `(B_q, P)` let `Π_q := Background(E) ++ elaborate(policy(D)) ++ B_q`.

```text
follows     := an accepted certificate  Π_q ⊢ P                                                 (Entails, by checkCertificate_sound)
gap         := a validated finite model M of Π_q with M ⊭ P                                     (¬Entails, by eval_iff_denote)
unresolved  := neither within budget; the budget named
```

Exactly these three; `refuted` (a certificate for `Π_q ⊢ ¬P`) is not imported: the plan forbids reading a countermodel
as `Π_q ⇒ ¬P`, and a document that wants the negation asks the polar question "Is it the case that not P?" whose "yes"
is that certificate. `follows` and `gap` for the same `(E, Π_q, P)` cannot both be sound (`follows_gap_exclusive`); the
implementation reports `CheckerConflict` and withholds a record, as debate-protocol.md prescribes.

A **proof task** is the command of 1.4; its compliance evidence is a replayed certificate for exactly `Π_q ⊢ P`, bound to
the query's meaning ids (which the command's own meaning id includes, 3.5). A submission whose premise list differs
from `Π_q` in any way, including adding `P`, is `QueryMismatch`. Acceptance establishes `Entails(E_n, Π_q, P)` and is
recorded **solely as compliance evidence** on the command's compliance line (5.4). It generates no premise and no graph
leaf: `done_submit(you, q)` is an independently interpreted base atom (norms.md 4.3) that no certificate entails, since a
model of every pinned premise may interpret it as false, and a usable `done` leaf would contradict `premises_core`
(8.4). The checker generates no `done` fact of any kind; acceptance establishes nothing about the submitter.

A **reading question** binds `(set, version)`. A nomination of candidate `i` by agent `g` is testimony: it records a
W2 narrowing (document.md, `ve/readings.py`: `set` and `version` the bound pair, `keeps` the one reading id of
candidate `i`, `by` the agent, `reason_spans` the question unit and the nomination unit; it never modifies the set), so
later checks can depend on the chosen reading under the label `readings:<set>@<version>:<i>` with the narrowing's
provenance visible; it is never proof of intent or of fidelity. No nomination, two nominations, or a nomination outside
the set leaves the status `CLARIFICATION-OPEN` and records nothing. The presupposition "exactly one intended reading"
is expressly non-formal (the set is not a domain of constants), so it is not a formula and cannot be a formalised
presupposition; it is a **W2 open term** (document.md) in W2's frozen schema (`ve/openterms.py`: the complete record,
token-valid names and arguments, closed-formula condition lists). Its `name` is the W2 token `intended-reading.<u>`,
`<u>` the reading question's unit id (W2 tokens are `[A-Za-z0-9_.-]` of at most 64 bytes, so `:` and `@` cannot occur
in a name, and a reading question whose unit id exceeds 47 bytes is `ResourceLimit: open-term name`); everywhere in
the report and the residual it is displayed under the label `intended-reading:<set>@<version>`, rendered from its
`arguments` and `version`. The declaration is derived content (3.2), regenerated from the question and compared, one
per reading question:

```json
{"name": "intended-reading.u6", "arguments": ["rs1"], "version": 2,
 "decided_by": "Alice", "jurisdiction": "t1",
 "necessary": [], "sufficient": [], "precedents": [],
 "factors": ["necessary: at least one nomination of a candidate of rs1 at version 2 by Alice",
             "sufficient: exactly one nomination of a candidate of rs1 at version 2 by Alice"]}
```

`arguments` is the bound set id (a W2 token); `version` is the bound version (W2 requires an integer of at least 1 of
an open term and of a reading set alike); `decided_by` is the addressee's constant name (mandatory here, since the
wording mentions "you": 1.1) and `jurisdiction` the scope's task token. `necessary` and `sufficient` are W2's
closed-formula lists and are **empty**: no closed formula over `E` expresses a nomination, because the candidates are
readings and not constants of a sort, which is exactly what "expressly non-formal" means; the nomination criteria are
therefore carried as `factors` text and enforced by the route's nomination-record rules (3.3), never by a formula, and
`precedents` is empty. The reading question's `meaning` names the term, `{"open": ["intended-reading.<u>"]}` (3.2), so
under W2's own status inference the unit is OPEN, the term is counted in the residual under W2's open-term count, and
the reading question's class is O (6).

### 4.7 Exact consequence correspondence and dormant-request invariance

The consequences of a speech-act document are **exactly** those of `premises(D)`: `Background(E)`, the regenerated
active W1 layers of `policy(D)` (the author's norm units and the elaborated active commands) and the fixed asserted
premises. Two things follow and are theorems (8.4):

- **No embedded proposition is a premise by occurrence.** `premises(D)` is a function of `E`, the scope, the validated
  regulated declarations, the active norm units, the active commands and the asserted units alone (`core`, 8.1); the
  body of a question, the proposition inside a command ("that the token is shared"), an answer record, a compliance
  record (an accepted proof-task certificate included, 4.6) and a binding unit contribute nothing. A supported answer
  may enter a later
  deduction only through the leaf `speech:answer:<u>:<a>`, admitted exactly when it equals `H(q) ∧ F(q, a)` for an answer
  supported by certificate over `premises(D)` (never for a model-evaluated answer), with the certificate's own leaves
  retained; that is the answer-to-claim bridge, and it states exactly what licenses it.
- **Ordinary composition is preserved.** From the admitted requirement `required_open(Alice, Desk1)` (a layer
  consequence) and the explicit asserted premise `required_open(Alice, Desk1) → reviewed(Atlas)`, the checker derives
  `reviewed(Atlas)`: W1's `norms_route_acceptance` on `policy(D)` is reused verbatim. Nothing in this route bars a
  document's own premises from mentioning regulated predicates.
- **Dormant-request invariance.** For two well-formed documents over the same environment (hence the same scope and
  declarations) with the same active norm units, the same active commands and the same asserted premises, `premises(D)`
  and `policy(D)` coincide, so every certificate replays identically, every countermodel is a countermodel of both and
  every conflict status agrees: adding, removing, quoting or answering a dormant unit changes no verdict. A change to the
  scope block or to a regulated declaration is a declaration change: a new `environment_id`, hence a new document under
  W2's rules, handled by identity, not by this invariance.

### 4.8 Scope: one pinned semantic scope per policy evaluation

W1's situation variables are exactly the act's arguments (norms.md 1) and carry no task coordinate, so nothing in a
regulated relation records which task a requirement belongs to. At `@0` the rule is therefore structural: `policy(D)` is
built from one document over one environment, every command rule is guarded by that environment's addressee constant,
and a policy evaluation never combines rules from documents with different `speech_acts` blocks. `combine(D₁, D₂)`, the
only way two documents' units reach one policy (a bundle or a multi-source check), returns `ScopeMismatch: <task₁>,
<task₂>` when the blocks differ, and the W3 citation rule already requires one environment identity across a bundle
(Definitions/STATEMENTS.md), which the block is part of. Consequently "Open the desk." in task A and "Do not open the
desk." in task B are never a CONFLICT: they are never in one relation. The same two sentences in one scope are a genuine
W1 pair conflict at `(Alice, Desk1)` with that witness. A scope-preserving encoding that would let differently scoped
demands share a relation (a task argument on the act) is a separately specified and verified profile, not `@0`.

## 5. The report: four separate lines per unit

### 5.1 Meaning admitted

Per unit: `admitted` (the object of 3.2 and its paraphrase), `repair: UnboundSlot <phrase>`, `readings: <set>@<v>,
<n> candidates` (each candidate's own line beneath), `unformalised(<reason>)`. A well-formed unanswered question is
`admitted` with the answer line `UNANSWERED`: checked semantics, no checked answer.

### 5.2 Norm outcome and conflict (commands)

The W1 report of `policy(D)` (norms.md 5.2): document status CONFLICT-FREE (certificates per target) / CONFLICT (witness
situation, rendered) / UNKNOWN (budget), and, per command, its demand in English ("In this task, Alice must click
Check.") and the outcome at its tuple under the exhibited premise-set model or by certificate (`premises(D) ⊢ p(ā)`).
A conflict involving a command names the command and the rule or command it collides with and the situation; a
command's demand is never silently overridden.

### 5.3 Answer evidence and its scope (questions)

```text
answer: supported <a> (certificate; assumptions: <leaves>;
                       premises: model <id> | INCONSISTENT (certificate) | UNKNOWN (<budget>); vacuous: no | yes | unknown)
      | supported <a> given the presupposition (certificate; assumption speech:presupposition:<u>;
                       premises with H: model <id> | INCONSISTENT (certificate) | UNKNOWN (<budget>); vacuous: no | yes | unknown)
      | evaluated <a> in model <id> (this situation only)
      | PRESUPPOSITION-FAILED (certificate for ¬H | model <id>)
      | UNKNOWN (<budget>)
      | UNANSWERED
judgment (follows questions): follows (certificate; premises: model <id> | INCONSISTENT (certificate) | UNKNOWN (<budget>))
                            | gap (model <id>) | unresolved (<budget>)
nomination (reading questions): <i> by <agent> (testimony) | CLARIFICATION-OPEN (none | multiple | outside set)
```

`premises` is P0's premise status (document.md: the premise set's model, its inconsistency certificate, or UNKNOWN
within the named budget) of the exact premise list the certificate was checked over: `Π` for an unconditional answer,
`Π ++ [H(q)]` for a conditional one (a false presupposition can make a conditional proof vacuous although `Π` is
consistent, so the conditional line carries the status of the extended list, never a copy of `Π`'s), and `Π_q` for a
`follows` judgment. `vacuous` is derived from that status and nothing else: `yes` under INCONSISTENT, `no` under a
model, `unknown` under UNKNOWN; the three-way status is never collapsed to a yes/no.

### 5.4 Compliance evidence (commands)

```text
compliance: none
          | external: unit <id> (<support kind>)          an asserted done_act(ā) unit with its own support
          | certificate: query <q>                        a proof task's replayed certificate (evidence on this line only:
                                                          no premise, no leaf, no generated done fact; 4.6)
```

Compliance is never inferred from the demand, from an answer, or from the passage of time; "external" repeats the
unit's support kind (observation, testimony, adapter, ...) and adds nothing. Physical completion requires external
evidence; "a clear explanation" is an open term with W2's decider, criteria and version, or `unformalised` if no adequate
contract exists.

### 5.5 Status text

```text
policy: CONFLICT-FREE (<k> certificates) | CONFLICT: <rule or command> against <rule or command> at <situation> | UNKNOWN (<budget>)
scope: task <task>; you = <constant>; <n> definite bindings; <m> commands active, <d> dormant
questions: <a> answered (<c> by certificate, <e> in a model), <p> presupposition failures, <u> unknown, <w> unanswered
compliance: <x> of <m> commands with evidence (<y> external, <z> certificates)
```

Residual lines beside W2's (open terms, named assumptions, bridge leaves, unresolved reading sets): `presuppositions`
(assumed, per question), `intended-reading` open terms (one per reading question, named `intended-reading.<u>` and
displayed `intended-reading:<set>@<v>`, under W2's open-term count),
`domain-closure` assumptions from rewrites, `unbound-slots`, `dormant-commands` (quoted, example, pending), `unanswered`,
`answer-bridges` (leaves `speech:answer:*` used).

## 6. Coverage projection C/L/O/R/U

W2 reports `bytes_by_kind` and `bytes_by_status` (CHECKED / OPEN / LABELLED / UNFORMALISED / MIXED parts). This route
adds a disjoint projection `bytes_by_class` over the same partition, totalling the source byte count, without rewriting
either W2 table. Each unit or MIXED part is first split by substance, then classed by precedence:

```text
non-substantive  := whitespace, punctuation and separators, list markers, headings and labels with no content
                    (W2 LABELLED), display numbers                                                   → L
substantive, in this order:
  U  any unbound slot; any unsupported component (temporal, coordination with order, ability, request, permission
     grant, open-domain which, pronoun, past-tense inversion); an active reading set with an unelaborated reading;
     unformalised(...)
  R  else an active open reading set whose every candidate is elaborated (each admitted as a command, question, norm
     or assertion), with each candidate's residual retained beneath it
  O  else a meaning `{"open": [...]}`, a question whose presupposition or a command whose guard is an open term, or a
     reading question (its meaning is `{"open": ["intended-reading.<u>"]}`, naming the open term of 4.6)
  C  else: admitted, every context slot bound, every presupposition formalised and either proved or retained as a named
     assumption in the residual; completion and answer truth are irrelevant to C
```

Failing C never by itself yields U: necessity versus duty ("Must Alice open the desk?") is R; "a clear explanation" is
O; "Which reading did you mean?" is O, because its expressly non-formal presupposition cannot meet C's formalisation
requirement and is carried by an open term with a decider and criteria in W2's frozen schema (4.6). Environment-declared
bindings and defaults are
the legend, outside the partition, no class. An authored `binding`
unit is substantive and C when it binds a declared phrase or "you" to a declared constant, U otherwise (a legend sentence
carrying a normative default or a factual assertion is never L). Reconciliation with W2: CHECKED ↦ C; OPEN ↦ R, O or U
by the rules above (W2 stores readings under OPEN; the class says which); LABELLED ↦ L; UNFORMALISED ↦ U; a MIXED unit
by its parts. Residual counts (5.5) accompany the table; per-reading residuals stay under R. Guessed deciders and opaque
action glosses earn no C: an action declaration cannot hide a sentence behind an opaque predicate and claim fidelity
(2.3, the `choose a mode` row declares the object inside the act only when that is the meaning).

## 7. Diagnostics (shared text in Python and Lean unless marked)

| Text | When | Kind |
|---|---|---|
| `UnsupportedProfile: speech-acts@0 requires norms@0` / `speech-acts@0 with <profile or declaration>` | profile gate: any profile outside the allowlist `relational-fol@0`, `norms@0`, `speech-acts@0` (`soft-norms@0`, `closure@0`, `order@0`, `nary@0`, ...), W3 definitions or W5 flags with the route (1.6) | error |
| `InvalidInput: speech_acts block` / `force` / `judgment` / `invalid command fields for <u>` / `invalid question fields for <u>` | field consistency (3.1 to 3.3), including a reading question whose `{"open": [...]}` meaning or open-term declaration differs from the derived form (4.6) | error |
| `UnknownSymbol: <constant>` / `UnknownSymbol: sort <s>` | undeclared addressee, definite constant, alternative or query constant | error |
| `UnboundSlot: you` / `UnboundSlot: <phrase>` | a command or "you"-mentioning unit without a binding (4.1(3)); English layer adds the legend rewrite | error (authoring) / `unformalised(unbound-slot)` (translation) |
| `BindingConflict: <phrase>` / `DuplicateDeclaration: binding <phrase>` | an authored binding disagrees with the block or repeats | error |
| `MissingObligationRole: <act>` / `MissingPermissionRole: <act>` | `require` on an act without an obligation role; `forbid` on an act without a permission role | error |
| `ModeMismatch: <u>` | stored mode differs from the wording-derived mode | error |
| `UnknownAlternative: <u>, <name>` / `DuplicateAlternative: <u>, <name>` / `AlternativeSort: <u>` | domain checks | error |
| `UnknownRule: rule cmd-<u>` | an author rule names a command in `over` | error (W1 text) |
| `ScopeMismatch: <task₁>, <task₂>` | combining documents with different `speech_acts` blocks (4.8) | error |
| `QueryMismatch: <u>` | a stored query or a submitted certificate's premise list differs from the regenerated `Π_q` | error |
| `AnswerOutsideDomain: <u>, <token>` / `AnswerMismatch: <u>` / `NominationOutsideSet: <u>` | answer records (3.3) | error |
| `TrivialQuery: <u>` | the target is an earlier asserted unit | warning |
| `CheckerConflict` | `follows` and `gap` artifacts for one `(E, Π_q, P)` (debate-protocol.md) | operational error |
| `ResourceLimit: rules` / `alternatives` / `definites` / `questions` / `open-term name` | W1's 256 rules including commands; more than 16 alternatives; 64 definites; 256 questions; a reading question's unit id over 47 bytes (W2's 64-byte token limit on `intended-reading.<u>`, 4.6) | error |
| `CoordinatedActs`, `PermissionNotCommand`, `ModalQuestion`, `OpenDomainWhich`, `TemporalWording` | English-layer hints with the rewrites of 2.3 (Python only) | hint |
| `Overlap(<n>, <m>)`, `DependencyCycle`, `PrecedenceAcrossPredicates`, `ConsequenceArguments`, ... | W1's, unchanged, on `policy(D)` | as W1 |

Order: the profile gate; the environment block; W1's declaration checks; units in document order (kind, content, slots,
mode, domain, query); `policy(D)` through W1's `check` (its diagnostics verbatim); queries; answer and compliance
records. English diagnostics carry the span and the plain-language expectation as today. Existing P0, W1 and W2
diagnostics are unchanged.

## 8. Lean (item 2): definitions and the exact statements to prove

Files: `lean/VE/SpeechActs/Tree.lean` (scope, commands, questions, queries, `WellFormedSpeech`), `Demand.lean`
(`eqGuard`, `demand`, `policy`, `premises`, the direct semantics and faithfulness), `Answer.lean` (`presupposition`,
`correct`, `tokens`, `AnswersAt`, support and model theorems), `Consequence.lean` (queries, `follows`/`gap`), `Wire.lean`,
`Admission.lean`, `Run.lean` (the `ve_speech_acts_route` executable) and `lean/SPEECH-ACTS.md` listing each theorem in
plain words. Frozen `Norms/*`, `Route/*` and all P0 sources are untouched; `VE.lean`, `VE/Audit.lean` and `lakefile.toml`
gain imports, audit entries and the new target only; the audit allowlist is unchanged and no theorem uses `sorry`. Names
below have prefix `VE.SpeechActs.`; W1 names are `VE.Norms.*` as in `lean/NORMS.md`. The blocks are statement schemata:
helper names are defined here, not already implemented Lean. Conventions are W1's: relation tuples in argument order,
`tupleVal` for valuations, `[]` for closed formulas, `E_n := envAt (policy D) (size (policy D))`.

### 8.1 Definitions

```lean
namespace VE.SpeechActs
open VE.Norms (Regulated Node Tree Doc WellFormed elaborate elabPremise Value IntendedAt holdsCatala tupleVal Sat
  background backgroundBase BaseAdmissible ConflictFree DocumentExpansion envAt size before pairs regulatedNames
  definitionsHold profileHold inst forget fuel AppliesD DecidesD AgreesBelow restrictAll)

inductive Force | require | forbid
  deriving DecidableEq                        -- `decide (c.force = .require)` in `demand` needs it
inductive Mode | polar | whichAll | whichOne | follows | reading
  deriving DecidableEq

structure Scope where
  task      : String
  addressee : Option (String × String)        -- (sort, constant)
  definites : List (String × String)          -- (phrase, constant), sorted by phrase

structure Command where
  unit  : String
  force : Force
  act   : String                              -- the realising regulated predicate
  args  : List String                         -- constants for the slots after slot 0
  guard : VE.Formula                          -- closed; .top when absent

structure Query where
  id         : String
  premiseIds : List String                    -- the pinned asserted unit ids (1.4), document order
  premises   : List VE.Formula                -- regenerated from the pinned unit ids, document order
  target     : VE.Formula

structure Question where
  unit       : String
  mode       : Mode
  body       : VE.Formula                     -- closed (polar); context [sort] (which modes); ignored otherwise
  sort       : Option String
  domain     : List String                    -- 2 to 16 distinct constants of `sort`, wording order
  query      : Option String
  readingSet : Option (String × Nat)

inductive Answer
  | yes | no
  | one (a : String)
  | all (S : List String)                     -- a sorted sublist of the domain

/-- The semantic core. The frozen `VE.Environment` (`lean/VE/Syntax.lean`) holds only sorts, predicate signatures and
    constants, so the validated regulated declarations (3.1: names, sorts, defaults, roles, acts, duals) are stored
    here explicitly, as W1's own decoder returns them; nothing recovers them from `E`. -/
structure SpeechDoc where
  E         : VE.Environment
  lits      : List String
  scope     : Scope
  regulated : List Regulated                  -- the validated `regulated` declarations of 3.1, W1's decoder output
  norms     : List Node                       -- active author norm units, document order
  commands  : List Command                    -- active commands, document order (1.2)
  questions : List Question
  queries   : List Query
  asserted  : List (String × VE.Formula)      -- W2's fixed asserted premises with their unit ids, document order

def regOf (D : SpeechDoc) (p : String) : Option Regulated := D.regulated.find? (fun r => r.name == p)
def actSorts (D : SpeechDoc) (c : Command) : List String                 -- E.predicates c.act
def addresseeConst (D : SpeechDoc) : Option String
/-- One equality per situation variable: slot i of n+1 slots is `var (n - i)`; slot 0 is the addressee (4.2). -/
def eqGuard (D : SpeechDoc) (c : Command) : VE.Formula
def demand (D : SpeechDoc) (c : Command) : Node :=
  { name := "cmd-" ++ c.unit, pred := c.act, sign := decide (c.force = .require),
    guard := .and (eqGuard D c) c.guard, carveOuts := [], over := [] }
def policy (D : SpeechDoc) : Doc :=
  ⟨D.E, D.lits, ⟨D.regulated, [], D.norms ++ D.commands.map (demand D)⟩⟩
def assertedFormulas (D : SpeechDoc) : List VE.Formula := D.asserted.map Prod.snd
def premises (D : SpeechDoc) : List VE.Formula :=
  background (policy D) ++ elaborate (policy D).T ++ assertedFormulas D
def En (D : SpeechDoc) : VE.Environment := envAt (policy D) (size (policy D))

/-- 4.1, executable, with the diagnostics of section 7; includes Norms.WellFormed (policy D). -/
def WellFormedSpeech (D : SpeechDoc) : Bool

/-- 4.3: the bound tuple of a command in a structure, argument order. -/
def boundTuple (D : SpeechDoc) (c : Command) (S : VE.Structure) : Option (List S.Carrier)

/-- 1.3: presupposition, tokens and correctness. -/
def presupposition (D : SpeechDoc) (q : Question) : VE.Formula          -- H(q); .top for polar, whichAll, follows
def tokens (D : SpeechDoc) (q : Question) : List Answer
def correct (D : SpeechDoc) (q : Question) : Answer → Option VE.Formula  -- F(q, a); none off the token list
def AnswersAt (D : SpeechDoc) (q : Question) (S : VE.Structure) (a : Answer) : Prop :=
  a ∈ tokens D q ∧ (presupposition D q).denote S [] ∧ ∃ φ, correct D q a = some φ ∧ φ.denote S []
/-- The finite evaluator's answer test (model path). -/
def answerEval {α} [DecidableEq α] (D : SpeechDoc) (q : Question) (M : VE.FiniteModel α) (a : Answer) : Bool

/-- 4.6 -/
def queryPremises (D : SpeechDoc) (qr : Query) : List VE.Formula :=
  background (policy D) ++ elaborate (policy D).T ++ qr.premises
/-- 1.4: the pinned premises regenerated from the asserted units named by the query, in document order. -/
def pinnedAsserted (D : SpeechDoc) (qr : Query) : List VE.Formula :=
  (D.asserted.filter (fun u => u.1 ∈ qr.premiseIds)).map Prod.snd
/-- 1.4: the target is itself one of the pinned premises (`TrivialQuery`, a warning; the task stands). -/
def trivialQuery (D : SpeechDoc) (qr : Query) : Bool := decide (qr.target ∈ pinnedAsserted D qr)

/-- 4.8: the only way two documents' units reach one policy. -/
def combine (D₁ D₂ : SpeechDoc) : Except String SpeechDoc

/-- The active-unit projection: what `premises` may depend on. -/
def core (D : SpeechDoc) :
    VE.Environment × List String × Scope × List Regulated × List Node × List Command × List (String × VE.Formula) :=
  (D.E, D.lits, D.scope, D.regulated, D.norms, D.commands, D.asserted)
```

`D.regulated` is what W1's environment decoder validated (3.1), carried with the core because `E` cannot supply it;
`answerEval` evaluates `H(q)` and `F(q, a)` with `Formula.eval` under `[]`. `tokens` for `whichAll` lists every sorted
sublist of the domain (at most 2¹⁶ tokens; the report enumerates only the answers present in records, never the token
list). The decoded-source wrapper that carries everything `SpeechDoc` omits (W2's identity payload of 3.5 verbatim,
that is the validated front matter without removable weights, the source bytes and the fences; every unit including
dormant and `binding` units; the open terms; the reading sets with their command, question, norm and assertion
candidates; the structured narrowings; the lemmas; the query records; the answer, compliance and nomination records;
the graph and the provenance) is `SpeechSource` in 8.5; `SpeechDoc` is its projection.

### 8.2 Theorems: commands

```lean
/-- 4.1 ⇒ W1 well-formedness of the regenerated policy. -/
theorem policy_wellFormed (D : SpeechDoc) (h : WellFormedSpeech D = true) : WellFormed (policy D) = true

/-- The shape of every command rule: consequence over the situation variables, equality guard, no carve-outs, no edges. -/
theorem demand_shape (D : SpeechDoc) (h : WellFormedSpeech D = true) (c : Command) (hc : c ∈ D.commands) :
  (demand D c).carveOuts = [] ∧ (demand D c).over = [] ∧ (demand D c).pred = c.act ∧
  ((demand D c).guard.WellFormed D.E (actSorts D c).reverse)

/-- Polarity: require realises the obligation role with sign +, forbid the permission role with sign −. -/
theorem demand_polarity (D : SpeechDoc) (h : WellFormedSpeech D = true) (c : Command) (hc : c ∈ D.commands) :
  (c.force = .require → (demand D c).sign = true  ∧ ∃ r, regOf D c.act = some r ∧ r.role = .obligation) ∧
  (c.force = .forbid  → (demand D c).sign = false ∧ ∃ r, regOf D c.act = some r ∧ r.role = .permission)

/-- 4.3, faithfulness of the elaborated guard to the direct reading: the rule applies exactly at the bound tuple when
    the guard holds. -/
theorem demand_applies (D : SpeechDoc) (h : WellFormedSpeech D = true) (c : Command) (hc : c ∈ D.commands)
    (S : VE.Structure) (hS : S.Admissible (En D)) (vs : List S.Carrier)
    (typed : VE.TupleTyped S (actSorts D c) vs) :
  AppliesD S (tupleVal vs) (demand D c) ↔ (boundTuple D c S = some vs ∧ c.guard.denote S [])
  -- W1's `AppliesD` takes `S ρ N` (Elaborate.lean); it has no tree argument

/-- The command's normative contribution: where the elaboration holds and no opposite rule decides at the bound tuple,
    the realising predicate holds there iff the force is require (required_act(ā), respectively ¬permitted_act(ā)). -/
theorem demand_consequence (D : SpeechDoc) (h : WellFormedSpeech D = true) (c : Command) (hc : c ∈ D.commands)
    (S : VE.Structure) (hS : S.Admissible (En D)) (hel : Sat S (elaborate (policy D).T))
    (vs : List S.Carrier) (typed : VE.TupleTyped S (actSorts D c) vs)
    (hb : boundTuple D c S = some vs) (hg : c.guard.denote S [])
    (hno : ¬ DecidesD (policy D).T S (tupleVal vs) c.act (!decide (c.force = .require))) :
  S.relation c.act vs ↔ c.force = .require

/-- Where an opposite rule does decide there, the local elaboration of `c.act` cannot hold in `S` (via
    `decides_forget` and `elaborate_iff_at`). This is the whole of what follows from `hop` alone. -/
theorem demand_conflict_local (D : SpeechDoc) (h : WellFormedSpeech D = true) (c : Command) (hc : c ∈ D.commands)
    (S : VE.Structure) (hS : S.Admissible (En D)) (vs : List S.Carrier) (typed : VE.TupleTyped S (actSorts D c) vs)
    (hb : boundTuple D c S = some vs) (hg : c.guard.denote S [])
    (hop : DecidesD (policy D).T S (tupleVal vs) c.act (!decide (c.force = .require))) :
  ¬ Sat S (elaborate (policy D).T)

/-- ... and, when `S` agrees with every layer below `c.act` (W1's `AgreesBelow`, the hypothesis of `conflict_denote`),
    the base policy is a W1 conflict at that tuple: never a silent override. Without `ha` the conclusion is false:
    with a guard over a lower regulated predicate (12.11), an `S` admissible over `En D` whose lower relations are
    arbitrary can satisfy `hop` while the regenerated `conflict_p°` is false at the base restriction. `ConstantsTyped`
    comes from `hS`; the `PrefixAdmissible` form is a corollary through `agreesBelow_of_meanings`. -/
theorem demand_conflict (D : SpeechDoc) (h : WellFormedSpeech D = true) (c : Command) (hc : c ∈ D.commands)
    (S : VE.Structure) (hS : S.Admissible (En D)) (vs : List S.Carrier) (typed : VE.TupleTyped S (actSorts D c) vs)
    (ha : AgreesBelow (policy D) (before (policy D) c.act) S)
    (hb : boundTuple D c S = some vs) (hg : c.guard.denote S [])
    (hop : DecidesD (policy D).T S (tupleVal vs) c.act (!decide (c.force = .require))) :
  ¬ ConflictFree (policy D) (restrictAll (policy D).T S)

/-- Every command rule is guarded by the one addressee of the scope. -/
theorem scope_single (D : SpeechDoc) (h : WellFormedSpeech D = true) (c : Command) (hc : c ∈ D.commands) :
  ∃ you, addresseeConst D = some you ∧ VE.Norms.preds (eqGuard D c) = [] ∧
    (∀ S : VE.Structure, ∀ vs, boundTuple D c S = some vs → vs.head? = S.constant you)
```

### 8.3 Theorems: questions and answers

```lean
/-- 4.4: at most one polar answer; at most one single-choice answer; exactly one complete-list answer; none when H fails. -/
theorem answers_polar (D : SpeechDoc) (h : WellFormedSpeech D = true) (q : Question) (hq : q ∈ D.questions)
    (hm : q.mode = .polar) (S : VE.Structure) : ¬ (AnswersAt D q S .yes ∧ AnswersAt D q S .no)
theorem answers_one (D : SpeechDoc) (h : WellFormedSpeech D = true) (q : Question) (hq : q ∈ D.questions)
    (hm : q.mode = .whichOne) (S : VE.Structure) (a b : String) :
  AnswersAt D q S (.one a) → AnswersAt D q S (.one b) → a = b
theorem answers_all (D : SpeechDoc) (h : WellFormedSpeech D = true) (q : Question) (hq : q ∈ D.questions)
    (hm : q.mode = .whichAll) (S : VE.Structure) (hS : S.Admissible (En D)) :
  ∃ T : List String, AnswersAt D q S (.all T) ∧ ∀ T₂ : List String, AnswersAt D q S (.all T₂) → T₂ = T
theorem answers_all_empty (D : SpeechDoc) (h : WellFormedSpeech D = true) (q : Question) (hq : q ∈ D.questions)
    (hm : q.mode = .whichAll) (S : VE.Structure) (hS : S.Admissible (En D))
    (hnone : ∀ a ∈ q.domain, ¬ (inst [.const a] q.body).denote S []) : AnswersAt D q S (.all [])
  -- W1's `inst : List VE.Term → VE.Formula → VE.Formula` (Basic.lean): the substitution comes first
theorem answers_presupposition (D : SpeechDoc) (h : WellFormedSpeech D = true) (q : Question) (hq : q ∈ D.questions)
    (S : VE.Structure) (hH : ¬ (presupposition D q).denote S []) : ∀ a : Answer, ¬ AnswersAt D q S a

/-- 4.5, proof path. -/
theorem support_sound (D : SpeechDoc) (h : WellFormedSpeech D = true) (q : Question) (hq : q ∈ D.questions)
    (a : Answer) (φ : VE.Formula) (hφ : correct D q a = some φ) (c : VE.Tableau.Certificate)
    (acc : VE.Tableau.checkCertificate (En D) (premises D) (.and (presupposition D q) φ) c = true) :
  ∀ S : VE.Structure, S.Admissible (En D) → Sat S (premises D) → AnswersAt D q S a
theorem support_conditional_sound (D : SpeechDoc) (h : WellFormedSpeech D = true) (q : Question)
    (hq : q ∈ D.questions) (a : Answer) (φ : VE.Formula) (hφ : correct D q a = some φ) (c : VE.Tableau.Certificate)
    (acc : VE.Tableau.checkCertificate (En D) (premises D ++ [presupposition D q]) φ c = true) :
  ∀ S : VE.Structure, S.Admissible (En D) → Sat S (premises D) → (presupposition D q).denote S [] → AnswersAt D q S a
/-- Opposite polar answers are both supported only over unsatisfiable premises. -/
theorem support_exclusive (D : SpeechDoc) (h : WellFormedSpeech D = true) (q : Question) (hq : q ∈ D.questions)
    (hm : q.mode = .polar) (cy cn : VE.Tableau.Certificate)
    (hy : VE.Tableau.checkCertificate (En D) (premises D) (.and (presupposition D q) q.body) cy = true)
    (hn : VE.Tableau.checkCertificate (En D) (premises D) (.and (presupposition D q) (.not q.body)) cn = true) :
  ¬ ∃ S : VE.Structure, S.Admissible (En D) ∧ Sat S (premises D)
/-- Two distinct single-choice answers are both supported only over unsatisfiable premises (4.5's second clause). -/
theorem support_exclusive_one (D : SpeechDoc) (h : WellFormedSpeech D = true) (q : Question) (hq : q ∈ D.questions)
    (hm : q.mode = .whichOne) (a b : String) (hab : a ≠ b) (φa φb : VE.Formula)
    (hφa : correct D q (.one a) = some φa) (hφb : correct D q (.one b) = some φb) (ca cb : VE.Tableau.Certificate)
    (ha : VE.Tableau.checkCertificate (En D) (premises D) (.and (presupposition D q) φa) ca = true)
    (hb : VE.Tableau.checkCertificate (En D) (premises D) (.and (presupposition D q) φb) cb = true) :
  ¬ ∃ S : VE.Structure, S.Admissible (En D) ∧ Sat S (premises D)

/-- 4.5, model path: the evaluator's answers are exactly AnswersAt in that model; a failed presupposition yields none. -/
theorem model_answers {α : Type} [DecidableEq α] (D : SpeechDoc) (h : WellFormedSpeech D = true) (q : Question)
    (hq : q ∈ D.questions) (M : VE.FiniteModel α) (valid : M.Valid (En D))
    (hb : VE.Norms.backgroundValid (policy D) M = true) (hp : (premises D).all (fun φ => φ.eval M []) = true)
    (a : Answer) : answerEval D q M a = true ↔ AnswersAt D q M.asStructure a
theorem model_presupposition_failed {α : Type} [DecidableEq α] (D : SpeechDoc) (h : WellFormedSpeech D = true)
    (q : Question) (hq : q ∈ D.questions) (M : VE.FiniteModel α)
    (hH : (presupposition D q).eval M [] = false) : ∀ a : Answer, answerEval D q M a = false
/-- A countermodel to P is evidence about that model only: it does not give ¬P over the premises. The second conjunct
    needs the hypothesis that some admissible model of the premises satisfies `q.body`: over the premises `[¬P]` a
    countermodel to `P` exists and every premise model satisfies `¬P`, so without `S'` the conjunct is false
    (fixture η's regression). -/
theorem countermodel_not_negative {α : Type} [DecidableEq α] (D : SpeechDoc) (h : WellFormedSpeech D = true)
    (q : Question) (hq : q ∈ D.questions) (hm : q.mode = .polar) (M : VE.FiniteModel α)
    (valid : M.Valid (En D)) (hp : (premises D).all (fun φ => φ.eval M []) = true) (hn : q.body.eval M [] = false)
    (S' : VE.Structure) (hS' : S'.Admissible (En D)) (hp' : Sat S' (premises D)) (hb' : q.body.denote S' []) :
  AnswersAt D q M.asStructure .no ∧ ¬ (∀ S : VE.Structure, S.Admissible (En D) → Sat S (premises D) → AnswersAt D q S .no)
```

### 8.4 Theorems: consequence questions, correspondence, invariance, scope

```lean
/-- 4.6 -/
theorem follows_sound (D : SpeechDoc) (h : WellFormedSpeech D = true) (qr : Query) (hq : qr ∈ D.queries)
    (c : VE.Tableau.Certificate)
    (acc : VE.Tableau.checkCertificate (En D) (queryPremises D qr) qr.target c = true) :
  VE.Entails (En D) (queryPremises D qr) qr.target
theorem gap_sound {α : Type} [DecidableEq α] (D : SpeechDoc) (h : WellFormedSpeech D = true) (qr : Query)
    (hq : qr ∈ D.queries) (M : VE.FiniteModel α) (valid : M.Valid (En D))
    (hb : VE.Norms.backgroundValid (policy D) M = true)
    (hs : (queryPremises D qr).all (fun φ => φ.eval M []) = true) (hn : qr.target.eval M [] = false) :
  ¬ VE.Entails (En D) (queryPremises D qr) qr.target
theorem follows_gap_exclusive {α : Type} [DecidableEq α] (D : SpeechDoc) (h : WellFormedSpeech D = true)
    (qr : Query) (hq : qr ∈ D.queries) (c : VE.Tableau.Certificate)
    (acc : VE.Tableau.checkCertificate (En D) (queryPremises D qr) qr.target c = true)
    (M : VE.FiniteModel α) (valid : M.Valid (En D)) (hb : VE.Norms.backgroundValid (policy D) M = true)
    (hs : (queryPremises D qr).all (fun φ => φ.eval M []) = true) (hn : qr.target.eval M [] = false) : False
/-- The target never enters its own premise list through the query (`pinnedAsserted`, `trivialQuery`: 8.1). -/
theorem query_target_separate (D : SpeechDoc) (h : WellFormedSpeech D = true) (qr : Query) (hq : qr ∈ D.queries) :
  qr.premises = pinnedAsserted D qr ∧ (qr.target ∈ qr.premises → trivialQuery D qr = true)

/-- 4.7: premises depend only on the active core; questions, answers, compliance and dormant units contribute nothing. -/
theorem premises_core (D D₂ : SpeechDoc) (h : WellFormedSpeech D = true) (h₂ : WellFormedSpeech D₂ = true)
    (hc : core D = core D₂) : premises D = premises D₂ ∧ policy D = policy D₂
theorem questions_no_premises (D : SpeechDoc) (h : WellFormedSpeech D = true) (q : Question) (hq : q ∈ D.questions) :
  premises D = premises { D with questions := D.questions.erase q }
/-- Dormant-request invariance as verdict invariance: the same certificates replay and the same models refute. -/
theorem dormant_invariance (D D₂ : SpeechDoc) (h : WellFormedSpeech D = true) (h₂ : WellFormedSpeech D₂ = true)
    (hc : core D = core D₂) (Γ : List VE.Formula) (φ : VE.Formula) (c : VE.Tableau.Certificate) :
  (VE.Tableau.checkCertificate (En D) (premises D ++ Γ) φ c = VE.Tableau.checkCertificate (En D₂) (premises D₂ ++ Γ) φ c) ∧
  (∀ B : VE.Structure, BaseAdmissible (policy D) B → (ConflictFree (policy D) B ↔ ConflictFree (policy D₂) B))
/-- Ordinary composition preserved: W1's route acceptance on the regenerated policy, verbatim. `norms_route_acceptance`
    (Layer.lean:261) has exactly the binders `D h hc Γ φ c accepted`; the well-formedness of `Γ` and `φ` over
    `envAt D 0` is a hypothesis of its second conjunct, not a binder. -/
theorem speech_route_acceptance (D : SpeechDoc) (h : WellFormedSpeech D = true)
    (hc : ∀ B : VE.Structure, BaseAdmissible (policy D) B → ConflictFree (policy D) B)
    (Γ : List VE.Formula) (φ : VE.Formula) (c : VE.Tableau.Certificate)
    (acc : VE.Tableau.checkCertificate (En D) (background (policy D) ++ elaborate (policy D).T ++ Γ) φ c = true) :
  (∀ S : VE.Structure, S.Admissible (En D) → holdsCatala (policy D).T S → definitionsHold (policy D) S →
     profileHold (policy D) S → Sat S (backgroundBase (policy D)) → Sat S Γ → φ.denote S []) ∧
  ((∀ a ∈ Γ, a.WellFormed (envAt (policy D) 0) []) → φ.WellFormed (envAt (policy D) 0) [] →
     ∀ B : VE.Structure, BaseAdmissible (policy D) B → Sat B Γ → φ.denote B []) :=
  VE.Norms.norms_route_acceptance (policy D) (policy_wellFormed D h) hc Γ φ c acc
/-- The answer-to-claim bridge licenses exactly H ∧ F of a certificate-supported answer. -/
theorem answer_bridge_sound (D : SpeechDoc) (h : WellFormedSpeech D = true) (q : Question) (hq : q ∈ D.questions)
    (a : Answer) (φ : VE.Formula) (hφ : correct D q a = some φ) (c : VE.Tableau.Certificate)
    (acc : VE.Tableau.checkCertificate (En D) (premises D) (.and (presupposition D q) φ) c = true)
    (S : VE.Structure) (hS : S.Admissible (En D)) (hp : Sat S (premises D)) :
  (.and (presupposition D q) φ).denote S []

/-- 4.8 -/
theorem combine_scope (D₁ D₂ D : SpeechDoc) (h : combine D₁ D₂ = .ok D) :
  D₁.scope = D₂.scope ∧ D₁.E = D₂.E ∧ D.commands = D₁.commands ++ D₂.commands
theorem two_task_separation (D₁ D₂ : SpeechDoc) (hs : D₁.scope ≠ D₂.scope) :
  combine D₁ D₂ = .error ("ScopeMismatch: " ++ D₁.scope.task ++ ", " ++ D₂.scope.task)
/-- No policy contains rules of two scopes: every rule of policy D is an author unit of D or a demand of D's commands. -/
theorem policy_rules (D : SpeechDoc) (h : WellFormedSpeech D = true) (N : Node) (hN : N ∈ (policy D).T.nodes) :
  N ∈ D.norms ∨ ∃ c ∈ D.commands, N = demand D c
```

### 8.5 Theorems: wire and report

```lean
/-- The decoded source (Wire.lean): the complete validated `ve-document@2` payload, kept for identity, admission and
    report regeneration; `SpeechDoc` (8.1) is its projection and discards nothing that identity or regeneration needs
    because this wrapper keeps it. W2's identity payload (3.5) is retained verbatim in `metadata`, `source` and
    `fences`; every other field is decoded from it. The frozen P0 `ReadingSet` (`Route/Admission.lean`, formula-only)
    and P0's open-term name and narrowing id lists appear only in the P0 projection `SpeechAdmitted.p0`, never here. -/
structure SpeechUnit where
  id       : String
  span     : Nat × Nat
  kind     : SpeechKind                       -- W2's kinds (P0 `Kind`) plus `binding`
  meaning  : Json                             -- specified | contextual | open | unformalised(<reason>)
  support  : String
  content  : SpeechContent                    -- command | question | binding | norm | assertion | none
  active   : Bool                             -- 1.2 for commands; active author norm or fixed assertion otherwise
/-- A W2 open term in the frozen schema (document.md; `ve/openterms.py`): the conditions are closed formulas over `E`;
    the `intended-reading.<u>` terms of 4.6 are among these. -/
structure OpenTerm where
  name         : String                       -- a W2 token
  arguments    : List String                  -- distinct W2 tokens
  decidedBy    : String
  jurisdiction : String
  version      : Nat                          -- at least 1
  necessary    : List VE.Formula              -- closed
  sufficient   : List VE.Formula              -- closed
  factors      : List String
  precedents   : List String                  -- pinned meaning ids
/-- A W2 reading candidate (document.md; `ve/readings.py`) with its structured content: a command, question, norm or
    assertion candidate is retained as such, `none` while its elaboration is pending. -/
structure SpeechReading where
  id             : String
  kind           : SpeechKind
  meaningId      : String
  content        : Option SpeechContent
  who            : String                     -- admission.who
  why            : String                     -- admission.why
  distinguishing : List (String × String)     -- admission.distinguishing_models: other reading id ↦ model id
inductive ReadingStatus | authored | pending  -- W2 `authored` | `open`
structure SpeechReadingSet where
  id              : String
  unit            : String                    -- the source unit
  version         : Nat                       -- at least 1
  status          : ReadingStatus
  signature       : Option String             -- authored sets only
  readings        : List SpeechReading        -- 1 to 64, source order (the index of `readings:<set>@<v>:<i>`)
  models          : List (String × Json)      -- the distinguishing finite models by id; W2's optional `models`, `[]`
                                              -- whether omitted or `{}` (its presence is in `metadata`, `source_retained`)
  rejectedHistory : Json                      -- W2's optional `rejected_history`, `[]` when omitted, likewise
/-- A W2 narrowing (document.md; `ve/readings.py`): the kept readings by id and the cited reason units; it never
    modifies the set. A recorded nomination (4.6) is one of these. -/
structure Narrowing where
  id          : String
  setId       : String
  version     : Nat
  keeps       : List String                   -- reading ids of that set version, nonempty
  author      : String                        -- W2 `by`
  reasonSpans : List String                   -- unit ids, nonempty
structure SpeechSource where
  metadata    : Json                          -- the validated front matter without removable `weights` (3.5)
  source      : String                        -- the prose source bytes (UTF-8, `ve` fences excluded), the span domain
  fences      : List (String × String)        -- unit id ↦ `ve` fence text
  E           : VE.Environment
  canonical   : Json                          -- the canonical environment bytes (3.1), the input of `environment_id`
  scope       : Scope
  regulated   : List Regulated
  lits        : List String
  units       : List SpeechUnit               -- every unit, active or dormant, document order
  openTerms   : List OpenTerm                 -- every declared open term, the `intended-reading.<u>` terms included
  readingSets : List SpeechReadingSet         -- every version of every set, candidates retained with their structure
  narrowings  : List Narrowing                -- every narrowing, recorded nominations included
  lemmas      : List VE.Route.Admission.Lemma
  queries     : List Query                    -- the derived query records (3.2), regenerated and compared
  answers     : List AnswerRecord             -- 3.3
  compliance  : List ComplianceRecord         -- 3.3
  nominations : List NominationRecord         -- 3.3
  graphJson   : Json
  provenance  : Json
/-- 3.5: W2's identity payload and the `ve-document@2` document id, from the retained payload and nothing else. -/
def SpeechSource.identityPayload (src : SpeechSource) : Json :=
  Json.mkObj [("metadata", src.metadata), ("source", .str src.source), ("fences", Wire.encodeFences src.fences)]
def SpeechSource.documentId (src : SpeechSource) : Except String String :=
  VE.CertificateWire.digest "ve-document@2\n" src.identityPayload
/-- The projection to the semantic core: the active commands, active norm units, questions, queries and fixed
    asserted units of `src`. -/
def SpeechSource.toDoc (src : SpeechSource) : SpeechDoc

/-- The admission wrapper, the shape of `Norms.Admission.Admitted`: the decoded source, its projection, the P0 document
    actually sent to `admit_document` (W2's projection of the source: every source unit except `binding` units (3.2), a
    unit under an active reading set without its content, only the active assertion-only reading sets and those as
    P0's formula-only `ReadingSet`, the open-term names, the narrowing ids, the lemmas and the graph), the graph, the
    report, the kinds and the classes (6). -/
structure SpeechAdmitted where
  src     : SpeechSource
  D       : SpeechDoc                         -- = src.toDoc
  p0      : VE.Route.Admission.Doc
  graph   : VE.Graph.ClaimGraph VE.Tableau.Certificate
  report  : VE.Graph.Report
  kinds   : List Json
  classes : List Json

/-- The scope is in the canonical environment bytes (3.5). -/
theorem scope_in_identity (j : Json) (E : VE.Environment) (sc : Scope) (rs : List Regulated)
    (h : Wire.decodeSpeechEnvironment j = .ok (E, sc, rs)) :
  ∃ b : Json, (Wire.canonicalEnvironmentJson j).toOption = some b ∧
    b.getObjVal? "speech_acts" = .ok (Wire.encodeScope sc)

/-- The wrapper is lossless on what identity and regeneration need. W2's identity payload is retained verbatim, so the
    document id of 3.5 is recomputable from `src` alone; `reading_sets` and `narrowings` are front-matter fields, so
    that payload (`src.metadata`, every front-matter key but `weights`) retains them byte for byte, W2's optional
    fields with their presence (a singleton reading's `models` omitted or written `{}`). The structured records are
    exactly the decoding of those retained fields: every version of every set with its command and question candidates
    and every narrowing, no projection. Nothing structured is re-encoded for identity: `SpeechReadingSet` normalises
    W2's optional fields (both spellings of an absent `models` decode to `[]`), so it is not a source of bytes.
    `Wire.identityPayload`, `Wire.readingSetsJson` and `Wire.narrowingsJson` read the corresponding front-matter fields
    of `j`, the last two `[]` when the field is omitted, as W2 reads them; `Wire.decodeReadingSets` and
    `Wire.decodeNarrowings` are the decoders `decodeSpeechSource` applies to those fields (W2's `validate_reading_sets`
    and `validate_narrowings` over the environment, the unit ids and the sets). -/
theorem source_retained (j : Json) (src : SpeechSource) (h : Wire.decodeSpeechSource j = .ok src) :
  Wire.identityPayload j = .ok src.identityPayload ∧
  (∃ r : Json, Wire.readingSetsJson j = .ok r ∧ Wire.decodeReadingSets src.E src.units r = .ok src.readingSets) ∧
  (∃ n : Json, Wire.narrowingsJson j = .ok n ∧ Wire.decodeNarrowings src.units src.readingSets n = .ok src.narrowings)

/-- Which units are active: exactly kind `instruction`, specified meaning, command content, bound slots, no pending
    reading set (1.2). -/
theorem active_commands (j : Json) (src : SpeechSource) (h : Wire.decodeSpeechSource j = .ok src) (c : Command) :
  c ∈ src.toDoc.commands ↔ ∃ u ∈ src.units, ActiveInstructionUnit src u c

/-- `binding` units never reach P0 `admit_document` (its frozen kind decoder has no `binding`, 3.2): each is withheld
    as W2 withholds unsupported readings, is bound by the wrapper's report identity and is classed by the coverage
    projection; every other unit reaches P0 as W2 sends it. -/
theorem bindings_withheld (adm : SpeechAdmitted) (h : Admission.admitSpeech adm.src = .ok adm) :
  (∀ u ∈ adm.src.units, u.kind = .binding →
     (∀ p ∈ adm.p0.units, p.id ≠ u.id) ∧ u.id ∈ Admission.identityUnits adm ∧ u.id ∈ Admission.classedUnits adm) ∧
  (∀ u ∈ adm.src.units, u.kind ≠ .binding → ∃ p ∈ adm.p0.units, p.id = u.id)

/-- 11.4-shaped acceptance from the public entry point, over the wrapper. -/
theorem speech_wire_acceptance (j a : Json) (h : Run.runCase j = .ok a)
    (hk : VE.Route.Run.caseKind j = .ok "admission") (hs : Run.usesSpeechPath j = true) :
  ∃ (src : SpeechSource) (adm : SpeechAdmitted),
    Wire.decodeSpeechSource j = .ok src ∧ adm.src = src ∧ adm.D = src.toDoc ∧ WellFormedSpeech adm.D = true ∧
    a = encodeAdmitted (regeneratedAdmission adm) ∧
    BindingsMatchSourceAndRegeneration j adm a ∧ Admission.ReportAdmitted adm a ∧
    (∀ S : VE.Structure, S.Admissible (En adm.D) → Sat S (premises adm.D) → Sat S (reportOtherAssumptions adm a) →
       (reportConclusion adm a).denote S []) ∧
    (∀ line ∈ answerLines a, AnswerEvidence adm line ∧ PremiseStatusEvidence adm line) ∧
    (∀ line ∈ complianceLines a, ComplianceEvidence adm line) ∧
    (∀ line ∈ judgmentLines a, JudgmentEvidence adm line ∧ PremiseStatusEvidence adm line)
```

`ReportAdmitted` is the norms extension of P0's admission relation (`Norms.Admission.admitDocument_spec`) over the
P0 document `adm.p0` (binding units withheld), whose report id is the digest of 3.5 over `{"environment_id",
"document": adm.src.documentId, "report"}`, with exactly two route-local leaves: `speech:presupposition:<u>` (equal
to `presupposition D q`) and `speech:answer:<u>:<a>` (equal to `H ∧ F` of a certificate-supported answer over
`premises D`, with that certificate's leaves retained), each admitted only when equal to the regenerated formula.
There is **no** `speech:compliance:<u>` leaf and no leaf over a `done` atom that the checker generates: an accepted
proof-task certificate is evidence on the compliance line only (4.6), and a graph leaf claiming `done_submit(you, q)`
from it is rejected. `AnswerEvidence adm line` says: `supported` carries an accepted certificate for `H ∧ F` over
`premises D`; `supported given` carries one over `premises D ++ [H]` and lists the presupposition leaf; `evaluated`
carries a validated model of `premises D` with `H` true in which `answerEval` is true; `PRESUPPOSITION-FAILED` carries a
certificate for `¬H` or a validated model with `H` false; `UNKNOWN` and `UNANSWERED` carry nothing and claim nothing.
`PremiseStatusEvidence adm line` says the line's `premises` field (5.3) is P0's premise status of exactly the list the
line's certificate was checked over (`premises D`, `premises D ++ [H]` or `queryPremises D qr`): a validated model of
it, an accepted inconsistency certificate for it, or UNKNOWN with the budget, and `vacuous` is the fixed function of
that status. `JudgmentEvidence` is `follows_sound`'s or `gap_sound`'s hypothesis; `ComplianceEvidence` is an asserted
`done` unit with its support kind or an accepted certificate for exactly `queryPremises D qr ⊢ qr.target`, and in
the second case no premise, leaf or `done` fact accompanies it. Hash equality is equality of recomputed canonical
digests, not a claim that SHA-256 is injective.

### 8.6 The executable `ve_speech_acts_route`

`lean/.lake/build/bin/ve_speech_acts_route <cases.json>`, root `SpeechActsMain.lean`, a new Lake target; `Run.main` is
the executable root and no frozen file changes (norms.md 11.4). On raw input it runs the frozen envelope and profile
gate, requires `speech-acts@0` and `norms@0`, decodes the environment through the W1 norms decoder plus a strict scope
decoder (unknown fields rejected; the original complete environment hashed), decodes units, queries, answers and
compliance, runs `WellFormedSpeech`, regenerates `policy(D)`, `premises(D)`, every `H(q)`, `F(q, a)` and `Π_q`, validates
bindings and delegates every checker call to the unchanged W1 and P0 functions on the regenerated data.

| Kind | Extra input | Output |
|---|---|---|
| `speech-elaborate` | none | `scope`, `legend` (sentences), `policy` (W1 `norms-elaborate` output on `policy(D)`), per command `demand` (rule AST, paraphrase), per question `mode`, `presupposition`, `tokens` (polar, single) or `domain`, per query `premises`, `target` |
| `speech-answer` | `question`, `evidence` (`certificate` / `model` / `conditional`) | the answer line of 5.3 |
| `speech-consequence` | `query`, `certificate` or `model` | `follows` / `gap` / `unresolved` with detail |
| `speech-conflict` | W1 packages or witness on `policy(D)` | W1's verdict |
| `admission` | W2 `ve-document@2` with commands, questions, bindings, records and graph (bindings withheld from P0 `admit_document` and carried by the wrapper, 3.2) | `admitted`, `report`, `report_id`, `kinds`, `classes` (6), the status text of 5.5 |

W1 and P0 cases without speech constructs delegate unchanged to `Norms.Run.runCase`; malformed speech inputs never fall
back after a failed speech decode.

### 8.7 What is not claimed

No theorem about the English surface (plan item 3) or about an author's intent: `demand`, `presupposition` and `correct`
are the statements under this review and W8's fidelity gate. No theorem that a nomination reflects intent, that a
`done` unit is true, or that an accepted proof shows understanding; no checker-generated `done` fact of any kind (4.6).
No `refuted` judgment. No completeness of the answer
search or of the conflict check beyond norms.md 7 on `policy(D)`. No adoption of quoted commands (12.8). No claim about
combinations 1.6 excludes. No coverage number: section 6 defines a projection, not a result.

## 9. Acceptance fixtures for item 1

Deterministic, hand-written expected results; required from Python and, where the Lean route has a case kind, from Lean
(`tests/test_speech_acts*.py`, the `speech-acts` conformance family). Unless a fixture says otherwise, the environment
is F0: sorts `user`, `control`, `token`, `desk`, `service`, `thing`, `query`; constants `Alice : user`, `Check : control`,
`Token1 : token`, `Desk1 : desk`, `Atlas Beacon : service`, `Tom : thing`, `q1 : query`; base predicates
`reviewed(service)` "{0} is reviewed", `cat(thing)` "{0} is a cat", `animal(thing)` "{0} is an animal",
`disabled(control)` "{0} is disabled", `done_click(user, control)`, `done_open(user, desk)`, `done_submit(user, query)`;
regulated as in 3.1 plus `open_required`/`open_permitted(user, desk)` (obligation deny, permission allow, act
`{0} open {1}`); scope task `t1`, addressee `Alice`, definites `the token ↦ Token1`, `the desk ↦ Desk1`,
`the writing desk ↦ Desk1`. `Γ` is empty; "the premises" are the document's asserted units.

- **(α) Click Check.** Active command `u1`. `demand` is `rule cmd-u1: for every user x0, for every control x1,
  (x0 click_required x1) if ((x0 equals @Alice) and (x1 equals @Check)).`; `premises(D)` entails
  `click_required(Alice, Check)` by certificate; a countermodel to `done_click(Alice, Check)` exists and the report's
  compliance line is `none`; the paraphrase reads "In this task, you must click Check." with the default legend "By
  default, a user need not click a control."; policy CONFLICT-FREE. Python and Lean `speech-elaborate` agree byte for byte.
- **(β) Prohibition versus optionality.** `Do not share the token.` → `¬share_permitted(Alice, Token1)`, sign `−` on the
  permission predicate; `premises(D)` entails `¬share_permitted(Alice, Token1)` and entails nothing about
  `share_required` (no such predicate). A wire object with `force: forbid` and `act: share_required` (declared as an
  obligation-only act `{0} share {1}` in a variant environment): `MissingPermissionRole: {0} share {1}`; never
  `¬share_required`. `force: permit`: `InvalidInput: force`.
- **(γ) Two tasks.** Document A (task `ta`): `Open the desk.`; document B (task `tb`, same declarations): `Do not open the
  desk.`. `environment_id(A) ≠ environment_id(B)`; `combine(A, B)` is `ScopeMismatch: ta, tb`; neither document is a
  CONFLICT (each CONFLICT-FREE). The two sentences in one document (task `t1`): CONFLICT with witness `(Alice, Desk1)`
  on the pair `open_required → open_permitted`, rendered "cmd-u1 requires opening; cmd-u2 forbids it".
- **(δ) Conflicting duties.** `Click Check.` beside the author rule `Rule 1. Every user must not click each control, if
  that control is disabled.`: CONFLICT with witness "Check is disabled; cmd-u1 requires clicking; rule 1 forbids it";
  with the asserted unit `Check is not disabled.` the conflict check is still CONFLICT (base structures are unconstrained
  by document premises) while the premise set is consistent and the outcome line at the tuple is "required, not
  permitted where Check is disabled". A rule with `over: [cmd-u1]`: `UnknownRule: rule cmd-u1`.
- **(ε) Quoted command.** `The manual says: "Click Check."` as `["attributed", "manual", "says", "instruction"]`: no
  rule; `premises(D)` equals the document's without that unit (`dormant_invariance`); the unit is dormant in the status
  text; a graph leaf `layer:norms:click_required` whose formula includes a rule for the quoted command is rejected;
  the single-unit checks still run on the quoted content (a misspelt act is rejected).
- **(ζ) Forged context.** Replay (α)'s certificate with the addressee rebound to `Bob`: stale (new environment id);
  with `the token` rebound: stale; with the query premise list of (μ) extended by the target: `QueryMismatch: u2`; with
  an answer record whose stated answer the certificate does not establish: `AnswerMismatch`. **Stale proof-task
  identity:** (μ) with `q1` retargeted (the wording `Prove that Tom is a cat using these premises.`, the same query
  name and constant `q1`): the command unit's meaning id changes (3.5: it includes the query's premise and target
  meaning ids) and (μ)'s compliance certificate is stale, never carried over; likewise when `q1`'s premise set changes
  (an asserted unit inserted before the task) with the target unchanged.
- **(η) Polar.** `Is Atlas reviewed?` with `Atlas is reviewed.` asserted: `supported yes (certificate)`; "no" not
  supported. With no premise about Atlas: UNKNOWN for both within budget, although a countermodel to `reviewed(Atlas)`
  exists; supplying that model: `evaluated no in model m1 (this situation only)`. **Countermodel is not negation,
  regression:** with `Atlas is not reviewed.` asserted (premises `[¬P]`): the model line from a supplied model is still
  `evaluated no in model m1 (this situation only)` and licenses nothing beyond that model, while "no" is
  `supported no (certificate)` from the premise, and every premise model refutes `reviewed(Atlas)`; the implementation
  must not derive "no" from the countermodel (`countermodel_not_negative` applies only when some premise model
  satisfies `P`, which fails here). Quantified body: `Is it the case that
  every sampled district reported a drop?` over a variant environment with `sampled(district)` and `reported_drop(district)`:
  polar over `∀d. sampled(d) → reported_drop(d)`; `Did every sampled district report a drop?` is rejected with the
  `Is it the case that` rewrite.
- **(θ) Complete list.** `Which of Atlas and Beacon are reviewed?` (mode `which_all`, `H = ⊤`). With `Atlas is not
  reviewed.` and `Beacon is not reviewed.`: `supported none (certificate)` (the token `all []`). With `Atlas is
  reviewed.` and `Beacon is not reviewed.`: `supported Atlas`. With only `Atlas is reviewed.`: UNKNOWN (no token is
  provable), never "Atlas" as a partial answer; in a model with both reviewed: `evaluated Atlas and Beacon in model m2`.
- **(ι) Single choice and presupposition.** `Which one of Atlas and Beacon is reviewed?` (`H = (P(Atlas) ∨ P(Beacon)) ∧
  ¬(P(Atlas) ∧ P(Beacon))`). Both reviewed asserted: PRESUPPOSITION-FAILED (certificate for `¬H`), never "two answers"
  and never "no". `Atlas is reviewed.` and `Beacon is not reviewed.`: `supported Atlas` with `H` proved. Only `Atlas is
  reviewed.`: `supported Atlas given the presupposition` (certificate over `premises ++ [H]`, residual
  `speech:presupposition:u5`), and the unconditional line UNKNOWN. Model path in a model with both reviewed:
  PRESUPPOSITION-FAILED (model m3). The paraphrase shows "exactly one of Atlas and Beacon is reviewed" as presupposed.
- **(κ) Mode from wording.** The plural wording with stored `mode: which_one`: `ModeMismatch: u5`; the singular wording
  with `which_all`: `ModeMismatch`. Renaming the alternatives' order changes the domain list and the meaning id; the
  paraphrase is unchanged in substance.
- **(λ) Consequence question.** `Tom is a cat.` `Every cat is an animal.` `Does it follow from these premises that Tom is
  an animal?`: query `q1` with premises `[u1, u2]`; `follows` (certificate). Drop `u2`: `gap` with the model "Tom is a
  cat and not an animal". Both budgets zero: `unresolved (tableau: 0; search: 0)`. A record with `judgment: refuted`:
  `InvalidInput: judgment`. A certificate and a gap model together: `CheckerConflict`, no record.
- **(μ) Proof task.** `Prove that Tom is an animal using these premises.` after (λ)'s two premises: command on
  `submit_required(Alice, q1)`; a submitted certificate for `Π_q ⊢ animal(Tom)`: `compliance: certificate q1` on the
  compliance line only; `premises(D)` is unchanged by the submission (`premises_core`), no `done_submit(Alice, q1)`
  premise exists, and a graph leaf `speech:compliance:u3` or any leaf `done_submit(Alice, q1)` claimed from the
  certificate is rejected; a countermodel to `done_submit(Alice, q1)` over `premises(D)` still exists after
  acceptance. A certificate whose premise list adds `animal(Tom)`: `QueryMismatch: u3`; with `u2` dropped the task
  stands (`compliance: none`; the report says the target is not established, not that the task is wrong); with `Tom is
  an animal.` asserted earlier: `TrivialQuery: u3` and the task still stands. The report never contains the word
  "understood".
- **(ν) Reading question.** A reading set `rs1@2` over an earlier unit with two candidates; `Which reading did you mean?`
  bound to `(rs1, 2)`. Nomination `0` by `author`: a narrowing recorded, `support: testimony`, status line
  `nominated 0 by author (testimony)`; nomination `2`: `NominationOutsideSet: u6`, CLARIFICATION-OPEN; two nominations:
  CLARIFICATION-OPEN (multiple); none: CLARIFICATION-OPEN (none). The front matter declares the open term
  `intended-reading.u6` exactly as 4.6 derives it (arguments `["rs1"]`, version 2, decided by `Alice`, jurisdiction
  `t1`, empty `necessary` and `sufficient` lists, the two criterion factors) and `u6` has the meaning `{"open":
  ["intended-reading.u6"]}`; the residual lists the term under W2's open-term count, displayed `intended-reading:rs1@2`;
  the question's class is O. A declaration named `intended-reading:rs1@2` (which also fails W2's own token check), a
  non-empty `sufficient` list, or a `specified` meaning on `u6`: `InvalidInput: invalid question fields for u6`; a
  reading question whose unit id has 48 bytes: `ResourceLimit: open-term name`.
- **(ξ) Unbound slot.** `Share the token.` with `the token` removed from `definites`: authoring rejects with
  `UnboundSlot: the token` and the legend rewrite; translation admits the unit as `unformalised(unbound-slot)` (U);
  adding the authored binding unit `In this task, the token is Token1.` (kind `binding`, C) makes the command active.
  `Click Check.` with no addressee: `UnboundSlot: you`.
- **(ο) Modal questions.** `Must Alice open the desk?`: reading set {polar over `open_required(Alice, Desk1)`, follows
  over `done_open(Alice, Desk1)`}; both elaborated; class R with each reading's residual. `Can you open the desk?`:
  {polar over `open_permitted(Alice, Desk1)`, ability (unsupported), request (unsupported)}; class U; the permission
  reading's own line is shown beneath.
- **(π) Coordination.** `Click Check and save.`: `CoordinatedActs` with the two-command rewrite; the rewritten pair is
  two active commands; translation keeps the reading set {two commands, ordered sequence} whose second reading is
  unsupported: U.
- **(ρ) Permission grant.** `You may close the desk.`: not a command wording; hint `PermissionNotCommand` with the
  equality-guarded W1 rewrite `Every user may close each desk, if that user equals Alice and that desk equals Desk1.`
  (strict guard `((x0 equals @Alice) and (x1 equals @Desk1))`), which keeps both bindings; the universal
  `Every user may close each desk.` is not offered (it broadens the permission to every user and desk). As a unit,
  `unformalised(permission-grant)`, U; no rule, no premise.
- **(σ) Please.** `Please click Check.`: authoring accepts after approval and renders `Click Check.`; translation makes
  the unit a reading set {require, request}, U; the require reading's demand is shown beneath it.
- **(τ) Inconsistent premises.** `Atlas is reviewed.` and `Atlas is not reviewed.` with `Is Atlas reviewed?`: both
  "yes" and "no" supported; the premise-set check reports inconsistency; both answer lines carry `premises:
  INCONSISTENT (certificate); vacuous: yes` and the report shows the contradiction; (θ) over the same premises likewise.
  (ι) with only `Atlas is reviewed.` and the conditional line: `premises with H: model m4; vacuous: no`; (ι) with
  `Atlas is reviewed.`, `Beacon is reviewed.` and the conditional line: `premises with H: INCONSISTENT (certificate);
  vacuous: yes` while the unconditional premise status is a model (the conditional line reports the extended list's
  status, never `Π`'s).
- **(υ) Budgets.** (η) with the tableau budget zero: UNKNOWN naming the budget; (λ) with both zero: `unresolved`;
  never an answer, never `gap`. (η)'s `supported yes` with the premise-status budgets zero: `premises: UNKNOWN
  (tableau: 0; search: 0); vacuous: unknown`, never `vacuous: no`.
- **(φ) Profiles.** `speech-acts@0` without `norms@0`: `UnsupportedProfile: speech-acts@0 requires norms@0`; with
  `closure@0`: `UnsupportedProfile: speech-acts@0 with closure@0`; F0 with `soft-norms@0` enabled, with or without a
  `soft__` predicate or a soft-norms block: `UnsupportedProfile: speech-acts@0 with soft-norms@0` (1.6: the
  combination is rejected until specified and proved); F0 plus a `defined` predicate, with or without a command:
  `UnsupportedProfile: speech-acts@0 with definitions`; F0 plus a `functional` flag likewise.
- **(χ) Mixed span.** `Open the writing desk. It contains the token.` as one MIXED unit: part 1 an active command (C);
  part 2 `unformalised(pronoun)` (U); the two parts partition the span; `bytes_by_class` and `bytes_by_status` each
  total the source length and reconcile by the table of 6.
- **(ψ) Coverage projection.** A document with the legend in the environment, one active command, one polar question
  answered by certificate, one unanswered `which_all` question, (ο)'s two units, (ν)'s reading question and a heading:
  classes C, C, C (answer truth irrelevant), R, U, O (the reading question: mode admitted, meaning `{"open":
  ["intended-reading.u6"]}`, its expressly non-formal presupposition carried by that open term, displayed
  `intended-reading:rs1@2`, so not C, and OPEN in W2's status table), L; the environment legend contributes no
  bytes; an authored `binding` unit for `you` counts C and is withheld from P0 admission (3.2); totals reconcile with
  W2's status table.
- **(ω) Identity.** Every existing fixture, identity, certificate and wire hash unchanged; every `ve-document@1` fixture
  loads under `ve-document@2` with the same units and a new document id, which the wrapper recomputes from its retained
  payload alone (`SpeechSource.documentId`, `source_retained`); changing `task`, the addressee or a definite
  changes `environment_id` and stales every certificate; adding an answer record changes the document and report ids
  and not `premises(D)`; two questions differing only in domain order have different meaning ids.
- **(αα) Catalogue and tutorial sentences.** `Open the writing desk.` (C, `open_required(Alice, Desk1)`); `Choose
  authoring or translation mode.` (U, `unformalised(disjunctive-object)`, with the `choose a mode` rewrite offered only
  as a declaration of the object inside the act and no two-command rewrite; after declaring `{0} choose a mode`,
  `Choose a mode.` is C); `Change example now?` (U, `TemporalWording`); the tutorial's `Does the conclusion follow?` after a
  worked argument is the consequence question over that argument's premises and conclusion (follows or gap as the
  argument is).
- **(ββ) Composition.** (α) with the asserted premise `If Alice must click Check then Atlas is reviewed.`: a certificate
  for `reviewed(Atlas)` over `premises(D)` replays (`speech_route_acceptance`); dropping the command makes the same
  certificate fail; the question `Is Atlas reviewed?` then has `supported yes` whose used leaves include
  `layer:norms:click_required` and the asserted unit.

Beside these: norms.md 10.6 to 10.10 repeated on generated speech-act documents (surface round trip of legend, commands
and questions with metadata; identity of every existing fixture unchanged; certificate binding against a changed scope,
declaration, query or record; differential `policy`/`premises`/`H`/`F` Python versus Lean on 1,000 generated documents;
W1 DAG diagnostics on `policy(D)`).

## 10. Limits, regeneration, Rust

Rules ≤ 256 including command rules, regulated predicates ≤ 64, definites ≤ 64, alternatives ≤ 16 per question,
questions ≤ 256, reading sets and choices as W2 (64 complete choices), open-term names ≤ 64 bytes as W2 (so a reading
question's unit id ≤ 47 bytes, 4.6), formulas within `MAX_NODES`; witness and answer
search use the existing bounds and `MAX_EVALUATIONS`; every overflow is `ResourceLimit` with the limit named, never a
truth value. `policy(D)`, `premises(D)`, every `H(q)`, `F(q, a)`, `Π_q` and every leaf formula are regenerated from the
decoded units, records and declarations at every trusted site (norms.md 11.3); a finite model supplies base tables
(including `done` tables) and a supplied regulated table is rejected as in W1. Rust never elaborates speech acts: on the
`elaborated-document` family a speech-act case carries the Python-generated `premises(D)`, `H`, `F` and `Π_q` marked
`untrusted: true`, and its verdict must agree with Python's and Lean's regenerated ones (regression evidence; the trust
path is Lean).

## 11. Statement review checklist (Astra + Fable, before items 2, 3 and 4)

1. `demand(c)` (4.2): equality guards in the predicate's context, no carve-outs, no edges; `policy(D)` as one W1 tree;
   `demand_applies` and `demand_consequence` as the faithfulness statements; `demand_conflict_local` and
   `demand_conflict` (under `AgreesBelow`) for the opposite case.
2. Polarity and roles: `require` on the obligation role, `forbid` on the permission role, `MissingPermissionRole`,
   never `¬required` (1.2, 8.2).
3. `H(q)`, `tokens`, `F(q, a)` and `Answers(q, S)` (1.3, 4.4): the single-mode presupposition; the restricted domain
   with `H = ⊤`; open-domain "which" excluded (12.2); the four `answers_*` facts.
4. The two answer paths (4.5): `Supported`, `SupportedGiven` with the presupposition leaf, PRESUPPOSITION-FAILED on
   both paths, UNKNOWN, `support_exclusive`, `support_exclusive_one`, P0's three-way premise status and the derived
   vacuity (5.3); `countermodel_not_negative` with its premise-model hypothesis.
5. Consequence questions (4.6): exactly `follows`, `gap`, `unresolved`; `refuted` not imported; proof tasks as commands
   on the `submit a proof` act with `QueryMismatch`, their meaning bound to the query's premise and target
   meaning ids (3.5), and acceptance as compliance evidence only (no premise, no leaf, no `done` fact); reading
   nominations as testimony narrowings and the `intended-reading.<u>` open term in W2's frozen schema (empty
   closed-formula condition lists, the criteria as factors, the display label `intended-reading:<set>@<v>`).
6. Exact correspondence and invariance (4.7, 8.4): `premises_core`, `dormant_invariance`, the answer bridge leaf, and
   W1's `norms_route_acceptance` reused on `policy(D)`.
7. Scope (4.8): the block in the environment; `combine` and `ScopeMismatch`; `scope_single`, `policy_rules`,
   `two_task_separation`; the two-task fixture (γ).
8. The English table (2.1): one reading per wording; imperatives from the act phrase; the legend family; the two
   synonyms; the non-synonyms; the rewrites of 2.3 and the reader's checklist (2.4).
9. The report's four lines (5) and the coverage projection (6): C's entry conditions, U/R/O/C precedence, L
   non-substantive only, legend outside the partition, authored bindings as units.
10. The diagnostics (7) and every fixture (9) against the definitions; the wire theorem (8.5) over the decoded-source
    wrapper, with `binding` units withheld from P0 and W2's identity payload, reading sets and narrowings retained
    with their structure (`source_retained`), and the executable (8.6).
11. Open questions, resolved at the statement review (both reviewers): "these premises" = earlier asserted units
    (12.3) is accepted as the `@0` pinning, with the derived query record and `QueryMismatch`; a named wording can be
    added later without moving any identity. The `binding` kind is accepted as route-local (12.1), with the rule that
    binding units are withheld from P0 `admit_document` (3.2).
12. The resolved choices of section 12 and the applied edits of section 13.

## 12. Resolved choices in this draft

Each is a point where the plan left a reading open; the review may overturn any of them.

1. **The scope block lives in the environment**, identity-bound, so that "one scope per document" and "one pinned
   scope per policy evaluation" coincide through `environment_id`, and W3's one-environment bundle rule already
   enforces the separation. Authored `binding` units are a route-local kind of `ve-document@2` (as `rights@0` added
   unit kinds) and must agree with the block; because the frozen P0 kind decoder lacks the kind, they are withheld from
   P0 `admit_document` and enter only the wrapper identity and the coverage projection (3.2, 8.5).
2. **Open-domain "which" is outside `@0`.** The plan's "empirical claim that the listed names exhaust a wider domain"
   is realised as the IDE's rewrite to a restricted domain plus, in translation, the recorded domain-closure named
   assumption; a presupposition that depends on the answer given is not a presupposition, so it is not put in `H(q)`.
3. **"These premises" denotes the earlier asserted units** in document order, the `ve.prose@1` dependency convention,
   and the query record is derived content. A named query form is not offered at `@0`.
4. **Commands take no precedence edges** and cannot be named in `over`. A conflict between a command and a rule is
   reported as a W1 CONFLICT with its witness; the author's fix is a rule or a rewrite, never an implicit priority.
5. **`speech-acts@0` requires `norms@0`** and admits only the allowlist `relational-fol@0`, `norms@0`,
   `speech-acts@0` (1.6): `soft-norms@0` and every other profile are rejected with the route until their composition is
   specified and proved; the norms route's rejection of W3 definitions and W5 flags holds for the whole route,
   questions-only documents included, until INTEGRATION-GAPS closes; one gate, no partial path.
6. **Compliance reuses W1's `done` base predicates as asserted units with their own support kind.** A proof task's
   replayed certificate is compliance evidence on the report line only; it generates no `done` premise and no leaf,
   because `done_submit(you, q)` is a free base atom no certificate entails and a usable leaf would break
   `premises_core`. The checker generates no `done` fact of any kind.
7. **Reading nominations are W2 narrowings with testimony support**; "exactly one intended reading" is expressly
   non-formal (the set is not a domain of constants), so it is a W2 open term in W2's frozen schema, named
   `intended-reading.<u>` and displayed `intended-reading:<set>@<v>`, with the addressee as decider, empty
   closed-formula condition lists and one in-set nomination as the criterion carried in `factors` (4.6), and the
   reading question, whose meaning names the term, is class O (6), never C.
8. **Adoption of quoted commands is deferred**: W1 has no norm bridge, quoted norm content contributes no layer, and the
   same holds for quoted commands; the plan's "separate attributed adoption with a verified norm bridge" is a later
   item with its own statement review.
9. **Proof tasks are commands on a declared act with a `query` sort**, the one act whose completion the checker can
   witness; the query constant is an ordinary declaration so identity binding needs no new mechanism.
10. **Two polar wordings.** `Is <constant> <rest>?` for copular predicate wordings and `Is it the case that
    <sentence>?` for every closed sentence; which-questions are restricted to copular unary wordings, because the
    surface infers no inflection or do-support (english-surface.md).
11. **A command guard is optional `if`**, a closed formula; guards over regulated predicates follow W1's stratification.
12. **`ModeMismatch` is an admission rejection**, following Astra's "reject mismatching stored fields": the wording is
    authoritative and the stored mode is derived content.
13. **The `Do not` wording is the only negative imperative**; `Don't` is its one synonym; `Never` is temporal.
14. **The coverage projection splits substance first**, then applies U, R, O, C; W2's status table is unchanged and
    the reconciliation is a fixed mapping (6).
15. **A proof task's meaning includes its query's meaning** (3.5): the command object of a command with a `query` slot
    carries the query's regenerated premise meaning ids and target meaning id, so a constant `q1` cannot keep a
    command's identity across a retargeting.
16. **Meaning-changing rewrites are not offered** (2.3): a permission grant is rewritten only to the equality-guarded
    W1 rule that preserves both bindings; a disjunctive object is U unless the act declares the object; two demands
    are never offered for a choice.

## 13. Statement review response table (draft 2)

Source: `manage-agents/debates/speech-acts-spec/{astra,fable}.md`, CONVERGED after round 2, verdict FIX with the
union of both edit lists in the forms Astra's round 2 accepted. Process: one edit-verification pass by both reviewers
on this draft (each checks the edits below are applied as written; new findings admissible only where an edit
introduces a defect), then items 2 to 4 start; the proof and fidelity gates still govern enabling the route.

| Debate item | Change in this draft |
|---|---|
| Astra 1 = Fable 2: `countermodel_not_negative` second conjunct unprovable | 8.3: binders `(S' : VE.Structure) (hS' : S'.Admissible (En D)) (hp' : Sat S' (premises D)) (hb' : q.body.denote S' [])` added; the comment removed; 4.5 says why; the `[¬P]` counterexample is a regression in fixture (η). |
| Astra 2 = Fable 1: `demand_conflict` second conjunct false as stated | 8.2: split into `demand_conflict_local` (the elaboration incompatibility, from `hop` alone) and `demand_conflict` with the hypothesis `AgreesBelow (policy D) (before (policy D) c.act) S` for the base-conflict conclusion, W1's `conflict_denote` form (`ConstantsTyped` from `hS`; the `PrefixAdmissible` form a corollary via `agreesBelow_of_meanings`). |
| Astra 3 = Fable 5: representation and signatures | 8.1: `SpeechDoc.regulated : List Regulated` in `core`; `policy` reads it; `regulatedOf D.E` removed (the frozen `VE.Environment` has only sorts, signatures, constants). 8.5: `SpeechSource` (units, bindings, query records, evidence records, graph, provenance) with `toDoc`, and `SpeechAdmitted` in the shape of `Norms.Admission.Admitted`; the wire theorems quantify over them. `AppliesD S ρ N` without the tree argument; `norms_route_acceptance` invoked with exactly `D h hc Γ φ c acc` and `speech_route_acceptance` loses `hΓ hφ`; every abbreviated binder in 8.3 and 8.4 typed. Completed in draft 3 (14): `SpeechSource` retains W2's identity payload verbatim and the open terms, reading sets and narrowings with their structure. |
| Astra 4 = Fable 3, resolved as Astra's "no leaf": the `done_submit` premise | 4.6, 5.4, 8.5, 8.7, 12.6 and fixture (μ): the accepted certificate is compliance evidence on the compliance line only; no premise, no graph leaf (`speech:compliance:<u>` removed), no checker-generated `done` fact; a claimed `done_submit` leaf is rejected. |
| Astra 5: proof-task identity | 3.5: a command with a `query` slot includes the query's premise and target meaning ids in its `ast`; 12.15; fixture (ζ) gains the retargeted-`q1` and changed-premise stale cases. |
| Astra 6: P0's three-way premise status | 5.3: `premises: model | INCONSISTENT | UNKNOWN` on every certificate line, the status of `Π` for unconditional answers, of `Π ++ [H]` for conditional ones, of `Π_q` for judgments; `vacuous` derived (`no | yes | unknown`); 8.5 `PremiseStatusEvidence`; fixtures (τ) and (υ). |
| Astra 7: meaning-changing rewrites | 2.2, 2.3, 12.16, fixtures (ρ) and (αα): the permission rewrite is the equality-guarded rule of norms.md 3.3 keeping both bindings, never the universal; the two-command rewrite for a disjunctive object is withdrawn (two demands are not a choice), the unit is U unless the act declares the object. |
| Astra 8: fixture ψ versus C's formalisation requirement | 1.3, 4.6, 5.5, 6, 12.7, fixtures (ν) and (ψ): "exactly one intended reading" is a W2 open term displayed `intended-reading:<set>@<v>` (decider the addressee, criterion one in-set nomination), counted as an open term; reading questions are class O. Completed in draft 3 (14): the term is encoded in W2's frozen open-term schema under the token name `intended-reading.<u>`. |
| Astra 9: `soft-norms@0` | 1.6 is an allowlist (`relational-fol@0`, `norms@0`, `speech-acts@0`); 4.1(1), 7 and 12.5 updated; fixture (φ) names `soft-norms@0`. |
| Fable 4: `binding` units at the P0 boundary | 3.2, 8.5 (`bindings_withheld`, `SpeechAdmitted.p0`), 8.6, 12.1, fixture (ψ): withheld from P0 `admit_document` (its frozen kind decoder lacks the kind), present only in the wrapper identity and the coverage projection. |
| Fable 5: `inst`, `DecidableEq`, missing helpers | 8.3 `inst [.const a] q.body`; 8.1 `Force` (and `Mode`) `deriving DecidableEq`; `pinnedAsserted` and `trivialQuery` defined in 8.1 (with `Query.premiseIds` and asserted unit ids for them to be definable). |
| Fable 6: single-choice support exclusivity | 8.3 `support_exclusive_one`; 4.5 and 11.4 name it. |
| Fable 7: "per complete compatible choice" | 1.5: attributed to W2's readings query, not `policy(D)`, which excludes every pending command. |
| Both: open questions 11.11 | Accepted: earlier-assertion queries (12.3) and route-local `binding` (12.1, with Fable 4); 11.11 records the resolution. |
| Both: plan synchronisation | speech-acts-PLAN.md draft 3: item 1 records the converged FIX and the verification pass; item 4 gains the stale-proof-task, `soft-norms@0`, countermodel-not-negation and withheld-binding regressions; sections 2 to 4 aligned (open-term reading presupposition, no `done` premise, three-way premise status, allowlist); section 6 maps the edits. |

## 14. Edit-verification response table (draft 3)

Source: `manage-agents/speech-acts-p3ver1.final.md`, the statement-only verification of draft 2 (commit `88e6290`)
against the converged list of section 13: FAIL on two incomplete edits, every other edit and the plan synchronisation
present. Draft 3 completes those two and changes nothing else; a second bounded verification pass checks them, then
items 2 to 4 start.

| Finding | Change in this draft |
|---|---|
| Astra 3, source preservation: `SpeechSource` lacked the source bytes and fences that the 3.5 identity needs, used P0's formula-only `ReadingSet` (which cannot hold command or question candidates) and flattened narrowings to ids, losing their kept choices and reasons | 8.5: `SpeechSource` retains W2's identity payload verbatim (`metadata` without removable weights, `source`, `fences`) with `identityPayload` and `documentId`; new `OpenTerm`, `SpeechReading`, `SpeechReadingSet` (candidates with structured content, admission fields, distinguishing models, history) and `Narrowing` (kept reading ids, author, reason units) in W2's frozen schemas; `lemmas` retained; P0's formula-only sets, open-term names and narrowing ids appear only in the projection `SpeechAdmitted.p0`; theorem `source_retained`; 3.5 and 8.1 say what the wrapper carries; 11.10; fixture (ω). |
| Astra 8, W2-compatible open-term contract: `intended-reading:<set>@<version>` is not a W2 token (`:`, `@`) and the nomination criteria were not closed-formula lists | 4.6: the term is declared in W2's frozen schema, named `intended-reading.<u>` (a token; `ResourceLimit: open-term name` beyond 64 bytes) and displayed `intended-reading:<set>@<version>`; `arguments` the set id, `version` the set's, `decided_by` the addressee, `jurisdiction` the task, `necessary` and `sufficient` empty closed-formula lists (no formula over `E` expresses a nomination), the criteria as `factors`, `precedents` empty; the declaration and the question's `{"open": [...]}` meaning are derived content (3.2, 4.1(4), `InvalidInput`); 1.3, 5.5, 6, 7, 10, 11.5, 12.7, fixtures (ν) and (ψ). |

## 15. Edit-verification response table (draft 4)

Source: `manage-agents/speech-acts-p3ver2.final.md`, the statement-only verification of draft 3 (commit `60ba11d`)
against section 14: FAIL on one defect introduced by the Astra 3 completion; the source bytes and fences, the structured
speech candidates and narrowings, and the Astra 8 open-term contract present and compatible with W2; the plan
synchronised. Draft 4 corrects that one defect and changes nothing else; a bounded verification pass checks it, then
items 2 to 4 start.

| Finding | Change in this draft |
|---|---|
| `source_retained` required `Wire.encodeReadingSets src.readingSets` to reproduce the `reading_sets` front-matter field exactly, but W2 (`ve/readings.py`) accepts both an omitted `models` field and `"models": {}` for a singleton reading; both decode to `models = []` in `SpeechReadingSet`, no field keeps the distinction, and the encoder receives no retained metadata, so it cannot reproduce both originals | 8.5: the theorem is restated without re-encoding. Its first conjunct already retains the `reading_sets` and `narrowings` front-matter fields byte for byte inside `src.metadata` (W2's identity payload keeps every front-matter key but `weights`), optional fields with their presence; the second and third conjuncts now say that the structured `readingSets` and `narrowings` are exactly `Wire.decodeReadingSets` and `Wire.decodeNarrowings` of those fields (`Wire.readingSetsJson`, `Wire.narrowingsJson`, `[]` when omitted as W2 reads them), every set version and every narrowing, no projection. `Wire.encodeReadingSets` and `Wire.encodeNarrowings` are withdrawn; the `models` and `rejectedHistory` comments record the normalisation. No structure, definition or other theorem changes. |

## 16. Implementation review response table (draft 5)

Source: `manage-agents/speech-acts-looprecheck1.final.md`, the recheck of the merged Python and Lean routes against
the Fable and Astra implementation reviews. Each row is a spec-level correction the implementations now share; the
statements of section 8 are unchanged.

| Finding | Change in this draft |
|---|---|
| A, proof wording: the act `{0} submit a certificate for {1}` fails W1's frozen act linter (`for` is reserved), and the Python checker had been given a route-only exception | 1.4, 2.1, 3.1, 11.5 and the plan: the act is `{0} submit a proof of {1}`; the linter is W1's, unchanged, in Python and Lean. |
| A, meaning ids: proof tasks and follows questions digested different objects in Python and Lean | 3.5: the command and question objects are fixed JSON, the query's identity nested as `query: {id, premises, target}`. |
| B, certificate portability: Python folded `F(S)` of a complete-list answer as one mixed conjunction | No text change: 1.3's `⋀_{a∈S} P(a) ∧ ⋀_{a∈dom∖S} ¬P(a)` is two conjunctions, each folded from `⊤` in domain order (W1's `allF`), in every checker. |

## Change log

| Date | Revision | Changes |
|---|---|---|
| 2026-09-28 | Draft 1 | Item-1 specification from plan draft 2: scope block and legend; commands as W1 rules with equality guards, roles and polarity; questions with wording-derived modes, `H(q)`, `F(q, a)` and `Answers(q, S)`; proof and model paths with PRESUPPOSITION-FAILED and conditional support; consequence questions under `follows`/`gap`/`unresolved`; proof tasks and reading nominations; exact consequence correspondence, dormant invariance and the two-task rule; the four-line report; the C/L/O/R/U projection; diagnostics; every item-2 theorem as a statement in W1's Lean conventions; fixtures α to ββ; resolved choices. Spec only: no code, Lean or frozen contract changed. |
| 2026-09-28 | Draft 2 | The converged statement-review edit list applied as written (section 13): `countermodel_not_negative` hypotheses; `demand_conflict` split with `AgreesBelow`; regulated declarations in the core, decoded-source wrapper, `AppliesD` and `norms_route_acceptance` signatures, typed binders; no `done_submit` premise or leaf; proof-task identity over the query's meaning ids; P0 premise status on every certificate line; equality-guarded permission rewrite and no two-command rewrite; `intended-reading` open term and class O; profile allowlist with `soft-norms@0` rejected; `binding` units withheld from P0; `inst`, `DecidableEq`, `pinnedAsserted`, `trivialQuery`, `support_exclusive_one`; 1.5 attributed to W2's readings query; fixtures ζ, η, μ, ν, ρ, τ, υ, φ, ψ, αα; 11.11 resolved; 12.15, 12.16. Spec only. |
| 2026-09-28 | Draft 3 | The two edits the verification pass found incomplete (section 14): Astra 3, `SpeechSource` retains W2's identity payload (metadata, source, fences), structured open terms, reading sets with speech candidates, narrowings and lemmas, with `identityPayload`, `documentId` and `source_retained`; Astra 8, the `intended-reading` open term encoded in W2's frozen schema (token name `intended-reading.<u>`, display label `intended-reading:<set>@<version>`, empty closed-formula condition lists, criteria as factors, derived declaration and `open` meaning). Sections 1.3, 3.2, 3.5, 4.1, 4.6, 5.5, 6, 7, 8.1, 8.5, 10, 11, 12.7, fixtures ν, ψ, ω. Spec only; no other change. |
| 2026-09-28 | Draft 4 | The one defect of the second verification pass (section 15): `source_retained` restated over the front-matter fields the identity payload retains verbatim, the structured reading sets and narrowings as their decoding, `Wire.encodeReadingSets` and `Wire.encodeNarrowings` withdrawn; the `models` and `rejectedHistory` comments. Section 8.5 and the status header only. Spec only; no other change. |
| 2026-09-28 | Draft 5 | Implementation review corrections (section 16): the proof-task act phrase passes W1's frozen linter. |
