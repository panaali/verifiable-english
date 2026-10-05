# Composition stage S1: content-bearing reading candidates and separating situations (`readings@1`, part A)

> Status: item-1 specification, draft 2 (2026-10-02), written from [composition-PLAN.md](composition-PLAN.md)
> draft 2 (its sections 2.2 and 2.4, its S1 section, its fixtures and its open questions 3, 4, 12 and 13) through
> the pointer plan [composition-S1-PLAN.md](composition-S1-PLAN.md) draft 2, which records the converged Astra +
> Fable design debate (`manage-agents/debates/design-compose-s1/{astra,fable}.md`, CONVERGED after round 3; the
> Astra seat was held by Sol xhigh as the recorded cross-family stand-in) and the edits of it that bind S1. This is
> the file the plan and [composition.md](composition.md) call `readings.md`. It is the statement under the Astra +
> Fable item-1 review that gates S1's Lean (PLAN-EXPAND2 rule 10): a draft alone opens nothing. **Draft 2** applies
> the converged statement review of draft 1 (`manage-agents/debates/compose-s1-spec/{astra,fable}.md`, verdict FIX,
> CONVERGED after round 3, the Astra seat again held by Sol xhigh) and nothing else: Fable's six edits and the Astra
> seat's refusal of a fixed unit attached to two sets, each listed in the change log. No design question is
> reopened. A verification of draft 2 against that review (`manage-agents/compose-s1-p3ver1.final.md`) found the
> seven corrections present, nothing else changed in substance, and one of them overstated: 4.5 said that
> `separates` enforces all of step 1, and `situationWF` does not test the base's validity. That claim is now
> qualified; no definition or theorem statement changes (change log). The changed statements, admission rules,
> wording and fixtures are under re-review (12), and the build opens when it passes. **Frozen inputs**:
> composition.md draft 3 (the stack contract, `dispatch`, the slot, `Content`, the wordings E1 to E21 and the
> diagnostics texts of its section 8) and `lean/VE/Compose/{Slot,Dispatch,Content}.lean` as merged; this file
> instantiates them and changes none. Sections 1, 4 and 8 are the statements under review; section 13 lists every
> point where this draft chose between readings of the plan. Theorem statements and fixtures are implementation
> obligations, not claims of completed proofs or tests. Every expected value of section 9 was derived by reading the
> sources; none has been executed. Inputs: the plan; composition.md; [document.md](document.md) (W2);
> [norms.md](norms.md) (W1); [soft-norms.md](soft-norms.md); [rights.md](rights.md);
> [norm-defaults.md](norm-defaults.md); and, read at `3a99ed1e`, `ve/readings.py`, `ve/rights.py`,
> `ve/document.py`, `ve/profiles.py`, `lean/VE/Finite.lean`, `lean/VE/Norms/{Tree,Elaborate,Prefix,Conflict}.lean`,
> `lean/VE/SoftNorms/{Tree,Soften,Semantics,Coherence}.lean`,
> `lean/VE/Rights/{Tree,Correlate,Semantics,Route,Wire,Run,Admission,Examples}.lean`,
> `lean/VE/Route/Readings.lean`. Nothing here changes a frozen contract, a canonical byte, an identity or an
> existing theorem statement, or the answer of any executable on a document that does not turn `readings@1` on.

## 0. Scope, one paragraph

Today a reading candidate of kind `norm` has `content: null`, and a right candidate is checked alone, over its own
generated vocabulary, so a strict and a default reading of one sentence never share a situation (plan section 1,
failure 2). S1 makes a candidate a content: a norm, a right, added right lines or a limitation, in the existing
wire forms, with the identity of the same content as a fixed unit. It admits a set by four checks (closure,
distinct declarations across sets, each candidate elaborates beside the fixed units, every pair is separated), and
it defines separation so that both readings are checked on **one situation**: a finite base over the author's
vocabulary and the decisions of the fixed units, with only the witnessing reading's own decisions beside it. Lean's
`separates` is the authority; Python searches for the situation (untrusted; since lean-first batch 3 nothing
replays Lean's answer, 8.4). S1 also
lets every candidate carry `labels` and every labelled set be coupled, and reports two findings
(`SeparatedByActOnly`, `SeparatedByDecisionOnly`). S1 adds **no premise, no slot and no verdict**: a document
verdict that depends on a content-bearing set stays UNKNOWN ("superposition pending") until S2. What it buys is
measured, not predicted (section 11).

In this specification: definitions (1), the English (2), wire and identity (3), the semantics (4), what a checked
separation certifies (5), the report (6), diagnostics (7), the Lean definitions and every theorem as a statement
(8), the acceptance fixtures (9), limits, regeneration, Python and Rust (10), the measured unlock (11), the review
checklist (12), the resolved choices (13).

Out of scope, by the plan: `sup`, `Choice_D`, quiescence, every verdict across readings, `DeadReading`, the copy
mapping of a fixed reference to qualified copies (S2); clauses and relations (S3); reference resolution (S4); bar
candidates as contents (the one enumerated axis, S2b); any composition with a route outside the chain
(composition.md 4.2 names the abstention); any coverage number.

## 1. Definitions

### 1.1 The profile, its route and the chain

`readings@1` is the wrapper profile of rank 3 (composition.md 1.1). S1 registers it in `ve/profiles.py` and in
the gate of its own executable; no S0 file changes (`wrapperProfiles` already lists it). `dispatch` is
composition.md 4.2's, unchanged: the profile requires `norms@0`, sits on the routes `norms`, `normDefaults`, `soft`
and `rights`, and its head is `readings`. The head validates the reading sets and hands every other case to
`dispatch` on the list without `readings@1` (4.1).

```text
chain of a list    rights   if the list has rights@0
                   soft     else if it has soft-norms@0
                   norms    otherwise (norms@0 alone; a candidate norm is then a strict rule, composition.md 1.6)
```

With `norm-defaults@0` in the list, a set that holds a content-bearing candidate is the named abstention
`UnsupportedProfile: readings@1 content with norm-defaults@0 is not implemented` (13.7). A formula-only set on such
a list validates as today.

### 1.2 Candidates, sets and the document

```text
content              composition.md 1.6: assertion φ | norm N | right R | rightLines r ls | limitation L
candidate            an id, a content or none, the cites of a norm content, labels
pending candidate    a candidate with no content of this section: content null on the wire, or a wire content S1
                     does not elaborate (a quantity, a composite W2 kind). S1 checks nothing for it
content-bearing      a candidate whose content is a norm, a right, right lines or a limitation
formula-only set     a set none of whose candidates is content-bearing
content-bearing set  a set with at least one content-bearing candidate
fixed unit           a unit with content that is no open set's unit, and the one signed reading of an authored set
open set             the active version (W2: the latest version per unit) of a set with status open
document D           the chain, the frame (the environment: E, literals, the soft block, the regulated and defined
                     predicates, the rights block, the source unit ids), and the items in source order: a fixed
                     content, a fixed bar, or an open set
```

A unit's content is in force only under its kind, as W2 loads it (Python's `ve/document.py`): a formula is an
assertion only in a unit or candidate of kind `asserted`, a norm is a rule only in a unit of kind `norm`, and a
rights block is correlated from a unit of a rights kind or `norm`. Any other unit (a quoted norm, a formula of kind
`question` or `example`, any composite kind) is no fixed unit, and a formula candidate of another kind is pending.
So the wire of 8.4 carries every unit's `kind`, and a unit with content and no kind is refused (`InvalidInput: unit
kind is required`).

A candidate of a composite W2 kind (quoted, hedged, causal), a quantity candidate and a bar candidate are not
contents: the first two keep today's handling of their own content, and a bar candidate keeps `content: null`
(13.8). All three are pending candidates in every check of S1: such a candidate has no document `one D s i`, it
declares nothing, and a pair it is in needs no situation (3, 4.5). A set may mix kinds (plan 2.2): the unit takes
the kind of the candidate chosen.

### 1.3 Declared names, interface names, attached units

```text
declared names of a content     composition.md 1.6, Content.declared: pairs (kind of name, name), kind ∈ rule, right,
                                limitation
names a content uses            a norm: its over entries, and the rule named by a cites key over:<rule> or
                                narrows:<line>; a right or right lines: the same per line (both units of a power),
                                and for right lines the target right; a limitation: the rights of its scope
declared by set t               declared by some candidate of t
interface name of t             declared by every candidate of t (a pending candidate declares nothing)
attached(u), u a fixed unit     the least family of sets with t ∈ attached(u) when u uses a name declared by t, or
                                a name declared by a fixed unit u′ with t ∈ attached(u′)
free fixed unit                 attached(u) = ∅
fixed(s)                        the fixed units u with attached(u) ⊆ {s}, in source order
```

A fixed unit that uses a name declared by set `t` exists only relative to `t`'s readings: in S2 it is copied per
candidate (plan 2.3). So it takes part in checking `t`'s candidates and in no other set's (13.4). A fixed unit
attached to more than one set would take part in no check at all, so S1 refuses the document (4.2).

### 1.4 A candidate's document

```text
one D s i    the document of fixed(s) and candidate i of s, each unit at its source position, assembled as the
             rights decoder assembles units today (rights 1.6; lean/VE/Rights/Wire.lean addUnit), together with
             the assertions in force: the fixed assertion units, and the candidate's own formula if it is one
free D       the document of the free fixed units alone, and the fixed assertions
```

`one D s i` is an ordinary document of the chain: no generated name, no choice atom, nothing qualified. It is
regenerated from the decoded document at every trusted site and bound to the chain's document hash (norms 11.3,
soft-norms 3.4, rights 3.5). Units of other open sets are absent from it.

### 1.5 Generated predicates, source keys, shared and owned

The chain generates base predicates for a document `X`: the decision predicates of soft-norms 1.3 and the
limitation, condition and bar predicates of rights 1.5. Their names depend on the document (rights' are
positional), so a situation never names them. It names their **source keys**:

| Key | Generated predicate of `X` | Source | Sorts |
|---|---|---|---|
| `excepted r` (`bearer b`) | `soft__excepted__<rule>` | a default rule: an outside rule named `r`, or a line whose author rule name is `r`; `b` for the fan-out instance on bearer sort `b` | the rule's predicate's |
| `off r` (`bearer b`) `π` | `soft__off__<rule>__<π>` | likewise, per alterable party `π` | the same |
| `outweighs a L H` | `soft__outweighs__<L>__<H>__<a>` | holistic outranking and a comparable colliding default pair on act `a`, ranks `L` below `H` | the act's |
| `lim L a` | `rights__lim__<k>` | limitation `L` and the act key `a` of a line in its scope | the act's |
| `cond L a c` | `rights__cond__<k>` | likewise, condition `c` | the act's |
| `aimed m` | `rights__bar__<k>` | a bar unit and a liberty or power-liberty line on `m` | `m`'s |

```text
owned by candidate a_{s,i}    a key whose rule name (excepted, off) or limitation name (lim, cond) the candidate's
                              content declares
shared                        every other key: its rule or limitation is a fixed unit's, or it names environment
                              names only (outweighs, aimed)
```

A shared table is one table for both readings of a pair: the decision of a fixed rule's exception, of a fixed
limitation on an act, of the bar on a permission, of the outranking decider on an act. A reading whose document
does not generate a shared key does not read its table. An owned table is the reading's own: no other reading
has it (candidates of one set may share a rule name; each then owns its own table for it).

### 1.6 Situations, probes, separation

```text
situation σ      base       a finite model over the author's base vocabulary: sorts, constants and base predicates
                            of E (no regulated, defined or generated predicate)
                 fixed      tables for shared keys, by key                 (absent: empty)
                 witness    the reading the situation was built for
                 decisions  tables for keys the witness owns, by key       (absent: empty)
                 probe      outcome p v̄ | selects kind p v̄ | holds
                 value      the recorded value of the probe under the witness, true or false
probe            outcome p v̄       the value of the regulated predicate p at the typed tuple v̄
                 selects k p v̄     whether some rule or line of kind k on p selects at v̄. k is an instance kind of
                                   rights 1.2 (claim, liberty, immunity, powerLiberty, powerRecognition) or norm
                                   for a rule outside rights. The key is (kind, predicate, tuple), today's key
                                   (ve/readings.py); a probe never names a rule
                 holds             whether every assertion in force is true
completion       a reading's document, the base, the shared tables, and tables for the keys the reading owns,
                 admissible for the reading's document (BaseAdmissibleR)
Achieves(a, B, F, q, v)   B is admissible over the author's base vocabulary (no true tuple on any other predicate,
                          a generated one included), and some completion of a over base B and shared tables F
                          gives probe q the value v
Separated(a, b)           ∃ B, F, q, v. Achieves(a, B, F, q, v) ∧ ¬ Achieves(b, B, F, q, v), or the same with a and b
                          exchanged
```

Outcomes, selections and assertions are read in the **expansion** of a completion: every regulated and defined
predicate at its meaning over the base (soft-norms' `canon`), so a guard or an assertion that mentions a
regulated predicate reads the document's own outcome (13.5). An outcome probe has the value `v` when the direct
semantics gives `some v` (soft-norms 4.2, `ValueSoft`; on a rights document `ValueRight`, by `correlate_faithful`);
where two rules collide the act has no value and no outcome probe is achieved there.

### 1.7 Findings

```text
force twins                two candidates that are equal except in one rule, which is strict in one and default in
                           the other with every other field equal (mode, exception and hard apart)
SeparatedByDecisionOnly    force twins whose default rule has no sufficient exception condition, is no fan-out
                           instance, and is the only rule on its act in the default reading's document
SeparatedByActOnly         two norm-bearing candidates each of which regulates exactly one act, and the two acts
                           differ
```

Both are report lines of an admitted set, never errors. `SeparatedByDecisionOnly` is emitted only under its
criterion. The theorem that would make the criterion sufficient, `decision_only_sound` (8.3: with the default
reading's exception table empty the two readings reach the same probe values on every base), is stated and **not
proved**. Until it is, the finding is **not certified** (DRI ruling 2 of 2026-10-02): its text carries
` (not certified)` (7), its English says so (E25), and nothing downstream reads it as a checked result. A pair that
fails the criterion gets no finding, whatever is true of it. `SeparatedByActOnly` is syntactic: two readings with no common act have no shared
act on which a situation could separate them.

### 1.8 Reserved names

Under `readings@1`, author input is rejected (`InvalidInput`, composition.md 1.7 and 8) when a sort, constant or
predicate name begins `ve__`, when a rule, right or limitation name begins `rd-`, or when an element name of a
situation contains `__` or begins `rd-`. S1 generates no such name; the prefixes are reserved for S2.

## 2. The English (one reading each)

S1 registers E5, E14, E16, E19 and E21 of composition.md 2.1 with the slots that table leaves to the
registering stage, and four sentences of its own (E22 to E25). E15 is not shown while `decision_only_sound` is
unproved: it states the theorem's claim as checked, and E25 takes its place (1.7). The frames of E5 to E21 are composition.md's and are
not restated. No sentence here can be written by an author as document content. Each goes through W7's
all-derivations gate, and E14, E22 and E23 through W8's fidelity gate, before it is shown. If S1 is the first stage
to wire `dispatch`, it also registers E1 and E2 and checks fixtures G1 to G3 (composition.md 6).

### 2.1 Slots

| Slot | Definition | Used in |
|---|---|---|
| `<axis>` | `bearer`, `polarity`, `incident` or `force` (rights 3.3); for any other axis token `t`, the two words `label t` | E5 |
| `<source word>` | the text of the set's recorded `source_word` span (3), ASCII letters lowercased and U+2019 read as an apostrophe, in italics. It must be one of `shall`, `shall not`, `should`, `should not`, `shouldn't`, `must`, `must not`, `always`, `never`. A set without the span, or whose span holds any other text, has no source word, and E14 is not used for it | E14 |
| `<strict paraphrase>`, `<default paraphrase>` | the canonical VE sentence of the twin rule under each reading (norms 2.1, soft-norms 2.1, rights 2.1), without its header, in italics | E14 |
| `<subject>` | after `applies to`: the probe tuple's element names in slot order, `a`, `a and b`, or `a, b and c`. In an outcome sentence: the element at slot 0 of the probed predicate. S1 never renders a pronoun for it | E14, E19 |
| `<outcome sentence>` | composition.md 2.1: `<subject> still must`, `<subject> is not required to`, `<subject> is permitted to`, `<subject> is not permitted to`, by the probed predicate's role and the checked value | E14, E19 |
| `<act phrase>` | the declared act phrase of the reading's one act with its slot markers removed, in italics | E16 |
| `<situation>` | `<fact>[; <fact>]*`, in this order: per element, `<name> is <a or an> <sort noun>`, by sort then name; per true base tuple, the predicate's declared verbalisation; per tuple of a decision table in the shown situation, `suppose <decision>`. A situation with no element is the one fact `nothing exists` | E19, E21 |
| `<decision>` | `excepted` of the witness's own rule: `<decider> decides the exception applies to <tuple>`; of a fixed rule: `<decider> decides the exception to sentence <n> applies to <tuple>`; `lim`, `cond`, `aimed`: `<decider> decides that` and rights 2.1's generated English at the tuple; `off`: `<party> has turned sentence <n> off for <tuple>`, or `this sentence` for the witness's own rule; `outweighs`: `<decider> decides that <rank L> outweighs <rank H> for <tuple>`. `<tuple>` is written as `<subject>` after `applies to` | `<situation>` |

`<reading>`, `<decider>`, `<citation>` and `<n>` are composition.md 2.1's. Element names are shown as the
situation records them.

### 2.2 Wordings S1 adds

| # | Wording | The one reading | Formal content | Gate |
|---|---|---|---|---|
| E22 | `Where this sentence applies and a rule that says must, must not, may or need not decides the same act the other way, (1) contradicts that rule and (2) gives way to it.` | Where the open sentence's rule applies and a strict rule decides the act against it, the strict reading is a conflict with that rule and the default reading is blocked by it. | soft-norms 4.2 step 2; W1's conflict check. Shown after E14 only when no rule of the default reading's document takes precedence over the twin (none names it in `over`), and that document has a strict rule on the twin's act, of the opposite effect (incompatible with the twin, soft-norms 1.4), that is not related to the twin by precedence (`over`, in either direction, through any chain) | W7, W8 |
| E23 | `Under (1), a rule on the same act that says should, should not, generally may or generally need not gives way wherever (1) applies. Under (2), it gives way only as the ranks of the two rules decide.` | Where the strict reading's rule applies, it blocks that other rule: a strict rule blocks a default rule on its own predicate, or one whose effect is incompatible with its own across the act's declared pair, wherever it selects, and with no rule taking precedence over it the strict rule selects wherever it applies. The default reading's rule blocks nothing: under strict outranking, one of two default rules gives way to the other only by rank dominance. | soft-norms 4.2 steps 2 and 3. Shown after E14 only when all of these hold: the document's outranking flag is `strict`; no rule of the default reading's document takes precedence over the twin; that document has a default rule, other than the twin, on the twin's act that step 2 blocks under the strict twin (it is on the twin's predicate, or its effect is incompatible with the twin's across the declared pair, soft-norms 1.4) and that is not related to the twin by precedence | W7, W8 |
| E25 | `It is not certified that these two readings differ only where <decider> decides that the exception applies.` | The finding `SeparatedByDecisionOnly` was computed from its criterion. Nothing about the pair is claimed: whether the two readings differ only there is not established. | the finding, whose theorem `decision_only_sound` is unproved (1.7, 8.3); replaced by E15 when that theorem is proved | W7 |
| E24 | `These two readings differ in a checked situation that VE cannot yet show in words.` | A situation separating the two readings was checked. No registered sentence renders it. Nothing is said about what the difference is. | a checked separation whose probe has no registered wording yet: a `selects` probe until S2b registers E20; a mixed pair recorded with `holds` until `right-clauses.md` registers its wording (composition.md 2.1) | W7 |

E22 and E23 are the two sentences composition.md 2.1 asks S1 to add to E14 (plan open question 3). They are
statements of the semantics, not of the shown situation, which is why each is conditional and each is shown only
when the document has a rule it speaks of and the semantics makes the sentence true of that rule. Three cases are
therefore left without either sentence (soft-norms 4.2 steps 2 and 3). A twin that some rule takes precedence over
need not select where it applies, and a strict rule that does not select contradicts and blocks nothing. A strict
rule does not block a default rule of a compatible effect on the other predicate of the declared pair (a strict
requirement beside a default permission). Under holistic outranking the `outweighs` decision, not rank alone,
decides between two default rules. No theorem backs the two sentences beyond the definitions they paraphrase;
`force_agrees_off_exception` (8.3) says only that a rule alone differs from its strict twin nowhere but where the
exception applies.

### 2.3 Which wording a pair gets

A pair of an admitted set is shown by the first row that applies:

1. E14, when composition.md 2.1's four conditions hold and the set has a source word (2.1). E22 and E23 follow it
   when their conditions hold. E25 follows when the finding applies.
2. E19, when the recorded probe is `outcome`, with the second sentence by composition.md 2.1's four cases.
3. E21, when the recorded probe is `holds` and both candidates are assertions.
4. E24 otherwise. On a rights document the reader's checklist keeps rights 2.3's display of the situation ("who
   owes what to whom" under each reading) beside it, as today.

E16 is shown under the set when the finding applies, E5 under each coupling. Python's search prefers an `outcome`
probe, then `holds` between two assertions, then `selects`, then `holds` on a mixed pair, so E24 is the exception.

### 2.4 Non-wordings, beyond composition.md 2.2

- A pronoun for `<subject>`. The outcome sentence repeats the name.
- `may not`, in a frame or in a slot. `<source word>` is a closed list without it, and `<subject>` joins names
  with `and`, so composition.md's G9 holds of every rendering S1 produces (composition.md 13.20).
- E15, in S1: its second sentence states `decision_only_sound`'s claim, which is unproved (1.7). E25 for a pair that
  does not meet the criterion of 1.7, or for a pair that was merely recorded with a decision.
- E14 with a paraphrase that adds words to the canonical sentence (13.11).
- Any generated name, source key or situation id.

### 2.5 Examples

On fixture K1 (9.2), with decider `unstated` and source word *shall*:

- E14: "This sentence says *shall*. (1) *Every agent must avoid deceiving each user.* (2) *Every agent should avoid
  deceiving each user.* They differ here: suppose the decider decides the exception applies to a and u. Under (1) a
  still must. Under (2) a is not required to."
- E25: "It is not certified that these two readings differ only where the decider decides that the exception
  applies."

On K6: E19, "These two readings differ here: a is an agent; u is a user. Under *should*, a is not required to. Under
*must* that is not so, whatever is decided." On K14: "These two readings differ here: a is an agent; u is a user; a
asks u. Under *must*, a still must. Under *should*, this situation is ruled out, whatever is decided." On K4: E16,
"These two readings are about different acts: *avoid deceiving* / *help*. No situation separates them on a shared
act."

## 3. Wire form and identity

Under `readings@1` a reading (document.md; `ve/readings.py`) keeps its five fields and may carry `labels` on every
chain. Its `content` is `null`, a formula or quantity as today, or one of:

```json
{"norm": {"name": "no-deception", "predicate": "avoid_required", "sign": true, "guard": ["top"], "unless": [],
          "over": [], "mode": "default",
          "exception": {"decided_by": "unstated", "sufficient": [], "necessary": [], "factors": []}},
 "cites": {}}
{"right": { … }}          {"right_lines": {"right": "r18", "lines": [ … ]}}          {"limitation": { … }}
```

in the existing unit wire forms (norms 3.2, soft-norms 3.2, rights 3.2), `cites` optional on a norm as on a norm
unit. `kind` is the content's kind word (`asserted`, `norm`, `right`, `right_lines`, `limitation`;
`Content.kind`). `meaning_id` is the digest of the same content as a fixed unit (norms 11.2, soft-norms 3.4,
rights 3.5), so a candidate and that unit have one identity. A content needs its chain profile (`Content.needs`).

A content-bearing set records its separations in a new optional field, and may record its source word:

```json
"source_word": [12, 17],
"situations": {
  "<situation id>": {
    "base": {"domains": {"agent": ["a"], "user": ["u"]}, "constants": {}, "relations": {"asks": []}},
    "fixed": [{"key": {"excepted": "be-kind"}, "tuples": [["a", "u"]]}],
    "witness": "default",
    "decisions": [{"key": {"excepted": "no-deception"}, "tuples": [["a", "u"]]}],
    "probe": {"outcome": {"predicate": "avoid_required", "tuple": ["a", "u"]}},
    "value": false}}
```

- Keys: `{"excepted": r}`, `{"off": r, "party": π}`, each with an optional `"bearer": b`;
  `{"outweighs": a, "lower": L, "higher": H}`; `{"lim": L, "act": a}`; `{"cond": L, "act": a, "condition": c}`;
  `{"aimed": m}`. Probes: `{"outcome": {"predicate", "tuple"}}`, `{"selects": {"kind", "predicate", "tuple"}}`,
  the string `"holds"`.
- `base` is the existing finite-model wire form over the author's base vocabulary and lists exactly its base
  predicates. `fixed` and `decisions` list each key at most once, in the order of 1.5's table, then by name.
- The situation id is the digest, under the domain tag `ve-situation-<identity version>`, of
  `{"environment_id", "situation"}` with the entry in canonical form, as a model id is computed today.
- In a content-bearing set, `admission.distinguishing_models` maps each other reading to a situation id for every
  pair in which neither candidate is pending (1.2: a quantity, composite or bar candidate is pending); both
  readings of a pair may name one situation. The situation a reading names for a pair has one of the two readings
  of that pair as its witness: a situation recorded for the pair (x, y) with a third reading z as witness would
  check (z, x) and leave x and y uncompared, so it is `InvalidInput: invalid situation <id>` (4.5 step 1). A pair with a pending candidate keeps any token, as today. `models`
  is not read for such a set.
- `source_word` is a byte span inside the unit's span.

Identity. S1 adds no identity. Every new key is absent from canonical bytes when absent, so existing reading sets,
environments and documents keep their identities. A set's situations and source word are validated metadata of
the document: the wrapper report identity binds them as it binds `models`, and no meaning identity does. Removing a
narrowing or a coupling changes no identity of a set (plan F2). `couplings` (rights 3.3) is accepted under
`readings@1` on every chain. With `readings@1` off, every construct of this section is rejected with today's
texts, and `rights@0`'s right sets keep today's validation.

## 4. Semantics

### 4.1 The head and the order of checks

The head `readings` validates and strips `readings@1` and calls `dispatch` on the rest (composition.md 4.2,
`dispatch_descends`). A document none of whose sets is content-bearing is handed to the lower route unchanged,
with today's reading-set validation (4.9). Otherwise the head runs, in this order, stopping at the first error:
today's structural validation of the sets with its texts; the abstentions of 1.1 and 1.2; reserved names (1.8);
distinct declarations (4.3); closure, then single attachment (4.2); the lower route's own checks on `free D`; per
set in source order and per candidate by index, the chain's well-formedness of `one D s i` (4.4); per set and per
pair of candidates neither of which is pending, the separation check (4.5); couplings (4.7). A refused document is
never partly checked.

**S1 limitation: what Lean checks** (DRI ruling 3 of 2026-10-02). Lean's `readings-validate` (8.4) decodes the
units and the active sets and runs the checks above from the abstentions to the separation check. It does not
decode couplings or narrowings, so it does not run 4.7, and it does not repeat W2's structural validation of the
sets (today's texts of `validate_reading_sets`), which Python runs first. `Doc.couplings` and `Doc.narrowings` are
empty in every decoded document. Those checks are Python's alone (`ve/readings.py`: `validate_reading_sets`,
`validate_couplings`, `validate_narrowings`), with their texts unchanged, and no report says that Lean checked
them: the report's `readings.checked_by` names what each checker covers (6).

The layer contract of composition.md 4.1, for this stage:

| Rule | What S1 supplies |
|---|---|
| 1. One position | the head `readings`; "unchanged when off" is 4.9 and F20 |
| 2. Source in, same kind out | `one D s i` is an ordinary document of the chain (`chain_soft`). A situation supplies tables for the chain's generated predicates, as every finite model of a soft or rights document does today; it names them by source key, and no document S1 hands on mentions one |
| 3. Regenerated | `readings-validate`'s answer (8.4), regenerated by Lean from the decoded document; Python relays it (lean-first batch 3 deleted the byte-for-byte comparison with Python's regeneration) |
| 4. Premises through slots | none: S1 adds no premise (5) |
| 5. Identity when unused | `one_formula_only`, `separation_conservative` |
| 6. Abstention is named | the four `UnsupportedProfile` texts of section 7 |

### 4.2 Closure and interface names

A fixed unit may use a name declared by a set only if it is an interface name of that set:
`ReadingInterface: <set>: <name>` otherwise, for the first such set in source order and its first such name. So
`Right 18 includes: …` is admissible exactly when every candidate of `rs_u066` declares right 18. A candidate may
use only names declared in its own document `one D s i`: its own, those of `fixed(s)`. A name it uses that only
another set, or a fixed unit attached to another set, declares is undeclared there, and the chain reports it (4.4).

**Single attachment.** After closure, every fixed unit must be attached to at most one set:
`UnsupportedProfile: readings@1 fixed unit <u> depends on reading sets <s> and <t>` otherwise, for the first such
unit in source order, `<s>` and `<t>` the first two sets it is attached to, in source order. A unit attached to two
sets is in neither `free D` nor any `one D s i` (1.4), so no check of S1 would read it, and the document would be
admitted with that unit unchecked. Checking it needs one candidate of each set, which is S2's complete choice: the
refusal is S1's named abstention, and S2 lifts it (13.4). The check runs before `free D` and every `one D s i` are
checked.

### 4.3 Distinct declarations across sets

Every name a candidate declares is distinct from every name a fixed unit declares and from every name a candidate
of another set declares: `DuplicateDeclaration: <name> in reading sets <s> and <t>`, with `<s>` before `<t>` in
source order, or `<t>` the words `the document` for a fixed name. Candidates of one set may share a name. The
check is over all open sets at once and compares names whatever their kind (13.14), because the chain requires
rule, right, limitation and bar names to be distinct together, and a compatible choice in S2 holds one candidate of
every set. It is the hypothesis `distinctAcrossSets` that the plan's `choice_wellFormed` names.

The same check requires the names declared by fixed units, bars included, to be distinct across the whole
document, whatever their kind and whichever sets the units are attached to. The chain cannot be left to find such
a duplicate: two fixed units attached to different sets meet in no `one D s i`, and single attachment (4.2) does
not help, since each of the two is attached to one set. A name that two fixed units declare is refused with the
chain's own text for a repeated name, for the first fixed unit in source order that declares a name an earlier one
declares, and its first such name: `DuplicateDeclaration: rule <name>` (norms 4.1); on the rights chain
`DuplicateDeclaration: right <name>` when a right has the name, else `limitation <name>` when a limitation has it,
else `bar` when a bar has it, else `rule <name>` (rights 8, as `checkRights` words it).

### 4.4 Each candidate elaborates

**The line order first** (DRI ruling 1 of 2026-10-02). On the rights chain, `free D` and every `one D s i` with
content list each line of each right once in their line order (`sourceOrder`, which `place` builds): the first entry,
in line order, that is no line of a right of that name is the rights decoder's `UnknownRight: <r>` (a `right_lines`
unit before its right, which `VE.Rights.Wire.addUnit` refuses and `place` does not), and the first entry that an
earlier entry repeats (a right that lists one line twice) is `InvalidInput: line order lists a line of right <r>
twice`; on `one D s i` either text takes the suffix below. `linesOnce` (8.3) is the check as a Boolean, and
`genKeys_nodup` takes it as its hypothesis. The frozen rights checks are unchanged; this check runs before them.

For every candidate with content, `one D s i` passes the chain's well-formedness: `WellFormedRights` on the rights
chain; `WellFormedSoft` on the soft chain; on the norms chain `WellFormedSoft` of the document with the empty soft
block, every rule strict (13.6). Every assertion in force is well-formed over the complete vocabulary. A failure is
the chain's own diagnostic followed by ` under <set>@<v>:<i>`, `<i>` the candidate's index in the set as in W2's
`readings:` labels: a default candidate that takes precedence over a hard fixed rule is
`SoftOverHard: rule <n> over <m> under <set>@<v>:<i>`. Findings of the chain that need no certificate
(`limitationScope` without certificates, `noDistinction`) are computed per candidate and reported with the same
suffix (plan F5).

### 4.5 The separation check

For readings `a` (the witness) and `b` of a set, neither of them pending (1.2), and a situation `σ` recorded for
the pair:

1. `σ` is well-formed: its id is its digest; its witness is `a` or `b`, the two readings of the pair it is recorded
   for (3); `base` is a typed finite model over the author's base vocabulary and
   lists no other predicate; no key is listed twice; every `fixed` key is owned by neither reading and is
   generated in `a`'s or in `b`'s document; every `decisions` key is owned by `a` and generated in `a`'s document;
   every table, the shared tables each reading reads and the decisions, is typed over the base's domains by the
   key's sorts; the probe names a regulated predicate, a kind of 1.6 and a typed tuple. A reading reads the shared
   tables of the keys its own document generates, and no other. A situation that fails this step is refused with
   section 7's texts and separates nothing. The decoder checks the whole step. `separates` checks its conditions
   on keys, tables and the probe itself (`situationWF`, 8.3), so a malformed table can never make the other
   side's failure count as a separation (K21). It tests neither the id nor the condition on the base, that it is
   valid over the author's vocabulary: a finite model in Lean gives a table for every predicate name, so that
   validity is not a Boolean check on it. It is the proof the decoder supplies for the base it builds
   (`SeparateReplay.valid`, 8.4) and the hypothesis `valid` of `separates_sound`; on a base that is not valid
   `separates` may answer true, and the answer certifies nothing (8.3, notes).
2. **The witness.** `a`'s document with the base, the shared tables and the decisions is admissible (the
   regenerated base background, the exception and coherence premises, the limitation premises), else
   `distinguishing model violates a generated premise`. The probe has the recorded value there.
3. **The other side.** Let `n` be the number of cells of `b`'s owned tables over the base (per owned key of `b`'s
   document, the number of typed tuples). If `n > 12`: `ResourceLimit: decision assignments`, never a verdict. Else
   for each of the `2ⁿ` assignments: if `b`'s document with the base, the shared tables and the assignment is
   admissible and the probe has the recorded value, the pair is not separated by `σ`.
4. The pair is separated by `σ` when 2 holds and no assignment of 3 reaches the value. Otherwise
   `distinguishing model does not separate readings`, today's text.

Shared tables are never enumerated: were the tables of a dozen fixed default rules free, the bound would be
exceeded on every set (plan 2.4). A probe never names a rule, so two candidates that differ only in a rule name are
not separated by any situation (F22, K3). The witness matters: on K1 the situation separates with the default
reading as witness and does not with the strict one.

### 4.6 Findings

After a set is admitted, per pair: `SeparatedByDecisionOnly: <set>: <i>, <j> (not certified)` when the criterion of
1.7 holds, `<i>` the strict twin; `SeparatedByActOnly: <set>: <i>, <j>` when its criterion holds. Neither changes admission, a
status or a verdict.

### 4.7 Labels and couplings

`labels` is allowed on every candidate and `couplings` on every set whose candidates all carry the axis, on every
chain. The checks and texts are rights 3.3's and 6.2's, unchanged (`CouplingLabelMissing`, `CouplingUnsatisfiable`,
`ResourceLimit: couplings`); only the requirement of `rights@0` is dropped under `readings@1`. A coupling adds no
premise in S1: `coupling:<id>` premises are S2's `Choice_D`.

### 4.8 Statuses and verdicts

S1 defines no status and no status rule. Rights 7.2's rule ("READINGS only when every candidate has elaborated
lines and a distinguishing situation") is applied with *elaborated* covering every content of 1.2 and
*distinguishing situation* meaning a situation checked as 4.5 says; on the other chains a unit with an open set
keeps the status W2 gives it today. A query or report that depends on a content-bearing set is UNKNOWN with the
reason `superposition pending`, on every chain; the rights report keeps its text `per-choice rights elaboration
pending`. A formula-only document keeps W2's ALL, NONE and SOME route verbatim.

### 4.9 Conservativity

- `readings@1` off: nothing of this specification is reachable. Identities, statuses and verdicts are
  byte-identical (plan F20).
- `readings@1` on, no content-bearing set: `one D s i` is the fixed document for every candidate
  (`one_formula_only`), every fixed unit is free, and the sets validate by today's code with today's `models`.
- A content-bearing set whose candidates own no key: the check is the comparison of outcomes and selected rules
  that today's right sets use, on each candidate's document (`separation_conservative`).
- No frozen file, canonical byte, identity or theorem statement changes. The plan's lemma that a default rule
  alone differs from its strict twin only where the exception holds is `force_agrees_off_exception`.

## 5. What a checked separation certifies, and what S1 does not add

1. A checked separation proves, of the shown base and the shown shared tables, that the witnessing reading has a
   completion in which the probe has the recorded value and that the other reading has none (`separates_sound`,
   8.3). `Separated` follows from it. It proves no more (composition.md 2.1, "What E19 to E21 may state").
2. It is about the documents `one D s a` and `one D s b`: the fixed units that depend on no other open sentence,
   and the candidate. It does not say that the two readings differ under every choice of the other open sentences,
   or under any: that is S2's per-choice semantics.
3. It does not say the set is exhaustive, that either reading is the author's, or that a coupling or narrowing is
   right.
4. S1 adds no base premise: no slot, no label, nothing in `conditional_on`, no entry of composition.md 6's slot
   column. The premises a completion must satisfy are the lower route's own (`BaseAdmissibleR`, which is
   `BaseAdmissibleP` at `Lim_D` by `rights_is_slot`).
5. A finding is a report line. `SeparatedByDecisionOnly` would claim exactly `decision_only_sound`'s statement;
   while that theorem is unproved it claims nothing and is reported as not certified (1.7).

## 6. The report

Per content-bearing set: the candidates with content and the pending ones; per pair, the situation id, the probe's
form and the wording of 2.3; the findings, those not certified listed apart (1.7); the chain's static findings per
candidate with their reading. Residual lines: `separations` (pairs by probe form: outcome, selects, holds),
`findings` (the two of 1.7, counted; `readings_findings` in the coverage residual), `pending_candidates`, and on
every chain rights 7.2's `couplings` line. The report says which checker covers what (`checked_by`): Lean the
admission, the separations and the findings; Python W2's structure, couplings and narrowings (4.1, S1 limitation).
Rust's untrusted replay was deleted in lean-first batch 3 (10). Python's implementation is `ve/readings_route.py` (`report`,
`Wording`). `conditional_on` and the status text are
the lower route's, unchanged (composition.md 7). Every English line about a separation is one of 2.3.

## 7. Diagnostics

In the order of 4.1. Texts in the first table are composition.md 8's or today's, verbatim.

| Text | When | Kind |
|---|---|---|
| `InvalidInput: name <n> begins with ve__` / `begins with rd-` | 1.8 | error |
| `DuplicateDeclaration: <name> in reading sets <s> and <t>` | 4.3 | error |
| `DuplicateDeclaration: rule <name>` / `right <name>` / `limitation <name>` / `bar` | 4.3: two fixed units declare one name (the chain's text) | error |
| `ReadingInterface: <set>: <name>` | 4.2 | error |
| `distinguishing model id does not match model` | a situation's id is not its digest (today's text) | error |
| `distinguishing model violates a generated premise` | 4.5 step 2 (today's text) | error |
| `ResourceLimit: decision assignments` | 4.5 step 3 | error, never a verdict |
| `distinguishing model does not separate readings` | 4.5 step 4 (today's text) | error |
| `SeparatedByActOnly: <set>: <i>, <j>` / `SeparatedByDecisionOnly: <set>: <i>, <j> (not certified)` | 4.6 | finding (the second not certified, 1.7) |

New in S1:

| Text | When | Kind |
|---|---|---|
| `UnsupportedProfile: readings@1 content with norm-defaults@0 is not implemented` | 1.1 | error |
| `UnsupportedProfile: reading <set>:<id> of kind <k> requires <profile>` | a content whose `Content.needs` is not in the list | error |
| `UnsupportedProfile: readings@1 bar candidate content is not implemented` | a bar candidate with content (13.8) | error |
| `UnsupportedProfile: readings@1 fixed unit <u> depends on reading sets <s> and <t>` | 4.2: a fixed unit attached to more than one set | error |
| `InvalidInput: reading <set>:<id> has kind <k> and content of kind <k′>` | 3 | error |
| `InvalidInput: invalid situation <id>` | 4.5 step 1: a witness that is not one of the pair's two readings, shape or typing, a base that lists a predicate outside the author's base vocabulary, a key listed twice, a `fixed` key that neither reading's document generates, a `decisions` key that the witness's document does not generate | error |
| `InvalidInput: situation <id> decides <key>, which reading <r> does not own` | a `decisions` key that the witness does not own, or a `fixed` key that one of the two readings owns (it is not shared) | error |
| `InvalidInput: invalid source word span` | `source_word` outside the unit's span | error |
| `InvalidInput: line order lists a line of right <r> twice` | 4.4: the line order of `free D` or of `one D s i` (then with ` under <set>@<v>:<i>`) repeats an entry (DRI ruling 1) | error |
| `UnknownRight: <r>` | 4.4: a line order entry that is no line of a right named `<r>` (the rights decoder's text) | error |
| `<chain diagnostic> under <set>@<v>:<i>` | 4.4 | error, or finding for a chain finding |

`<key>` is written as in 1.5's table: `excepted <r>`, `off <r> <π>`, `outweighs <a> <L> <H>`, `lim <L> <a>`,
`cond <L> <a> <c>`, `aimed <m>`, with ` bearer <b>` after the rule of a fan-out instance. Unchanged: today's
structural texts of `validate_reading_sets`, `validate_couplings` and `validate_narrowings`; every W1, soft, rights
and P0 text; `dispatch`'s texts.

## 8. Lean (S1): definitions and the exact statements to prove

### 8.1 Files

`lean/VE/Readings/Doc.lean` (8.2), `Separate.lean` (8.3), `Lines.lean` (`linesOnce`, its admission text and
`genKeys_nodup`, 8.3, DRI ruling 1), `Wire.lean` and `Run.lean` (8.4), `Examples.lean` (the
`#guard` fixtures of 9.2), the root `lean/ReadingsMain.lean` of the new target `ve_readings_route`, and
`lean/READINGS.md` listing each theorem in plain words. `VE.lean` and `VE/Audit.lean` gain imports and audit
entries; the audit allowlist is unchanged (`propext`, `Classical.choice`, `Quot.sound`). Frozen `Norms/*`,
`SoftNorms/*`, `Rights/*`, `Route/*`, `Discourse/*`, `Compose/*` and all P0 sources are untouched. The namespace
`VE.Readings` is new (`lean/VE/Route/Readings.lean` is `VE.Route`). The blocks are statement schemata: binders shown
once are repeated where a later statement abbreviates them.

### 8.2 `Doc.lean`

```lean
import VE.Compose.Content
import VE.Rights.Route

namespace VE.Readings
open VE.Norms (Regulated Sat tupleVal envAt size)
open VE.SoftNorms (SoftNode SoftDoc soften WellFormedSoft ValueSoft)
open VE.Rights (RightsDoc Bar SourceLine correlate limPremises WellFormedRights sourceLines)
open VE.Compose (Content)
universe u

inductive Chain | norms | soft | rights
  deriving DecidableEq, Repr
def chainOf (ps : List String) : Chain :=
  if ps.contains "rights@0" then .rights else if ps.contains "soft-norms@0" then .soft else .norms

structure Candidate where
  id : String
  /-- `none`: pending, or a candidate S1 does not elaborate (a quantity, a bar, a composite kind). -/
  content : Option Content
  /-- The `cites` of a norm content; `[]` otherwise. -/
  cites : List (String × List String)
  labels : List (String × String)
  deriving DecidableEq, Repr
structure ReadingSet where
  id : String
  unit : String
  version : Nat
  candidates : List Candidate
  deriving DecidableEq, Repr
/-- A unit in source order (1.2). -/
inductive Item
  | fixed (unit : String) (c : Content) (cites : List (String × List String))
  | bar (unit : String) (b : Bar)
  | set (R : ReadingSet)
  deriving DecidableEq, Repr
structure Coupling where
  id : String
  axis : String
  sets : List (String × Nat)
structure Narrowing where
  id : String
  set : String
  version : Nat
  keeps : List String
structure Doc where
  chain : Chain
  /-- E, literals, the soft block, regulated predicates, definitions, the rights block, the source unit ids; no
      rule, right, limitation or bar, and `sourceOrder := some []`. -/
  frame : RightsDoc
  items : List Item
  couplings : List Coupling
  narrowings : List Narrowing

def Doc.sets (D : Doc) : List ReadingSet := D.items.filterMap (fun | .set R => some R | _ => none)
def candidate (D : Doc) (s : String) (i : Nat) : Option Candidate :=
  (D.sets.find? (·.id == s)).bind (·.candidates[i]?)

/-! ## Names (1.3) -/

def nodeUses (N : SoftNode) : List (String × String) := N.over.map (fun n => ("rule", n))
def citeUses (cs : List (String × List String)) : List (String × String) :=
  cs.filterMap (fun kv => if kv.1.startsWith "over:" then some ("rule", kv.1.drop 5)
                          else if kv.1.startsWith "narrows:" then some ("rule", kv.1.drop 8) else none)
def lineUses (S : SourceLine) : List (String × String) :=
  (S.norm.toList ++ S.liberty.toList ++ S.recognition.toList).flatMap nodeUses ++ citeUses S.cites
def uses (c : Content) (cites : List (String × List String)) : List (String × String) :=
  match c with
  | .assertion _ => []
  | .norm N => nodeUses N ++ citeUses cites
  | .right R => R.lines.flatMap lineUses
  | .rightLines r ls => ("right", r) :: ls.flatMap lineUses
  | .limitation L => (L.scope.getD []).map (fun r => ("right", r))

def declaredBy (R : ReadingSet) : List (String × String) :=
  (R.candidates.filterMap (·.content)).flatMap (·.declared)
def interfaceOf (R : ReadingSet) : List (String × String) :=
  (declaredBy R).filter (fun n => R.candidates.all (fun a => (a.content.map (·.declared.contains n)).getD false))
/-- Fixed unit u is attached to set t (1.3): the least such relation. -/
inductive Attached (D : Doc) : String → String → Prop
  | direct {u : String} {c : Content} {cs : List (String × List String)} {t : String}
      (hu : Item.fixed u c cs ∈ D.items) (n : String × String) (hn : n ∈ uses c cs)
      (R : ReadingSet) (hR : R ∈ D.sets) (ht : R.id = t) (hd : n ∈ declaredBy R) : Attached D u t
  | step {u u' : String} {c c' : Content} {cs cs' : List (String × List String)} {t : String}
      (hu : Item.fixed u c cs ∈ D.items) (hu' : Item.fixed u' c' cs' ∈ D.items)
      (n : String × String) (hn : n ∈ uses c cs) (hd : n ∈ c'.declared) (h : Attached D u' t) : Attached D u t
/-- The sets a fixed unit is attached to, computed with fuel `D.items.length`. -/
def attached (D : Doc) (unit : String) : List String
theorem attached_iff (D : Doc) (u t : String) : t ∈ attached D u ↔ Attached D u t

/-! ## A candidate's document (1.4) -/

/-- One unit appended, as `VE.Rights.Wire.addUnit` appends it. -/
def place (X : RightsDoc) (c : Content) (cites : List (String × List String)) : RightsDoc :=
  match c with
  | .assertion _ => X
  | .norm N => { X with soft := { X.soft with T := { X.soft.T with nodes := X.soft.T.nodes ++ [N] } },
                        outsideCites := X.outsideCites ++ (if cites.isEmpty then [] else [(N.name, cites)]) }
  | .right R => { X with rs := X.rs ++ [R],
                         sourceOrder := some (X.sourceOrder.getD [] ++ R.lines.map (R.name, ·)) }
  | .rightLines r ls =>
    { X with rs := X.rs.map (fun R => if R.name == r then { R with lines := R.lines ++ ls } else R),
             sourceOrder := some (X.sourceOrder.getD [] ++ ls.map (r, ·)) }
  | .limitation L => { X with limits := X.limits ++ [L] }
def asserted : Content → List VE.Formula
  | .assertion φ => [φ]
  | _ => []
def build (D : Doc) (keep : String → Bool) (pick : ReadingSet → Option Candidate) : RightsDoc × List VE.Formula :=
  D.items.foldl (fun acc it => match it with
    | .fixed u c cs => if keep u then (place acc.1 c cs, acc.2 ++ asserted c) else acc
    | .bar u b => if keep u then ({ acc.1 with bars := acc.1.bars ++ [b] }, acc.2) else acc
    | .set R => match (pick R).bind (fun a => a.content.map (fun c => (c, a.cites))) with
      | some (c, cs) => (place acc.1 c cs, acc.2 ++ asserted c)
      | none => acc) (D.frame, [])
def free (D : Doc) : RightsDoc × List VE.Formula := build D (fun u => (attached D u).isEmpty) (fun _ => none)
def one (D : Doc) (s : String) (i : Nat) : RightsDoc × List VE.Formula :=
  build D (fun u => (attached D u).all (· == s)) (fun R => if R.id == s then R.candidates[i]? else none)

/-! ## Admission without separation (4.2 to 4.4) -/

def noRights (X : RightsDoc) : Bool :=
  X.rs.isEmpty && X.limits.isEmpty && X.bars.isEmpty && (sourceLines X).isEmpty
def allStrict (X : RightsDoc) : Bool := X.soft.T.nodes.all (fun N => N.mode == .strict && N.alterable.isEmpty)
def chainWF : Chain → RightsDoc → Bool
  | .rights, X => WellFormedRights X
  | .soft, X => noRights X && WellFormedSoft X.soft
  | .norms, X => noRights X && allStrict X && WellFormedSoft X.soft
def sideWF (D : Doc) (X : RightsDoc × List VE.Formula) : Bool :=
  chainWF D.chain X.1 &&
    X.2.all (fun a => a.check (envAt (soften (correlate X.1)) (size (soften (correlate X.1)))) [])
/-- 1.8 on the frame and on every fixed and candidate content. -/
def reservedFree (D : Doc) : Bool
/-- The names a fixed unit or a bar declares; none for a set. -/
def Item.names : Item → List String
  | .fixed _ c _ => c.declared.map (·.2)
  | .bar _ b => [b.name]
  | .set _ => []
/-- 4.3: no name declared by a candidate is declared by a fixed unit or by a candidate of another set, and no two
    fixed units declare one name. -/
def distinctAcrossSets (D : Doc) : Bool
/-- 4.2: every name a fixed unit uses that a set declares is an interface name of that set. -/
def interfaceClosed (D : Doc) : Bool
/-- 4.2: no fixed unit is attached to two sets. Such a unit would be in neither `free D` nor any `one D s i`. -/
def singlyAttached (D : Doc) : Bool
def WellFormedDoc (D : Doc) : Bool :=
  reservedFree D && distinctAcrossSets D && interfaceClosed D && singlyAttached D && sideWF D (free D) &&
  D.sets.all (fun R => (List.range R.candidates.length).all (fun i =>
    (R.candidates[i]?.bind (·.content)).isNone || sideWF D (one D R.id i)))

theorem distinctAcrossSets_spec (D : Doc) : distinctAcrossSets D = true ↔
  (∀ R ∈ D.sets, ∀ n ∈ declaredBy R, ∀ u c cs, Item.fixed u c cs ∈ D.items → ∀ m ∈ c.declared, m.2 ≠ n.2) ∧
  (∀ R ∈ D.sets, ∀ n ∈ declaredBy R, ∀ u b, Item.bar u b ∈ D.items → b.name ≠ n.2) ∧
  (∀ R ∈ D.sets, ∀ R' ∈ D.sets, R.id ≠ R'.id → ∀ n ∈ declaredBy R, ∀ m ∈ declaredBy R', m.2 ≠ n.2) ∧
  D.items.Pairwise (fun x y => ∀ n ∈ x.names, n ∉ y.names)
theorem interfaceClosed_spec (D : Doc) : interfaceClosed D = true ↔
  ∀ u c cs, Item.fixed u c cs ∈ D.items → ∀ n ∈ uses c cs, ∀ R ∈ D.sets, n ∈ declaredBy R → n ∈ interfaceOf R
theorem singlyAttached_spec (D : Doc) : singlyAttached D = true ↔
  ∀ u t t', Attached D u t → Attached D u t' → t = t'

/-- Without rights content the rights elaboration is the soft document itself. -/
theorem correlate_noRights (X : RightsDoc) (h : noRights X = true) : correlate X = X.soft ∧ limPremises X = []
theorem chain_soft (c : Chain) (X : RightsDoc) (h : chainWF c X = true) : WellFormedSoft (correlate X) = true
/-- On the norms chain the value is W1's. -/
theorem chain_norms_value (X : RightsDoc) (h : chainWF .norms X = true) (r : Regulated)
    (hr : r ∈ X.soft.T.regulated) (S : VE.Structure.{u}) (vs : List S.Carrier) :
  ValueSoft (correlate X) r S vs = VE.Norms.Value X.soft.base.T r S vs

/-- Identity when unused (composition.md 4.1 rule 5): assertion candidates leave the document as it is, and
    without a declaring candidate no fixed unit is attached. -/
theorem one_formula_only (D : Doc)
    (h : ∀ R ∈ D.sets, ∀ a ∈ R.candidates, ∀ c, a.content = some c → ∃ φ, c = .assertion φ) (s : String) (i : Nat) :
  (one D s i).1 = (free D).1 ∧ (free D).1 = (build D (fun _ => true) (fun _ => none)).1
end VE.Readings
```

Notes for the review. `place` is `addUnit`'s fold step on decoded units; a `rightLines` whose right is absent
leaves `rs` as it is and records the lines in `sourceOrder`, so `WellFormedRights` answers `UnknownRight: <r>` as
the decoder does today. When the right comes later in source order, `WellFormedRights` does not see it (it reads the
rights' own lines, and the order then holds a line the right lacks); the line-order check of 4.4 answers
`UnknownRight: <r>` there, as `addUnit` does. `chain_norms_value` is `soften_faithful` with `soften_hard_identity`, both existing.
`chainWF` asks `WellFormedSoft` on the norms chain as well (13.6). `singlyAttached` is what makes `free D` and the
documents `one D s i` cover every fixed unit: a free unit is in all of them, a unit attached to `s` alone is in
every `one D s i` (and every candidate of `s` has content, or closure would have failed), and no unit is left in
none. The last conjunct of `distinctAcrossSets_spec` is 4.3's check on fixed units: it compares two different
items, so it says nothing of the names inside one unit, which the chain checks where the unit sits.

### 8.3 `Separate.lean`

```lean
import VE.Readings.Doc

namespace VE.Readings
open VE.Norms (Regulated Sat tupleVal envAt size conflict outcomeBase)
open VE.SoftNorms (SoftNode SoftDoc soften WellFormedSoft ValueSoft SelectsSoftD canon circ selects' exceptedF)
open VE.Rights (RightsDoc correlate BaseAdmissibleR backgroundValidR linesOf nodeOf)
open VE.Compose (Content)
universe u

/-! ## Source keys (1.5) -/

inductive GenKey
  | excepted (rule : String) (bearer : Option String)
  | off (rule : String) (bearer : Option String) (party : String)
  | outweighs (act lower higher : String)
  | lim (limitation act : String)
  | cond (limitation act condition : String)
  | aimed (pred : String)
  deriving DecidableEq, Repr
/-- The generated base predicates of X's elaboration: source key, name in X, argument sorts, in the order
    `VE.SoftNorms.decisions (correlate X) ++ VE.Rights.genDecls X`. -/
def genKeys (X : RightsDoc) : List (GenKey × String × List String)
theorem genKeys_names (X : RightsDoc) :
  (genKeys X).map (fun g => (g.2.1, g.2.2)) = VE.SoftNorms.decisions (correlate X) ++ VE.Rights.genDecls X
/-- The line order lists each line of each right once, and only lines of its right (DRI ruling 1; in
    `Lines.lean`, with the admission text `lineOrderText` of 4.4 and `linesOnce_of_text`). -/
def linesOnce (X : RightsDoc) : Bool :=
  decide (VE.Rights.sourceLines X).Nodup &&
  (VE.Rights.sourceLines X).all (fun e => X.rs.any (fun R => R.name == e.1 && R.lines.contains e.2))
theorem genKeys_nodup (c : Chain) (X : RightsDoc) (h : chainWF c X = true) (hl : linesOnce X = true) :
  ((genKeys X).map (·.1)).Nodup

/-- The rule or limitation name a key carries; `none` for a key over environment names only. -/
def GenKey.source : GenKey → Option (String × String)
  | .excepted r _ => some ("rule", r)
  | .off r _ _ => some ("rule", r)
  | .lim L _ => some ("limitation", L)
  | .cond L _ _ => some ("limitation", L)
  | .outweighs _ _ _ => none
  | .aimed _ => none
def owned (D : Doc) (s : String) (i : Nat) (k : GenKey) : Bool :=
  match (candidate D s i).bind (·.content), k.source with
  | some c, some n => c.declared.contains n
  | _, _ => false
def ownedKeys (D : Doc) (s : String) (i : Nat) : List GenKey :=
  ((genKeys (one D s i).1).map (·.1)).filter (owned D s i)

/-! ## Completions and probes (1.6) -/

abbrev Tables (α : Type u) := GenKey → List α → Prop
/-- B with every generated predicate of X read from its key's table. -/
def withTables (X : RightsDoc) (B : VE.Structure.{u}) (G : Tables B.Carrier) : VE.Structure.{u} :=
  { B with relation := fun p vs => match (genKeys X).find? (·.2.1 == p) with
      | some g => G g.1 vs
      | none => B.relation p vs }
/-- Every regulated and defined predicate at its meaning over the base. -/
def expand (X : RightsDoc) (B : VE.Structure.{u}) : VE.Structure.{u} := canon (soften (correlate X)) B

inductive Probe (α : Type u)
  | outcome (p : String) (vs : List α)
  | selects (kind p : String) (vs : List α)
  | holds
  deriving DecidableEq
def kindWord : VE.Rights.IKind → String
  | .claim => "claim" | .liberty => "liberty" | .immunity => "immunity"
  | .powerLiberty => "powerLiberty" | .powerRecognition => "powerRecognition"
/-- The nodes of the kind on p, as they sit in `correlate X`. A probe never names a rule. -/
def selectable (X : RightsDoc) (kind p : String) : List SoftNode :=
  if kind == "norm" then X.soft.T.nodes.filter (·.pred == p)
  else ((linesOf X).filter (fun RN => kindWord RN.2.ikind == kind && RN.2.node.pred == p)).map
    (fun RN => nodeOf X RN.2)

/-- Probe q has value v in the expansion of B, for the document X with assertions A. -/
def Observes (X : RightsDoc) (A : List VE.Formula) (B : VE.Structure.{u}) : Probe B.Carrier → Bool → Prop
  | .outcome p vs, v => ∃ r ∈ (correlate X).T.regulated, r.name = p ∧ VE.TupleTyped B r.sorts vs ∧
      ValueSoft (correlate X) r (expand X B) vs = some v
  | .selects k p vs, v => VE.TupleTyped B (VE.SoftNorms.sortsOf (correlate X) p) vs ∧
      ((∃ N ∈ selectable X k p,
          SelectsSoftD (correlate X) (expand X B) (tupleVal vs) (VE.SoftNorms.fuel (correlate X)) N) ↔ v = true)
  | .holds, v => ((∀ a ∈ A, a.denote (expand X B) []) ↔ v = true)

/-- The author's base vocabulary. -/
def authorEnv (D : Doc) : VE.Environment := envAt D.frame.soft.base 0
/-- B is admissible over the author's base vocabulary, and some completion of candidate i over B and shared
    tables F gives q the value v. Tables of keys the candidate does not own are F's and are not reassigned.
    Without the first conjunct a base could carry a true tuple on a predicate that one reading's document
    generates and the other's does not declare (K2b). -/
def Achieves (D : Doc) (s : String) (i : Nat) (B : VE.Structure.{u}) (F : Tables B.Carrier)
    (q : Probe B.Carrier) (v : Bool) : Prop :=
  B.Admissible (authorEnv D) ∧
  ∃ G : Tables B.Carrier, (∀ k, owned D s i k = false → ∀ vs, G k vs ↔ F k vs) ∧
    BaseAdmissibleR (one D s i).1 (withTables (one D s i).1 B G) ∧
    Observes (one D s i).1 (one D s i).2 (withTables (one D s i).1 B G) q v
def Separated (D : Doc) (s : String) (i j : Nat) : Prop :=
  ∃ (B : VE.Structure.{u}) (F : Tables B.Carrier) (q : Probe B.Carrier) (v : Bool),
    (Achieves D s i B F q v ∧ ¬ Achieves D s j B F q v) ∨ (Achieves D s j B F q v ∧ ¬ Achieves D s i B F q v)

/-! ## The executable check (4.5) -/

structure Situation (α : Type u) where
  base : VE.FiniteModel α
  fixed : List (GenKey × List (List α))
  decisions : List (GenKey × List (List α))
  probe : Probe α
  value : Bool
/-- M with, for every generated predicate of X, the table of its key in T (`[]` when absent). -/
def tablesModel {α : Type u} (X : RightsDoc) (M : VE.FiniteModel α) (T : List (GenKey × List (List α))) :
  VE.FiniteModel α
/-- Every table of T is on a key of X and holds tuples typed over M's domains by the key's sorts. -/
def tablesTyped {α : Type u} [DecidableEq α] (X : RightsDoc) (M : VE.FiniteModel α)
  (T : List (GenKey × List (List α))) : Bool
/-- The probe names a regulated predicate, a kind of 1.6 and a tuple typed over M's domains. -/
def probeTyped {α : Type u} [DecidableEq α] (X : RightsDoc) (M : VE.FiniteModel α) (q : Probe α) : Bool

def observe {α : Type u} [DecidableEq α] (X : RightsDoc) (A : List VE.Formula) (M : VE.FiniteModel α) :
    Probe α → Option Bool
  | .outcome p vs =>
    match (correlate X).T.regulated.find? (·.name == p) with
    | some r => if (conflict (soften (correlate X)) r).eval M (tupleVal vs) then none
                else some ((outcomeBase (soften (correlate X)) p).eval M (tupleVal vs))
    | none => none
  | .selects k p vs => some ((selectable X k p).any (fun N =>
      (circ (correlate X) (selects' (correlate X) N)).eval M (tupleVal vs)))
  | .holds => some (A.all (fun a => (circ (correlate X) a).eval M []))

def sideValid {α : Type u} [DecidableEq α] (D : Doc) (s : String) (i : Nat) (M : VE.FiniteModel α)
    (T : List (GenKey × List (List α))) : Bool :=
  tablesTyped (one D s i).1 M T && backgroundValidR (one D s i).1 (tablesModel (one D s i).1 M T)
def sideValue {α : Type u} [DecidableEq α] (D : Doc) (s : String) (i : Nat) (M : VE.FiniteModel α)
    (T : List (GenKey × List (List α))) (q : Probe α) : Option Bool :=
  observe (one D s i).1 (one D s i).2 (tablesModel (one D s i).1 M T) q
/-- The cells of candidate j's owned tables over M: per owned key, the number of typed tuples. -/
def cells {α : Type u} (D : Doc) (s : String) (j : Nat) (M : VE.FiniteModel α) : Nat
/-- Every assignment of tables to candidate j's owned keys over M's typed tuples: `2 ^ cells` of them. -/
def assignments {α : Type u} (D : Doc) (s : String) (j : Nat) (M : VE.FiniteModel α) :
  List (List (GenKey × List (List α)))
def maxCells : Nat := 12
/-- The tables of T on keys that candidate i's document generates: a reading reads no other. -/
def tablesFor {α : Type u} (D : Doc) (s : String) (i : Nat) (T : List (GenKey × List (List α))) :
    List (GenKey × List (List α)) :=
  T.filter (fun t => (genKeys (one D s i).1).any (·.1 == t.1))
/-- The tables of T as relations: the table of key k, empty when T has none. -/
def tablesOf {α : Type u} (T : List (GenKey × List (List α))) : Tables α :=
  fun k vs => ∃ t ∈ T, t.1 = k ∧ vs ∈ t.2
/-- 4.5 step 1 without the id and without the base's validity over the author's vocabulary (the hypothesis
    `valid` of `separates_sound`), i the witness: no key listed twice; every shared key owned by neither reading
    and generated in i's or in j's document; every decision key owned by i and generated in i's document; the
    tables each reading reads typed over the base; the probe typed. -/
def situationWF {α : Type u} [DecidableEq α] (D : Doc) (s : String) (i j : Nat) (σ : Situation α) : Bool :=
  decide (((σ.fixed ++ σ.decisions).map (·.1)).Nodup) &&
  σ.fixed.all (fun t => !owned D s i t.1 && !owned D s j t.1 &&
    ((genKeys (one D s i).1).any (·.1 == t.1) || (genKeys (one D s j).1).any (·.1 == t.1))) &&
  σ.decisions.all (fun t => owned D s i t.1 && (genKeys (one D s i).1).any (·.1 == t.1)) &&
  tablesTyped (one D s i).1 σ.base (tablesFor D s i (σ.fixed ++ σ.decisions)) &&
  tablesTyped (one D s j).1 σ.base (tablesFor D s j σ.fixed) &&
  probeTyped (one D s i).1 σ.base σ.probe

/-- i is the witness. False on a situation that fails `situationWF`, and when the bound is exceeded. It does not
    test whether the base is valid over the author's vocabulary: `separates_sound` takes that as `valid`. -/
def separates {α : Type u} [DecidableEq α] (D : Doc) (s : String) (i j : Nat) (σ : Situation α) : Bool :=
  situationWF D s i j σ &&
  sideValid D s i σ.base (tablesFor D s i (σ.fixed ++ σ.decisions)) &&
  sideValue D s i σ.base (tablesFor D s i (σ.fixed ++ σ.decisions)) σ.probe == some σ.value &&
  decide (cells D s j σ.base ≤ maxCells) &&
  (assignments D s j σ.base).all (fun G =>
    !(sideValid D s j σ.base (tablesFor D s j σ.fixed ++ G) &&
      sideValue D s j σ.base (tablesFor D s j σ.fixed ++ G) σ.probe == some σ.value))

/-- The finite evaluation is the semantics, on an admissible side and a typed probe. -/
theorem observe_sound {α : Type u} [DecidableEq α] (c : Chain) (X : RightsDoc) (A : List VE.Formula)
    (h : chainWF c X = true)
    (hA : ∀ a ∈ A, a.WellFormed (envAt (soften (correlate X)) (size (soften (correlate X)))) [])
    (M : VE.FiniteModel α) (valid : M.Valid (envAt (soften (correlate X)) 0))
    (hb : backgroundValidR X M = true) (q : Probe α) (hq : probeTyped X M q = true) (v : Bool) :
  observe X A M q = some v ↔ Observes X A M.asStructure q v

theorem separates_sound {α : Type u} [DecidableEq α] (D : Doc) (hD : WellFormedDoc D = true) (s : String)
    (i j : Nat) (hi : (candidate D s i).bind (·.content) ≠ none) (hj : (candidate D s j).bind (·.content) ≠ none)
    (σ : Situation α) (valid : σ.base.Valid (authorEnv D)) (h : separates D s i j σ = true) :
  Achieves D s i σ.base.asStructure (tablesOf σ.fixed) σ.probe σ.value ∧
    ¬ Achieves D s j σ.base.asStructure (tablesOf σ.fixed) σ.probe σ.value
/-- The corollary: a checked separation proves `Separated`. -/
theorem separates_separated {α : Type u} [DecidableEq α] (D : Doc) (hD : WellFormedDoc D = true) (s : String)
    (i j : Nat) (hi : (candidate D s i).bind (·.content) ≠ none) (hj : (candidate D s j).bind (·.content) ≠ none)
    (σ : Situation α) (valid : σ.base.Valid (authorEnv D)) (h : separates D s i j σ = true) :
  Separated.{u} D s i j

/-! ## Conservativity (4.9) -/

/-- Every outcome probe and every selects probe on M: regulated predicates of the frame, the six kinds, typed
    tuples, in canonical order. -/
def probesOf {α : Type u} (D : Doc) (M : VE.FiniteModel α) : List (Probe α)
def observeAll {α : Type u} [DecidableEq α] (D : Doc) (s : String) (i : Nat) (M : VE.FiniteModel α)
    (F : List (GenKey × List (List α))) : List (Option Bool) :=
  (probesOf D M).map (sideValue D s i M (tablesFor D s i F))
/-- Neither side owns a key, and F is a well-formed list of shared tables (4.5 step 1; its typing is in `hvi` and
    `hvj`): some probe separates exactly when the two observations differ. -/
theorem separation_conservative {α : Type u} [DecidableEq α] (D : Doc) (s : String) (i j : Nat)
    (M : VE.FiniteModel α) (F : List (GenKey × List (List α)))
    (hi : ownedKeys D s i = []) (hj : ownedKeys D s j = [])
    (hF : ∀ t ∈ F, owned D s i t.1 = false ∧ owned D s j t.1 = false ∧
      ((genKeys (one D s i).1).any (·.1 == t.1) || (genKeys (one D s j).1).any (·.1 == t.1)) = true)
    (hu : (F.map (·.1)).Nodup)
    (hvi : sideValid D s i M (tablesFor D s i F) = true) (hvj : sideValid D s j M (tablesFor D s j F) = true) :
  (∃ q ∈ probesOf D M, ∃ v, separates D s i j ⟨M, F, [], q, v⟩ = true ∨ separates D s j i ⟨M, F, [], q, v⟩ = true) ↔
    observeAll D s i M F ≠ observeAll D s j M F

/-! ## Force (1.7) -/

def strictOf (N : SoftNode) : SoftNode := { N with mode := .strict, exception := none }
def strictTwin (X : SoftDoc) (N : SoftNode) : SoftDoc :=
  { X with T := { X.T with nodes := X.T.nodes.map (fun M => if M.name == N.name then strictOf M else M) } }
/-- The force axis is real exactly where the exception can apply: a default rule alone and its strict twin agree
    wherever the rule's exception does not hold. -/
theorem force_agrees_off_exception (X : SoftDoc) (h : WellFormedSoft X = true) (N : SoftNode)
    (hN : X.T.nodes = [N]) (hd : N.mode = .default) (ha : N.alterable = []) (r : Regulated)
    (hr : r ∈ X.T.regulated) (S : VE.Structure.{u}) (vs : List S.Carrier)
    (he : ¬ (exceptedF X N).denote S (tupleVal vs)) :
  ValueSoft X r S vs = ValueSoft (strictTwin X N) r S vs

/-- The strict and the default rule of a pair of force twins (1.7), strict first; `none` otherwise. -/
def forceTwins (c c' : Content) : Option (SoftNode × SoftNode)
/-- The criterion of 1.7 with i the strict twin: the default twin's exception key. -/
def decisionOnly (D : Doc) (s : String) (i j : Nat) : Option GenKey
theorem decisionOnly_spec (D : Doc) (s : String) (i j : Nat) (k : GenKey) (h : decisionOnly D s i j = some k) :
  ∃ ci cj Ns Nd, (candidate D s i).bind (·.content) = some ci ∧ (candidate D s j).bind (·.content) = some cj ∧
    forceTwins ci cj = some (Ns, Nd) ∧ k = .excepted Nd.name none ∧
    (∀ e, Nd.exception = some e → e.sufficient = []) ∧
    ∀ M ∈ (correlate (one D s j).1).T.nodes,
      VE.SoftNorms.act (correlate (one D s j).1) M = VE.SoftNorms.act (correlate (one D s j).1) Nd → M.name = Nd.name
/-- Achieves, with the table of k₀ empty. -/
def AchievesQuiet (D : Doc) (s : String) (j : Nat) (k₀ : GenKey) (B : VE.Structure.{u}) (F : Tables B.Carrier)
    (q : Probe B.Carrier) (v : Bool) : Prop :=
  B.Admissible (authorEnv D) ∧
  ∃ G : Tables B.Carrier, (∀ k, owned D s j k = false → ∀ vs, G k vs ↔ F k vs) ∧ (∀ vs, ¬ G k₀ vs) ∧
    BaseAdmissibleR (one D s j).1 (withTables (one D s j).1 B G) ∧
    Observes (one D s j).1 (one D s j).2 (withTables (one D s j).1 B G) q v
/-- With the default twin's exception table empty the two readings reach the same probe values on every base:
    every separation of the pair uses that table. -/
theorem decision_only_sound (D : Doc) (hD : WellFormedDoc D = true) (s : String) (i j : Nat) (k₀ : GenKey)
    (h : decisionOnly D s i j = some k₀) (B : VE.Structure.{u}) (F : Tables B.Carrier) (q : Probe B.Carrier)
    (v : Bool) :
  Achieves D s i B F q v ↔ AchievesQuiet D s j k₀ B F q v

/-- The two act keys of 1.7's `SeparatedByActOnly`; `none` otherwise. -/
def actOnly (D : Doc) (s : String) (i j : Nat) : Option (String × String)
end VE.Readings
```

Notes for the review. `genKeys_nodup` as first approved, without `hl`, was false (DRI ruling 1): `WellFormedRights`
accepts an order that lists one default fan-out line twice (`Examples.lean`, `twiceListed`), and an order that lists
a line no right has (`orderOnly`, no entry repeated); two pairs of keys then repeat. The hypothesis is the admission
check of 4.4, which refuses both. `Achieves` uses `BaseAdmissibleR`, which is `BaseAdmissibleP (correlate X) (limPremises X)`
by `rights_is_slot`; on the soft and norms chains `limPremises` is empty and `correlate X` is the soft document
(`correlate_noRights`). `withTables` and `expand` keep the carrier, so a `Probe B.Carrier` is a probe of both.
`observe_sound` is `conflict_canon`, `outcome_canon`, `circ_canon` and `selectsPrime_denote`
(`lean/VE/SoftNorms/Coherence.lean`) under `chain_soft`. `Achieves` and `AchievesQuiet` ask that the base be
admissible over the author's vocabulary. `withTables` passes `B.relation` through on every name the document does
not generate, and `Structure.Admissible` refuses a true tuple on an undeclared predicate; so without the conjunct
a base carrying a tuple on one reading's generated predicate would be admissible for that reading alone,
`Separated` would hold of K2's pair, and `decision_only_sound` would be false on K1 (K2b). In `separates_sound`
the hypothesis `valid` supplies that conjunct (`FiniteModel.Valid` is `asStructure.Admissible`), and it is the
author's vocabulary only: validity of each side's model over its own base vocabulary follows from it, from
`tablesTyped` and from the freshness of generated names that `chainWF` checks. `valid` is a hypothesis and not a
conjunct of `situationWF`: `FiniteModel.relations` gives a table for every predicate name, so validity over an
environment is not a Boolean check on a `FiniteModel`, and the decoder proves it of the base it builds from the
listed relations, as the existing model decoder does (`decodeModel_valid`, `lean/VE/ModelProofs.lean`).
`separates` therefore enforces step 1 of 4.5 without the id and without that validity. Nothing in `situationWF`,
`sideValid` or `observe` reads a table on a predicate that neither reading's document declares, so K1's σ with one
true tuple on such a predicate added to its base is answered true as K1's σ is, although `Achieves` is false of
both readings on that base. `separates = true` certifies a separation only together with `valid`, which is what
`separates_sound` states and what `SeparateReplay` carries. The conclusion is about the shown
base and the shown shared tables (`tablesOf σ.fixed`), which is what composition.md 2.1 says a checked separation
proves: the witness reaches the recorded value there and the other reading cannot. `Separated` is its corollary
`separates_separated`. `situationWF` makes both sides read one list of well-typed shared tables, each key once:
without it an ill-typed table on a key that only the other reading's document generates would fail every
`sideValid` of that side, and `separates` would answer true for a malformed situation (K21). The other side's
negation ranges over all tables: admissibility forces every table into the typed tuples of the finite domains,
which is what `assignments` enumerates. `separation_conservative` takes step 1 for its list `F` as hypotheses,
since `separates` now refuses a list that fails it. `force_agrees_off_exception` is deliberately about a rule
alone (plan S1); E22 and E23 say what else differs in a document, and no theorem claims otherwise.
`decision_only_sound` is the only statement behind E15. It is not proved yet, so S1 shows E25 instead and
reports the finding as not certified (1.7).

### 8.4 `Wire.lean`, `Run.lean`

The decoder of a content is the existing unit-content decoder of the chain's head (composition.md 9.4);
`Wire.lean` adds the decoder of a document's items, of a situation and of a key, and the regenerated answer.

```lean
namespace VE.Readings.Wire
structure SeparateReplay where
  D : Doc
  wf : WellFormedDoc D = true
  set : String
  witness : Nat
  other : Nat
  hw : (candidate D set witness).bind (·.content) ≠ none
  ho : (candidate D set other).bind (·.content) ≠ none
  σ : Situation VE.Bridge.Entity
  /-- 4.5 step 1, the base: valid over the author's vocabulary. `separates` does not test it. -/
  valid : σ.base.Valid (authorEnv D)
  /-- 4.5 step 1, the keys, the tables and the probe: the decoder refuses a malformed situation with section 7's
      texts. -/
  shape : situationWF D set witness other σ = true
def replaySeparate (j : Lean.Json) : Except String SeparateReplay
theorem readings_wire_separate_sound (j : Lean.Json) (r : SeparateReplay) (h : replaySeparate j = .ok r)
    (hs : separates r.D r.set r.witness r.other r.σ = true) :
  Achieves r.D r.set r.witness r.σ.base.asStructure (tablesOf r.σ.fixed) r.σ.probe r.σ.value ∧
    ¬ Achieves r.D r.set r.other r.σ.base.asStructure (tablesOf r.σ.fixed) r.σ.probe r.σ.value
end VE.Readings.Wire
```

`Separated r.D r.set r.witness r.other` follows by `separates_separated`. The decoder checks 4.5 step 1 before it
answers: a situation that fails it is `InvalidInput` with section 7's text, on both case kinds below, and is never
answered `separated: false`. It checks the whole step: the id, the base's validity (the field `valid`) and
`situationWF` (the field `shape`). `separates` by itself tests only the last (4.5), so the theorem needs `r.valid`
as well as `hs`.

Case kinds on `ve_readings_route`:

- `readings-validate`: the environment and the document. The answer is regenerated and compared byte for byte
  with Python's: per content-bearing set and candidate, the chain's document hash of `one D s i`, its owned and
  shared keys with their generated names, and its chain findings; per pair, `separated` for the recorded
  situation; the findings of 4.6; or the first diagnostic of 4.1.
- `readings-separate`: one pair, one situation. The answer is `separated: true | false`, the witness's value, and
  for the other side whether it has an admissible completion and, when it owns no key, its one value (the facts
  E19's four cases need); for a situation that fails 4.5 step 1, the diagnostic.
- Every other kind: `readings@1` is stripped and the case is run by the lower route's logic unchanged.

S1 has no kind named `-elaborate`: `readings-validate`'s answer is its regenerated output, and S2 adds
`readings-elaborate` for `sup D`.

**Lean-first batch 3 (2026-10-04, docs/LEAN-FIRST-PLAN.md rule 2).** The answer is Lean's alone: `ve/readings_route.py`
relays the row (or raises Lean's diagnostic with its text) after checking it against the schema of `Run.lean`'s
encoders and binding it to the request (its sets, candidates, pairs and their situations, and the producer's
invariants: `ve/readings_route.py` `_check`; anything else is `CheckerUnavailable`), and the
byte-for-byte comparison with Python's regeneration (`readings_s1.answer`), the rights route calls it made for the
chain findings, and Rust's untrusted replay (`readings-evaluate`) are deleted. The batch's evidence and the inputs
whose answer changed are in `docs/lean-first/b3/DELTA.md`.

### 8.5 What is not claimed

No theorem about `sup`, a choice atom, a complete choice or any verdict across readings. No claim that
`Separated` holds under any choice of the other open sets (5.2). No completeness: `separates = false` does not say
the pair is inseparable, and no finding is emitted from a failed search. No claim that `decisionOnly` is
necessary, and, until `decision_only_sound` is proved, none that it is sufficient (1.7). No theorem about the English of section 2. No claim about `norm-defaults@0` documents. Python's search
is not verified; Lean checks what it finds.

## 9. Acceptance fixtures for item 1

Review protocol as composition.md 10: each reviewer derives the expectation from sections 1, 4 and 8 before
reading the expected column; a builder who finds one wrong reports it against this section instead of changing the
fixture.

### 9.1 The plan's fixtures (S1's share, composition.md 10.5)

Spans are UTF-8 byte offsets into the pinned sources (plan section 5). "Today" is the verdict at `2205be39`.

| # | Unit | Input | Expected in S1 | Left to |
|---|---|---|---|---|
| F1 | C `u0156.s03` [95093, 95193) | set {strict, default} of rule `no-system-prompt-deception` on `system_prompt_deception_avoidance_required(claude_instance, user)`; situation: one instance, one user; witness default; decision: excepted at that pair; probe: the outcome at that pair; value false | `separates = true`: the default reading reaches "not required"; the strict reading owns no key and gives "required". With the strict reading as witness and value true, `separates = false`. `SeparatedByDecisionOnly` exactly if the rule is alone on its act in the document: the rerun reports it, this fixture does not assert it. Today: "relations must contain exactly the base predicates" | — |
| F2 | C `u0165.s03` [101609, 101698) with narrowing `narrow-u0165-s03` | the set of F1's shape plus the narrowing | the set is admitted with the narrowing recorded, and both candidates stay candidates; removing the narrowing changes no identity of the set and no separation result | `Choice_D`'s `narrowing:` premise: S2a |
| F3 | C main document, 14 force sets | `readings-validate` | all 14 sets admitted in the document with their stored situations (`readings/separating-situations.json`, each re-expressed as one situation with the default reading as witness); document verdicts UNKNOWN, `superposition pending` | conflict and premise status: S2a |
| F4 | U `u017` [2179, 2244) | `rs_u017` v2 {strict, default} as norm contents | the set is admitted in the document with one situation; the two companion files are no longer needed for separation | "verdicts equal the two companions'": S2 |
| F5 | U `u091` [8275, 8476) Art. 25(1) | right candidates {strict, default} of the claim, labels `force` | separated where the exception applies, limitation 29's tables shared and empty; unit READINGS; under the default candidate the uncited exception's `UnlicensedLimitation` finding with ` under rs_u091@<v>:<i>`, under the strict one none. Today: UNFORMALISED, `force_variants_in_one_reading_set` | — |
| F6 | U coupling `c-force` over F5's set and the Art. 22 to 27 sets, citing `u013a` | `couplings` on `force` | the coupling is admitted over norm and right candidates alike; a set with an unlabelled candidate is `CouplingLabelMissing: c-force, <set>`; E5 renders "… are read with the same force, because of sentence `<n>`." | `coupling:c-force` on ALL results: S2 |
| F15 | U `u032` Art. 7 as rejected on 2026-09-30 | the set of the two candidates on two predicates | admitted with `SeparatedByActOnly` and E16 naming both act phrases | — |
| F19 | synthetic twin of F1 | default candidate whose exception has an unsatisfiable necessary condition | set rejected: K2 | — |
| F20 | U translation `document_id 97f65591…4533`; rights fixtures; discourse fixtures α to ω | `readings@1` off | identities, statuses and verdicts byte-identical | `right-clauses@0`: S3 |
| F22 | synthetic twin of F1 | the same rule under two rule names | `separates = false` throughout: K3 | — |

F8's admission half is 4.2's `ReadingInterface` (K9); its copies are S2b's.

F3 and F4 presuppose that neither pilot document has a fixed unit attached to two sets: 4.2 refuses the whole
document for one such unit. Neither document has been checked for one. The rerun of section 11 reports it before
the build relies on these two fixtures.

### 9.2 Lean and Python fixtures on one small document

`lean/VE/Readings/Examples.lean` as `#guard` lines, and the same cases through `readings-validate` in
`tests/test_readings_s1.py`. Environment K: sorts `agent`, `user`; base predicate `asks(agent, user)`,
verbalisation `{0} asks {1}`; obligations, deny by default, no dual: `avoid_required(agent, user)`, act
`{0} avoid deceiving {1}`, and `help_required(agent, user)`, act `{0} help {1}`. Profiles `norms@0, readings@1,
relational-fol@0, soft-norms@0` unless said. Rules: `S` is the strict rule `no-deception`, `+avoid_required`, guard
`⊤`; `Df` is `S` as a default rule, exception decided by `unstated`, no condition. Set `rs1` on unit `u1` is
{0: `S`, 1: `Df`} unless said. Model `m0`: one agent `a`, one user `u`, `asks` empty. `q0` is the outcome probe on
`avoid_required` at `(a, u)`.

| # | Input | Expected |
|---|---|---|
| K1 | `rs1`; σ = (`m0`, fixed none, witness 1, decisions `excepted no-deception` = {(a, u)}, `q0`, false) | `ownedKeys` 0 = `[]`, 1 = `[excepted no-deception]`; `separates … 1 0 σ = true`; with witness 0, no decision, value true: `false` (the default reading reaches true with the empty table); `decisionOnly D rs1 0 1 = some (excepted no-deception)`; finding `SeparatedByDecisionOnly: rs1: 0, 1 (not certified)` |
| K2 | `Df` with `necessary: [⊥]` | K1's σ: `distinguishing model violates a generated premise`; the same base, witness 1, no decision, value true: `distinguishing model does not separate readings`; no probe of `probesOf` separates the pair on `m0` |
| K2b | K2's set; as the base of a situation, `m0` with one more relation: `soft__excepted__no_deception` = {(a, u)}, the default document's generated exception predicate | through the wire, `InvalidInput: invalid situation <id>`: the base lists a predicate outside the author's base vocabulary. In Lean, an `example` that this structure is not `Admissible (authorEnv D)`, so that `Achieves` is false of both candidates on it, for every `F`, probe and value, and the base witnesses no `Separated`. Without the admissibility conjunct it would separate the pair: the default document overrides the predicate with its own table, and the strict document inherits a true tuple on a predicate it does not declare. The fixture does not ask for a proof that K2's pair is inseparable on every base (8.5), nor for an answer of `separates` on this base: `separates` does not test the base's validity (4.5 step 1), which the wire refusal and the `example` cover |
| K3 | {`S` named `no-deception-a`, `S` named `no-deception-b`} | for every probe of `probesOf` and both values, `separates = false` in both directions; `observeAll` equal. Both default: with witness 0, `excepted no-deception-a` = {(a, u)}, `q0`, false: `false` (the other reading empties `avoid_required` with its own table). The `selects norm avoid_required (a, u)` probe has the same value under both |
| K4 | {`S` named `avoid-x`, strict `help-x` on `+help_required`}; σ = (`m0`, witness 0, `q0`, true) | `separates = true`; `actOnly = some (avoid_required, help_required)`; finding `SeparatedByActOnly: rs1: 0, 1` |
| K5 | K1 with a fixed default rule `be-kind` on `+help_required`; σ = K1's with fixed `excepted be-kind` = {(a, u)} | `excepted be-kind` is shared for both candidates and owned by neither; `separates = true`; `cells … 0 = 0`, `cells … 1 = 1`: the fixed table is not enumerated. The same table under `decisions`: `InvalidInput: situation <id> decides excepted be-kind, which reading default does not own`. The finding of K1 still holds (`be-kind` is on another act) |
| K6 | K1 with a fixed strict rule `never-avoid` on `−avoid_required`, guard `⊤`; σ = (`m0`, witness 1, no decision, `q0`, false) | under 1 the default rule is blocked and `never-avoid` decides: `some false`; under 0 two strict rules collide: no value. `separates = true` with no decision; `decisionOnly = none`, no finding; E19 with case 4's second sentence |
| K7 | K1 with 13 users; witness 0, no decision, `q0` at `(a, u1)`, true | `cells … 1 = 13`: `ResourceLimit: decision assignments`; `separates = false` |
| K8 | a second set `rs2` on unit `u2` with a candidate declaring `no-deception` | `DuplicateDeclaration: no-deception in reading sets rs1 and rs2`. A candidate of `rs1` declaring the fixed `be-kind`: `DuplicateDeclaration: be-kind in reading sets rs1 and the document`. With K20's `rs2`, two fixed strict rules both named `twice-x`, one on `−avoid_required` with `over: [no-deception]` and one on `−help_required` with `over: [be-kind]`: `DuplicateDeclaration: rule twice-x` (each is attached to one set, and the two meet in no `one D s i`) |
| K9 | a fixed strict rule `except-x` on `−avoid_required`, guard `asks`, `over: [no-deception]` | admitted: `no-deception` is an interface name of `rs1`; `attached except-x = [rs1]`; `one D rs1 i` holds it and, with K4's set as `rs2`, `one D rs2 i` does not. With candidate 1 renamed `no-deceit`: `ReadingInterface: rs1: no-deception` |
| K10 | a candidate rule named `rd-1-x`; a base predicate `ve__bit__1__0` | `InvalidInput: name rd-1-x begins with rd-`; `InvalidInput: name ve__bit__1__0 begins with ve__` |
| K11 | a fixed strict rule `be-strict` on `+avoid_required`; `Df` with `over: [be-strict]` | `SoftOverHard: rule no-deception over be-strict under rs1@1:1` |
| K12 | {assertion `∀ agent ∀ user. asks`, `S`}; σ = (`m0`, witness 1, `q0`, true) | `separates = true` (the assertion reading has no rule: false); E19 with case 3, readings named `reading 1`, `reading 2`. Recorded instead with `holds`, value true: `separates = true`, shown by E24 |
| K13 | {assertion `∀ agent ∀ user. asks`, assertion `∀ agent ∀ user. ¬asks`, `S`}; pair (0, 1), σ = (`m0`, witness 1, `holds`, true) | `separates = true`; E21: "… Under reading 2, the sentence is true there. Under reading 1, it is false there." |
| K14 | `Df` with `sufficient: [asks]`, `necessary: [⊥]`; `m1` = `m0` with `asks` = {(a, u)}; σ = (`m1`, witness 0, `q0`, true) | the default reading has no admissible completion on `m1`; `separates = true`; `decisionOnly = none`; E19 with case 1's second sentence |
| K15 | {`S`, a candidate with `content: null`} | admitted as today; no pair is checked; the unit is not READINGS; K9's `except-x` beside it: `ReadingInterface: rs1: no-deception` |
| K16 | a set of two formulas with today's `models`, under the profile, no content-bearing set in the document | validated by today's code; identities and verdicts as with the profile off; `one_formula_only` |
| K17 | K4 on `norms@0, readings@1, relational-fol@0` | the same results on the norms chain; a default candidate there is rejected as a norm unit with soft fields is today, by the W1 decoder's text |
| K18 | K1 with `norm-defaults@0` in the list | `UnsupportedProfile: readings@1 content with norm-defaults@0 is not implemented` |
| K19 | rights chain, `VE.Rights.Examples.gamma`'s environment: fixed limitation `l29` (scope all, two necessary conditions); set `rs9` of right `r9` {claim `no-arbitrary-arrest` strict, the same claim default}; base: Texas; Ann, Bob; `arbitrary_arrest` = {(Texas, Ann)}; σ = (witness 1, fixed none, decisions `excepted no-arbitrary-arrest` = {(Texas, Ann)}, outcome `arrest_permitted (Texas, Ann)`, true) | `lim l29 arrest_permitted` and its two `cond` keys are shared; `ownedKeys` 0 = `[]`; `separates = true` (strict: the claim selects, not permitted); `SeparatedByDecisionOnly: rs9: 0, 1 (not certified)`; under candidate 1 the uncited exception's finding with ` under rs9@1:1` |
| K20 | K1 plus a second set `rs2` on unit `u2`, {strict `be-kind`, default `be-kind`} on `+help_required`, and on unit `u3` a fixed strict rule `both-x` on `−avoid_required`, guard `asks`, `over: [no-deception, be-kind]` | closure passes: `no-deception` is an interface name of `rs1` and `be-kind` of `rs2`. `attached u3 = [rs1, rs2]`, so `singlyAttached D = false` and the answer is `UnsupportedProfile: readings@1 fixed unit u3 depends on reading sets rs1 and rs2`; neither `free D` nor any `one D s i` is checked. With `over: [no-deception]` alone, `attached u3 = [rs1]` and the check passes |
| K22 | rights chain, K19's environment and `rs9`; (a) candidate 0's right lists its claim line twice; (b) a fixed `right_lines` unit on `r9` with a strict claim `no-detention` guarded by `journalist`, before `u9`; (c) the same unit after `u9` | (a) `InvalidInput: line order lists a line of right r9 twice under rs9@1:0`; (b) `UnknownRight: r9 under rs9@1:0` (the line is in the order and in no right); (c) admitted. In Lean, `linesOnce` is false of `twiceListed` and `orderOnly` and `genKeys` repeats keys on both, and true of the document listing the line once (DRI ruling 1) |
| K21 | malformed situations. (a) K1's σ with a `fixed` table `excepted be-kind` = {(a, u)}, in K1's document, which has no rule `be-kind`. (b) K5's σ with `excepted be-kind` listed twice in `fixed`. (c) K1 with the `soft` block's ranks `lo` and `hi`, `hi` outranking `lo`, outranking `holistic` decided by `unstated`; `S` and `Df` ranked `lo`; a fixed default rule `never-avoid-d` on `−avoid_required`, guard `⊤`, ranked `hi`, its exception as `Df`'s; σ = (`m0`, fixed `outweighs avoid_required lo hi` = {(u, a)}, witness 0, no decision, `q0`, true) | each: `situationWF = false`, `separates = false`, and through the wire `InvalidInput: invalid situation <id>`. In (a) neither reading's document generates the key. In (c) the key is shared and only the default reading's document generates it (the strict reading has no colliding pair of default rules), so the strict witness never reads the table, and its tuple is ill-typed: without step 1 in `separates`, every completion of the default reading would fail on that table and the pair would be shown as separated, by E19 with case 1's second sentence |

### 9.3 Differential and pilots

- **Differential.** 1,000 seeded generated sets (strict and default twins, mixed kinds, renamed twins that must
  not separate, fixed default rules, faulty sources): Python's search and validation against Lean's
  `readings-validate`, answers byte-identical, faulty sources rejected by both with one text. Every situation
  Python finds is accepted by Lean; a set for which the search finds none is rejected by both.
- **Shadow of `separation_conservative`.** On every generated pair in which neither side owns a key, some probe
  separates exactly when the two observation lists differ.
- **Pilots.** The constitution's 14 sets and the UDHR's 4 norm-candidate sets (`u017`, `u052`, `u112`, `u114`)
  validate in the document with their stored situations; the UDHR's right sets validate in the document with
  situations found by the search; section 11's figures are reported, among them any pilot document that the
  single-attachment check of 4.2 refuses.
- **F20.** With `readings@1` off no file under `conformance/` changes and `python3 VE/Route/frozen.py` passes.

### 9.4 The English

| # | Instance | Expected |
|---|---|---|
| G4 | E14 on F1 with decider `unstated` (composition.md 10.4) | contains "suppose the decider decides the exception applies"; does not contain "and the exception applies" |
| G6 | every sentence of section 2 rendered on K1 to K19 | no `ve__`, `rd-`, `soft__` or `rights__` substring |
| G9 | every sentence of section 2, with a source span whose text is "may not" | E14 is not used (no source word); no rendered sentence contains "may not" |
| H1 | E14 on K1 | the text of 2.5; one derivation; the second outcome sentence names `a`, no pronoun |
| H2 | E25 on K1; on K6 and K14 | shown on K1, with the finding's text ending ` (not certified)`; not shown on K6 or K14; E15 shown on none |
| H3 | E19 on K6, K12, K14 | cases 4, 3 and 1 of composition.md 2.1, texts of 2.5 |
| H4 | E22, E23 | neither on K1. E22 after E14 on K1 with K6's rule given the guard `asks` (it does not apply on `m0`, so E14's conditions hold); not on K9, whose strict rule is an exception to the twin. E23 after E14 on K1 with a fixed default rule on `−avoid_required`, guard `asks`, the `soft` block's outranking `strict`. Negative cases. A rule takes precedence over the twin: on K9 with K6's rule (guard `asks`) added, no E22; on K9 with that fixed default rule added, no E23. Outranking: the E23 document with outranking `holistic`, decided by `unstated`, no E23. Blocking: K with the permission predicate `avoid_permitted(agent, user)`, allow by default, declared as `avoid_required`'s dual, and the fixed default rule on `+avoid_permitted` instead, guard `asks`: no E23 (a permission beside the requirement, which step 2 does not block). On K5, no E23 (`be-kind` is on another act) |
| H5 | E24 | shown for K12's `holds` recording; never beside E14, E19 or E21 for the same pair |
| H6 | E5 on F6; E16 on K4 | as 9.1 and 2.5 |

### 9.5 `dispatch`

Composition.md's rows D28, D32, D34, D35, D38, D39, D40 and D50 (the lists with `readings@1` and no other
wrapper) are checked through the wired head. Python's
`checker_family` is extended so that it equals `dispatch` on every list containing `readings@1`, and fixture D-all
is extended to those lists (composition.md 6).

## 10. Limits, regeneration, Python, Rust

Limits: 64 candidates per set (W2); 12 cells of owned tables on the other side (`ResourceLimit: decision
assignments`); couplings at most 8 (rights 11); a situation's base within the finite-model limits of the lower
route. Every overflow is `ResourceLimit` with the limit named, never a truth value. Cost: one elaboration per
candidate with content, so linear in candidates; the load time is reported against the 85 s that 20 right sets cost
today, and is measured, not assumed.

Regeneration: `one D s i`, its generated vocabulary, its keys and every formula evaluated are recomputed from the
decoded document at every trusted site and bound to the chain's document hash; nothing is read from the wire as
authority. Until lean-first batch 3, Python regenerated `readings-validate` (`ve/readings_s1.py` `answer`) and
`ve/readings_route.py` compared it with Lean's byte for byte on every load; batch 3 deleted that regeneration
and the route relays Lean's answer (8.4). Python: `ve/profiles.py` registers the profile; `ve/readings.py` validates the wire of section 3,
searches for situations (domain size at most 2 per sort, preferring the probe order of 2.3) and delegates every
separation verdict to Lean under a backend authority; it renders section 2. Rust: nothing since lean-first batch 3
(its untrusted `readings-evaluate` replay was deleted).

## 11. The measured unlock

The plan names, for S1 (its section 6, ledgers of 2026-09-30T18:00Z):

| Text | Units the plan names | Baseline |
|---|---|---|
| UDHR (130 units, 10,916 bytes) | 43 units blocked on `force_variants_in_one_reading_set`; the 4 companion sets `u017`, `u052`, `u112`, `u114` | 4,175 bytes (38.2%) UNFORMALISED; 65 + 182 + 121 + 225 = 593 bytes in companion documents |
| Constitution (1,127 units, 184,893 bytes) | the 14 force sets | 1,833 bytes; separation shown by a placeholder model and a computation outside the document check |

The stage's rerun reports, per text and against these baselines: for each named unit, whether its recorded
primary blocker is gone, its new status and its bytes; the sets admitted in the document, by probe form; the
findings; pairs rejected, with their text; `ResourceLimit` hits; the load time. It also reports, per pilot
document, whether the single-attachment check of 4.2 refuses it, and if so the unit and the two sets. A refusal
covers the whole document, so one such unit fails F3 or F4; neither pilot has been checked for one, and this
report comes before the build relies on those fixtures. For the constitution the plan expects no status change.
The four UDHR units `u067`, `u068`, `u071a`, `u071b` are admissible by closure in S1 (13.17); the plan counts
their unlock under S2b, and the rerun says where it falls. No coverage number is predicted, and the measured row
replaces the plan's.

**Measured** (2026-10-02, [composition-s1-measured.md](composition-s1-measured.md), `tools/readings_s1_pilot.py`):
neither pilot is refused by the single-attachment check; the constitution's 7 strict/default force sets and the
UDHR's 23 content-bearing sets (19 right sets, the 4 norm-candidate sets) are admitted in the document, every pair
with one situation found by Python's search and checked by Lean, all with `outcome` probes; no unit changes status
(S1 adds none); the 43 UDHR units blocked on `force_variants_in_one_reading_set` lose that blocker but stay
UNFORMALISED until the translation re-encodes them; the UDHR loads in 141.7 s.

## 12. Statement review checklist (Astra + Fable, before S1's Lean)

The re-review of draft 2 covers what the statement review changed and no more: `WellFormedDoc` in 8.2
(`singlyAttached`, the fixed-name conjunct of `distinctAcrossSets_spec`) with 4.2 and 4.3; 8.3 and 8.4 (`Achieves`,
`AchievesQuiet`, `situationWF`, `separates`, `separates_sound`, `separation_conservative`'s hypotheses,
`readings_wire_separate_sound`); the rows of E22 and E23 with H4; pending candidates in 1.2; fixtures K2b, K20
and K21 and K8's added case; and the choices of 13.21. It also covers the one claim the verification of draft 2
corrected: how much of 4.5 step 1 `separates` enforces (4.5 step 1, the docstrings of `situationWF`, `separates`
and `SeparateReplay`, the notes of 8.3 and 8.4).

1. The frozen inputs: nothing of composition.md or `lean/VE/Compose/*` is changed; `dispatch` is used as defined;
   `Content` and `Content.declared` are S0's.
2. Fixed units, open sets, attached units and `one D s i` (1.2 to 1.4, 8.2): `place` against `addUnit`; what a
   candidate's document holds and omits; 5.2's limit on what separation says.
3. Source keys (1.5): the six key forms against soft-norms 1.3 and rights 1.5 and 1.6; shared against owned;
   F5 and K19 under both classifications (13.3).
4. Probes (1.6, 8.3): the key (kind, predicate, tuple) against `ve/readings.py`; no rule name; `Observes` on the
   expansion; the value `none` at a collision.
5. `Achieves`, `Separated`, `separates` and `separates_sound`: admissibility of the base over the author's
   vocabulary; step 1's conditions on keys, tables and the probe inside `separates`, and the base's validity as
   the hypothesis `valid`; the conclusion on the shown base and shared tables; the witness; the bound; why the
   other side's negation is exhausted by `assignments`.
6. `separation_conservative` against today's comparison, and its difference at a collision (13.19).
7. `force_agrees_off_exception` as the plan states it; `decisionOnly` and `decision_only_sound`; that E15 claims
   no more.
8. Admission (4.1 to 4.4): the order; `ReadingInterface`; single attachment and its named abstention; the
   cross-set check as the precondition of `choice_wellFormed`, with fixed names distinct across the document; the
   chain diagnostics with their reading.
9. The three chains (13.6) and the abstention on `norm-defaults@0` (13.7).
10. The wire (3): the situation, its id, keys by source; nothing in canonical bytes when absent.
11. The English (2): the slots; E14 without a pronoun and with a closed source word; E22 and E23 against
    soft-norms 4.2, with the conditions under which each is shown; E24; which wording a pair gets; G9.
12. Conservativity (4.9) and F20; the fixtures (9), each derived by hand.
13. The resolved choices of section 13.

## 13. Resolved choices in this draft

Each is a point where the plan left a reading open; the review may overturn any of them.

1. **This file is `composition-s1.md`.** The plan and composition.md name S1's specification `readings.md`; the
   pointer plan names this file. Neither frozen file is edited for the name.
2. **S1's share of F2, F3, F4, F6 and F20 follows composition.md 10.5**, not the plan's "F1 to F6": what needs
   `Choice_D` or a verdict across readings is left to S2 and named in 9.1's last column.
3. **A key is shared exactly when its rule or limitation is a fixed unit's.** The plan's sketch (`sharedBase`)
   takes "the generated predicates of the fixed units alone", under which a fixed limitation's table on an act
   that only candidate lines have is private to each candidate. Then F5 fails: with limitation 29 on every right,
   the strict reading reaches the default reading's outcome by deciding that the limitation holds, and no
   situation separates them. Plan 2.4's prose ("the decision, limitation and bar tables of the fixed units, keyed
   by source key") is taken instead: the limitation's decision is one table whichever reading is taken. This also
   makes the classification a test on one name, with no document of the fixed units alone, which need not be
   well-formed. `sharedName` is replaced by keys.
4. **`one D s i` omits fixed units attached to other sets**, and holds those attached to `s`. The plan says "fixed
   units plus the candidate"; a fixed unit that uses another set's interface name has no meaning without a
   candidate of that set. A unit attached to two sets is refused in S1; S2 lifts this.
5. **Probes are read in the expansion of a completion** (`canon`), and tuples are typed. The plan's `Observes`
   applies `ValueSoft` to the base, where a guard that mentions a regulated predicate would read an empty table.
6. **Three chains, one check.** On the norms chain a candidate's document is checked as the soft document with the
   empty block, every rule strict. So under `readings@1` a `norms@0` document with a content-bearing set must pass
   the soft route's naming checks (a regulated name with `__` is rejected there). The alternative, W1's own
   check, would need the slot lemmas restated for W1.
7. **`norm-defaults@0` beside a content-bearing set is a named abstention.** Composition.md 6 asks each stage to
   state the `fill` instance for the routes it sits on. S1's is: not built. The soft and rights heads abstain on
   such documents today, neither pilot uses the profile, and the instance is the one plan 2.9 sketches: the
   `unsaid__p` tables shared, `Fill_T` among the premises, an outcome probe reading the three-valued status.
8. **A bar candidate keeps `content: null`.** Plan 2.2 lists `{"bar": …}`; composition.md 1.6 makes the bar the
   one enumerated axis and gives `Content` no bar constructor. Bar sets are S2b's.
9. **One recorded form.** Under the profile every pair of a content-bearing set is a situation with a witness, a
   probe and a value; today's probe-free right-set models are not read there. `separation_conservative` says the
   search finds a probe whenever today's comparison would have differed.
10. **Findings have checkable criteria.** Plan 2.4 defines both by "every separating situation", which no check
    decides. `SeparatedByDecisionOnly` is a sufficient criterion with a theorem; `SeparatedByActOnly` is syntactic
    and needs exactly one act per reading, since E16 names one phrase each.
11. **E14's slots.** The paraphrases are the bare canonical sentences, as in composition.md 2.4's instance; plan
    section 3's instance adds "unless an exception applies", which after an authored `unless` clause would read
    two ways. `<subject>` is never a pronoun, although composition.md 2.4's instance writes "it". The source word
    is a closed list, so that G9 holds without exception; a set without one is shown by E19.
12. **E22 to E24 are S1's proposals.** E22 and E23 are asked for by composition.md 2.1. E24 exists so that a
    checked pair is never shown with an unregistered sentence or with none.
13. **`selects` probes are checked in S1 and worded in S2b**, as composition.md 6 assigns E20; a mixed pair with
    `holds` is worded by `right-clauses.md`. Until then both are shown by E24, and the search avoids them.
14. **The cross-set check ignores the kind of name.** Plan 2.2 says "of its kind" for fixed names. Rights requires
    rule, right, limitation and bar names distinct together, and `choice_wellFormed` needs that of every choice.
15. **`Doc` carries what S1 reads**: couplings and narrowings as data, a candidate's `cites`, items in source
    order. The plan's sketch has `base`, `asserted` and `constraints`; discourse's constraints are added by the
    stage that reads them.
16. **A pending candidate declares nothing**, so a set with one has no interface name. A candidate S1 does not
    elaborate (a quantity, a composite kind, a bar) is pending in this sense too (1.2).
17. **Fixed units attached to a set are admitted in S1**, because closure and `ReadingInterface` are S1's (plan
    2.2, composition.md 8). Their copies and every verdict about them are S2b's.
18. **The rejection text is today's**, `distinguishing model does not separate readings` (composition.md 8); the
    plan's F19 writes "situation".
19. **`separation_conservative` is stated over S1's observation**, where an outcome is a value or none. Today's
    Python compares the truth of the outcome formula, which differs from it only at a collision; the fixtures
    compare the two on collision-free pairs.
20. **Chain findings that need no certificate are reported per candidate** in S1 (F5). Certified licences and the
    limitation audit across readings are S2b's.
21. **Forms draft 2 chose where the statement review fixed the correction and not its form.** The review may
    overturn any of them.
    - A name that two fixed units declare is refused with the chain's own `DuplicateDeclaration` text (4.3), so
      the correction adds no text.
    - Step 1 of 4.5, apart from the id and the base's validity, is one function, `situationWF`, which `separates`
      calls first and `SeparateReplay` carries as a field. The base's validity stays the proof `valid`, as the
      joint position has it (the `valid` hypothesis of `separates_sound` supplies the admissibility conjunct): it
      is not a Boolean check on a `FiniteModel`, so it is not added to `situationWF`.
    - `separation_conservative` takes step 1 for its list of shared tables as hypotheses; without them the
      statement is false of a list that `separates` now refuses.
    - K21 has three cases: an ungenerated key, a repeated key, and the review's own case of an ill-typed table on
      a key only the other reading's document generates.
    - H4's negative cases use a declared dual and a holistic flag, which environment K does not have.
    - K8 gains a case for the fixed-name check.

## Change log

| Date | Revision | Changes |
|---|---|---|
| 2026-10-02 | Draft 1 | First statement specification of stage S1, from plan draft 2 through the pointer plan's draft 2: candidates as contents on three chains; fixed units, attached units and a candidate's document; source keys, shared and owned; situations with a witness, a probe and a value; `Achieves`, `Separated`, the executable `separates` with its bound; admission in four checks; two findings with checkable criteria; labels and couplings on every chain; the slots of E5, E14, E15, E16, E19, E21 and the sentences E22 to E24; the wire of a situation; diagnostics; the Lean statements `separates_sound`, `observe_sound`, `separation_conservative`, `force_agrees_off_exception`, `decision_only_sound`, `one_formula_only` and the chain lemmas; fixtures F1 to F6, F15, F19, F20, F22 in S1's share, K1 to K19, the differential, the pilots, the English; the measured unlock; twenty resolved choices. No code, Lean or frozen contract changes. |
| 2026-10-02 | Draft 2 | The converged statement review of draft 1 applied (`manage-agents/debates/compose-s1-spec`, verdict FIX, CONVERGED after round 3), nothing else, and no design question reopened. **(1) Admissibility** (Fable 1, Astra 1): `Achieves` and `AchievesQuiet` require `B.Admissible (authorEnv D)`; `authorEnv` moved above them; 1.6; fixture K2b. **(2) Soundness on the shown base** (Fable 2): `separates_sound` and `readings_wire_separate_sound` conclude that the witness achieves the recorded value and the other reading cannot, on the shown base and `tablesOf σ.fixed`; `Separated` is the corollary `separates_separated`; 5.1. **(3) Step 1 of 4.5 enforced** (Fable 3): `situationWF` (keys once, generated-key membership, typing of both readings' shared tables, the probe) is the first conjunct of `separates` and a field of `SeparateReplay`; the decoder refuses a malformed situation; `separation_conservative` takes step 1 as hypotheses; section 7's row; fixture K21. **(4) E22 and E23** (Fable 4): both shown only when no rule takes precedence over the twin; E23 only when the other default rule is one step 2 blocks and outranking is strict; E23's "one reading" cell corrected; the wordings unchanged; H4's negative cases. **(5) Fixed names** (Fable 5): names declared by fixed units are distinct across the whole document (4.3, the last conjunct of `distinctAcrossSets_spec`, `Item.names`), with the chain's own text; K8's added case. **(6) Pending** (Fable 6): a quantity, composite or bar candidate is pending in every check of S1 (1.2, 3, 4.1, 4.5, 13.16). **(7) Single attachment** (Astra 2): `WellFormedDoc` gains `singlyAttached` with `singlyAttached_spec`, checked after closure and before `free D` and every `one D s i` (4.1, 4.2); the new text `UnsupportedProfile: readings@1 fixed unit <u> depends on reading sets <s> and <t>`; 13.4; fixture K20; 9.1, 9.3 and section 11 report any pilot document the check refuses, which has not been checked. Also: the status note, the re-review scope in 12, resolved choice 21. No code, Lean or frozen contract changes. |
| 2026-10-02 | Draft 2, verification fix | The verification of draft 2 against the joint position (`manage-agents/compose-s1-p3ver1.final.md`: the seven corrections present, no unrelated substantive change, one correction incomplete) applied, nothing else. **Correction (3) qualified**: 4.5 step 1 claimed that `separates` checks the whole step, a base valid over the author's vocabulary included, and `situationWF` never tests that validity, so `separates` can answer true on K1's σ with a true tuple on an undeclared predicate added to its base. Of the verifier's two remedies the claim is qualified and `situationWF` is left as it is: validity over an environment is not a Boolean check on a `FiniteModel`, and the joint position keeps it as the hypothesis `valid` of `separates_sound`. Changed: 4.5 step 1 (the decoder checks the whole step; `separates` checks the conditions on keys, tables and the probe; the id and the base's validity are the decoder's, and `separates = true` certifies a separation only with `valid`); the docstrings of `situationWF`, `separates` and `SeparateReplay`'s two fields; the notes of 8.3 and 8.4; K2b's last sentence; 12 (scope and item 5); 13.21's second bullet; the status note. No definition, theorem statement, admission rule, diagnostic text, wording or expected fixture value changes. No code, Lean or frozen contract changes. |
| 2026-10-02 | Draft 2, review fixes | The compose-s1 review (Astra, Fable: FIX) and the three DRI rulings of 2026-10-02 on the S1 Lean report, applied. **Witness in the pair** (A): a situation recorded for a pair has one of the pair's two readings as witness, else `InvalidInput: invalid situation <id>` (3, 4.5 step 1, 7). **Ruling 2** (A): `decision_only_sound` is unproved, so `SeparatedByDecisionOnly` ends with ` (not certified)`, E25 ("It is not certified that …") replaces E15, and nothing downstream reads the finding as checked (1.7, 2, 2.3 to 2.5, 4.6, 5.5, 7, 8.3 notes, 8.5, H2). **Ruling 1** (B): the line-order check of 4.4 (`InvalidInput: line order lists a line of right <r> twice`; `UnknownRight: <r>` for an entry no right has, which `place` allowed and the rights decoder refuses), `linesOnce`, and `genKeys_nodup` with the hypothesis `linesOnce X = true`, proved in `Lines.lean` (8.1, 8.2 note, 8.3, 7, K22). **Ruling 3** (B): 4.1 records that Lean decodes no couplings or narrowings and does not repeat W2's structural validation; the report says which checker covers what (6). **Unit kinds** (B): a unit's content is in force only under its kind; the wire carries the kind (1.2, 8.4). **Agreement and report** (B): Python's regeneration of `readings-validate` compared byte for byte on every load, the search, Rust's untrusted replay, the 9.3 differential, the section 6 report and the 2.3 wordings, and the measured rerun of section 11 ([composition-s1-measured.md](composition-s1-measured.md)); `situations` is optional (3). No frozen file changes; no other statement of 8.2 to 8.4 changes. |
| 2026-10-02 | Draft 2, recheck fix | The recheck of the review fixes (`manage-agents/compose-s1-looprecheck1.final.md`, FIX, one B finding) applied: Python's regeneration compared contents as written where Lean compares them decoded, so a right whose second line differed only by `cites: {}` was `InvalidInput: line order lists a line of right r9 twice` for Lean and passed the line-order check in Python (`CheckerUnavailable` on the route). Python now compares lines and rules as Lean's decoders hold them (`SourceLine`, `SoftNode`, a right's header) in the line order of 4.4 and in force twins of 1.7 (an empty `cites` or `fan_out`, a soft field at its default, another key order: the same line), and reads a rights unit's optional fields as Lean's decoder does (an absent guard is `top`, an empty `fan_out` none, an absent decider null, a bar's accepted). Regression tests per case and the 9.3 differential's generators write these variants. Not changed: Python's texts for malformed rights contents (an unknown field, an empty decider) still differ from the Lean decoder's, so such a document is `CheckerUnavailable`, not rejected with one text; no statement, Lean or frozen file changes. |
| 2026-10-02 | Draft 2, recheck 2 fix | The second recheck (`manage-agents/compose-s1-looprecheck2.final.md`, FIX, one B finding) applied: Lean receives the document through `wire`, which omits null values, while Python's regeneration elaborated the contents as written, so `cites: null` on a right's line, `mode: null` on a soft norm, `hard: null` or `alterable: null` were admitted by Lean and refused by Python (`CheckerUnavailable` on the route). Python's regeneration now reads the whole document as Lean receives it (an explicit null is an absent field, at every depth: candidates, fixed units, bars, and the attachment pass of the document path). The document path's W2 loader still refuses such nulls before S1 (v0 JSON has no null), so no document's verdict changes there. Regression tests on the rights, soft and norms chains, and the 9.3 differential's generators write optional fields as null. Not changed, as before: Python's texts for malformed contents (a field Lean's decoder refuses: an unknown field, a strict rule with an exception, W1's field list on the norms chain) differ from the Lean decoder's, which refuses them while decoding the document, before any candidate label, so such a document is `CheckerUnavailable`, not rejected with one text; no statement, Lean or frozen file changes. |
| 2026-10-02 | Draft 2, loop fix | The compose-s1 loop (`manage-agents/compose-s1-loop.final.md`, FIX, one B finding) and the orchestrator's directive (`manage-agents/compose-s1-null-directive.md`) applied: Lean receives the environment through `wire`, which omits null values, while Python's regeneration decoded it as written, so `vocabulary.soft: null` or `vocabulary.rights: null` on K1 was admitted by Lean and refused by Python (`CheckerUnavailable` on the route). Every S1 entry point now reads the same normalised input: `S1Environment` reads the environment through `wire`, as `Document` reads the document, and the route normalises both once and gives the same object to Lean and to Python. In the same class: Python's rights environment now reads the `rights` block as Lean's `decodeRightsBlock` does (`holders` and `bearers` required, an absent `protected` or `alters` empty, the block kept as written so the identity is Lean's; a malformed block is `InvalidInput: invalid rights block`, Lean's text); a missing or null `profiles` is Lean's `UnsupportedProfile: profiles must be a sorted unique array`, not a Python `KeyError`; a right's line on a predicate that is not regulated reaches the line decoder's `UnknownSymbol` instead of an `AttributeError`. Regression tests: every field of four environments at every depth, and each optional field they leave out, written as null, on the answer path and on the route; the 9.3 differential's environments carry such nulls (564 of 1,000 cases). Not changed, as before: where the environment without the field is malformed (a required field missing) or makes a content ill-typed, Python's text differs from Lean's (and on the rights chain Python's typing errors lack Lean's code prefix, `UnknownSymbol: `), so such a document is `CheckerUnavailable`, not rejected with one text, with a null exactly as without the field; no statement, Lean or frozen file changes. |
