# Purpose and explanation (`purposes@0`): buildable plan

> Status: plan draft 3 (2026-10-28), branch `design/purpose-explanation`, from `main` at `6d0a10526`. Research:
> [purpose-explanation.md](../research/purpose-explanation.md), cited **R n** for its section n. Draft 2 applied the
> converged plan debate (`manage-agents/debates/design-purpose-explanation/{fable,astra}.md`: REVISE, then BUILD;
> CONVERGED after round 3; edits E1–E7 as corrected in round 3, A2–A6 and Astra's round-2 and round-3 additions) and
> the acting DRI's cross-plan rulings of 2026-10-28 (`manage-agents/reviews/dri-decisions-20261028-purpose-explanation.md`,
> cited **DRI n**). The item-1 statement spec is [purpose-explanation.md](purpose-explanation.md); its statement
> review gates PE-1. Every byte figure is an estimate unless it says "measured"; no byte is claimed before its audit
> passes.
>
> Draft 3 applies the statement review's ruling (`manage-agents/debates/purpose-explanation-spec/DRI-RULING.md`,
> items 1 to 14, cited **SR n**) to this plan and to the spec (spec draft 2) in one pass. Section 9 maps each item to
> the sections that carry it. No frozen contract and no existing theorem changes.
>
> **Synthesis round 2 and the fidelity-pilot revision (2026-10-31).** This draft applies
> `manage-agents/debates/plan-synthesis-2/edits-purpose-explanation.md` (DRI-decided; edits 1 to 9) and the acting DRI's
> fidelity-pilot revision PE-R1 to PE-R5 (`manage-agents/reviews/dri-decisions-20261031-fp-purpose-explanation.md`
> item 1). Section 10 lists each and where it is applied. Docs only.
>
> **pe-rev, DRI 2026-11-02 fp-purpose-explanation item 1.** This draft applies findings PE-R6 to PE-R11 and the
> decision's two C points (`manage-agents/reviews/dri-decisions-20261102-fp-purpose-explanation.md` item 1) from the
> 2026-11-02 re-pilot (7 of 10). Section 10.3 lists each and where it is applied. PE-1's and PE-2's statements change
> (PE-R8, PE-R11); the spec carries them as written without elaboration. Docs only.
>
> **Lean directory**: `lean/VE/Purposes/` (namespace `VE.Purposes`), as the wave's brief names it. **Profile**:
> `purposes@0`. **Front-matter block**: `purposes`.

## 0. Summary

A document's reasons and purposes come in two kinds, and the plan treats them differently.

- **Document-level** reasons and purposes are the ones the author gives for its own rules, claims and devices: "We
  place X above Y because …", "This is why …", "The order is intended to convey …". Each is a **link** between two
  sides, recorded in a `purposes` block. Lean checks the link's structure and writes the sentence a reader sees. A
  link never adds a premise and never changes a rule. Where the target is a claim with one formula, Lean also reports
  whether the stated reason, with everything else the document says, is enough. It asks the target's question of the
  document without the target unit's own assertion (E1), on whichever of ask's three adapters (plain, zero-set,
  enumerated) ask selects (SR 7), and reads the answer from the certificate's cited sources (`VE.Ask.usedPositions`,
  `VE.Ask.cited`), with no new prover. Every other sentence, rule or definition the proof uses is named; a proof that
  uses no stated reason is reported as such (E2). Support on soft documents (a soft chain with defaults and
  exceptions) waits until ask serves them; until then such a request gets ask's own refusal (SR 11).
- **Content-level** reasons and purposes are part of what a rule requires or what a sentence describes. They are
  written inside the rule as W2 open terms or judgment terms with a decider, never as links. They include aim rules
  ("Education shall promote …"), an act's purpose ("concealing … in order to gain market advantage"), a purpose that
  limits a rule ("only such limitations as are … solely for the purpose of …"), and a motive an agent must act from.
- **"In order to" after a rule** can be either kind. Where readers would differ, it is a reading set: {the purpose is
  the rule's rationale; the purpose limits the rule}, shown with the distinguishing situation.

| Batch | What | Kind | Hours | After | Bytes (estimate) |
|---|---|---|---:|---|---|
| PE-M0 | Re-measure the need on the full unit text | measurement, model-free | 2 | — | 0 (replaces R 2.1's floors) |
| **PE-0p** | **UDHR u101, u102 as aim rules** | pilot, no product code | 3 | — | **UDHR +190 B** (+104 B if only u101 passes); claimed only at its audit |
| PE-1 | `VE.Purposes` core: links, wire, checks; the nonfactivity predicate; no pack premise from an unstated side (PE-R11); which candidates hold a link's target, and the unit's unlinked parts (PE-R8) | Lean, new files only | 5 | statement review | 0 |
| PE-2 | The `purposes` block in the document mode; relay; display, a link's line only under the candidates that hold its target, and a line that names the scope it cannot quote (PE-R8) | Lean + Python relay | 6 | PE-1; checked-view refactor; C6 item; document-mode queue | 0 alone; fidelity |
| PE-3 | Source-word rows and authored wordings; `judgments@0` in the `purposes@0` row, for D6 (a)'s limiting candidate (PE-R10) | Lean rows (english-lean) | 4 | PE-2, en-sw, ET-5's "since" row, PE-E1, PC-1 (G3 and `judgedIn`, PE-R10) | 0 alone |
| PE-4 | Cross-unit links through discourse mentions; cycles; summary | Lean | 5 | PE-2 | 0 new; fidelity for 149 B claimed |
| PE-5 | Support check over the certificate's cited sources, the target removed | Lean + relay hunk | 6 | PE-2, `feature/q1-4b` merged, support-context review | 0 now; enables arguments |
| PE-6 | Claims about the rules' own shape; the hard-constraint argument | Lean + pilot | 6 | PE-5, ET-1's audit, S3's owner (synthesis round 2), Q3, the evidence repair, the acts × alternatives lift (act-phrases) | none claimed (E4); fidelity for 119 B |
| PE-7b | Purposes of acts on events: "is aimed at" | Lean rows + pilot | 5 | the C21 bridge (speech-acts' `documents@1` lift, after commands' CI-2), ET-5, JT-5r, AP-3, events' `packSources_complete` (PE-R11) | 0 alone; u0185.s05 154 B with scope |
| PE-E1 | Experiment: purpose role, "not … because", attachment, display | experiment, model calls (DRI 4: authorised) | 3 | PE-1's statements | adds reading sets or rewords lines |
| PE-E2 | Experiment: motive rules as open relations | experiment, model-free + audit | 4 | — | gates a motive batch |
| PE-E3 | Experiment: does any pilot need means-end transmission? | experiment, model-free | 2 | — | gates a design batch |
| PE-E4 | Experiment: safety-case arguments in PF and RSP | experiment, model-free | 2 | dri-safetyfw ledgers | gates PE-5b fixtures |

PE-7a (UDHR u111's limiting purpose) is removed (E3): Art. 29(2) is rights' limitation `L29`, which already has the
open condition `solely_for_permitted_purpose` (`rights-PLAN.md` 217–223), and scope's F14. A binary
`for_the_purpose_of` with a new `aim` sort would be a second encoding of the same thing. u111's fidelity note goes to
rights' `L29`; `purposes@0` adds nothing there (DRI 3(f)).

**Order** (the round-3 joint order, DRI 4).
1. PE-M0 and PE-0p now, in parallel. Both are model-free and pilot-only, with no product code. PE-0p names C2.
2. The statement review of the corrected sections 2.1 to 2.6 ([purpose-explanation.md](purpose-explanation.md)): the
   reduced support context, the nonfactivity predicate and its theorems, the `Support` vocabulary (NEW under
   PLANS-INDEX D8; its lines reuse `VE.Ask`'s and `VE.Words`), and the typed checked-document view. The review ruled
   FIX (SR 1–13). Its gate (SR 14) is one check that the spec and this plan carry every item; it reopens nothing
   else. PE-1 starts after that check passes. SR 5 and SR 6 are PE-1's statement changes; the other items are PE-2
   text or PE-5 statements.
3. The C6 wire-contract item for `purposes@0` and the checked-view refactor (owner: the document model) are assigned
   and delivered; then PE-1, then PE-2. PE-2 and PE-5 add rows to the rd-9 relay-binding inventory (D9).
4. In parallel:
   - PE-4 after PE-2. It replaces `sameUnit` and checks existence, kind, coverage and nonfactivity on resolved sides.
   - PE-5 after `feature/q1-4b` and the support-context review.
   - PE-3 after en-sw, ET-5's "since" row, PE-E1 and (pe-rev, PE-R10) PC-1, whose G3 and `judgedIn` its
     `judgments@0` entries rest on.
5. PE-6 after PE-5, ET-1's audit, S3's owner (DRI 2(e)), Q3, the evidence repair (2.7) and the acts × alternatives
   lift (act-phrases; PE-6's gate, PE-R3).
6. PE-7b and CI-7's purpose integration wait for named, audited bridges: events and judgment terms in documents, and
   speech-acts × `documents@1` (C21, DRI 3(a)). C21's named bridge is speech-acts' `documents@1` lift, after
   commands' CI-2 (synthesis round 2). (pe-rev, PE-R11) PE-7b's `events@0` entries also wait for events' owner to
   prove `packSources_complete` for `events@0`.
7. PE-E2, PE-E3 and PE-M0 can run at any time.

## 1. Design decisions

- **D1. Two levels.**
  - Document-level reasons and purposes are links in the `purposes` block. They add no premise
    (`checkDocPurposes_base`, 2.5).
  - Content-level reasons and purposes are formulas and rule parts written with existing machinery: W2 open terms,
    judgment terms, guards.
  - Which level a source sentence has is the reading question (D6). Nothing is decided silently.
- **D2. A link needs a marker word in the source**: "because", "since" and "as" (reason sense), "this is why", "that
  is why", "in order to", "so that", "so as to", "to the end that", "for the purpose of", "for the sake of", "is
  intended to", "is meant to", "Now, therefore". Implicit reasons (a sentence that happens to explain another) are
  never links (R 3.2, PDTB).
- **D3. W2's slot order is pinned.**
  - For `causal("because", c, e)`, `c` is the reason's kind and `e` the target's.
  - For `causal("in order to", c, e)`, `c` is the target's kind (the means) and `e` the purpose's (the end).
  - `docs/spec/document.md` leaves this unstated. PE-1 proposes one sentence for it to W2's owner (shared pieces,
    S5).
- **D4. Marker bytes are honest.** A marker part (the bytes of the link words) may have status LABELLED only when at
  least one link it marks has both sides CHECKED or OPEN. Otherwise its meaning must be
  `{"unformalised": "purposes-side-unformalised"}`, so a "because" with unexpressed sides never adds covered bytes.
- **D5. Sufficiency only from the document's own certificate, the target removed.**
  - The target's question is asked of the document without the target unit's assertion (E1). Every assertion entry
    sourced to the target unit is removed; every other authored unit stays, a formula-equal statement included. The
    operation belongs to question-answering (`VE.Ask`, one owner of premise assembly; DRI 2(b)), and `Support.lean`
    calls it. Lean cannot tell which other unit an author derived from the target, so none is excluded for that
    reason: any other unit the proof uses is named.
  - VE says a reason is enough only when Lean replays a certificate that cites a reason unit and nothing else the
    author wrote. The background, pair and fill premises are VE's own machinery. An author's rule is not: it is named
    by its units (`VE.Ask.ruleUnits`). A definition is named ("the definition of n") until the definitions owner
    supplies its unit (E2).
  - It says "enough together with …" when the certificate also cites other units or definitions, and names them.
  - When the certificate cites no reason unit, VE says the claim follows without this reason, from the units and
    definitions it names (E2's new outcome). This describes that proof's independence of the reason, not a
    judgement that the reason is irrelevant.
  - It never says any of this for a rule, a ranking, a purpose or a denied link (2.6).
- **D6. Reading sets** where readers would differ:
  - (a) "<rule> in order to <Y>": {rationale: the rule as written plus a link; limiting: the rule's guard gains the
    open condition "doing so serves <Y>"}. Choosing the limiting reading is an author narrowing, recorded as such;
    VE never chooses it silently (synthesis round 2).
    - **Beside an attitude (PE-R7).** Where the rule is the content of a holder's attitude ("In order to <Y>, we
      believe <X> should <Z>", u0014.s03; "We want Claude to <Z> in order to <Y>"), the set gains a third candidate,
      `in-attitude`: the means-end relation is inside what the holder believes or wants ("we believe that, to <Y>,
      <X> should <Z>"; the anankastic reading, R 3.1). Its slot is the content position of the holder's attitude
      node, which attitudes owns (AT-3a's node; an attitude candidate is read at its node's content, PC-11's
      `KindReaderCovers`): what that content holds is a content-level purpose (D1's second level), and its form
      inside an attitude is attitudes' to state (request row in 8). This plan does not design it. Until attitudes
      states it, the candidate is pending (`content: null`, its rows `unknown`; PC rule 8), never dropped. It never
      derives "ought <Y>", and never a rule for <X> from <Y> (R 3.1; PE-E3's question stays open). It adds a
      candidate to D6 (a)'s existing set and adds no new set (DRI 3(h)); past 64 choices a whole-document readings
      answer is UNKNOWN naming the limit, never a refusal (a support request gets ask's `ResourceLimit`, SR 13). No
      reading set is reduced (below). The link's line is not shown under it: the candidate holds the holder's
      attitude, not the rule as a rule of the text, so its kind is not the kind the marker's slot gives the target,
      and it does not hold the link's target (D10a, PE-R8).
    - **Placement (C point of the 2026-11-02 decision).** The set sits on the rule's part, the link's target part,
      and the clause's bytes are a part of their own, the purpose side. `sameUnit` needs the marker, the target and
      the purpose as distinct parts of one MIXED unit, and a MIXED parent has no content of its own, so this is the
      one placement both checks accept. profile-composition's rule 12, "one reading set on the part that holds the
      rule and the clause", is read as this placement; its specification leaves the link's design to this plan.
  - (b) "not <A> because <B>": {the reason for not-A is B; A holds, and B is not its reason};
  - (c) A "because" that can give an agent's motive (PE-R9). D6 (c) covers exactly three frames:
    - "<holder> want(s) <agent> to <X> because <Y>" ("we want Claude to <X> because <Y>"): {Y is the reason for
      wanting; Y is the agent's motive};
    - "<agent> may choose to <X> because <Y>" (u0289.s05's "we may choose to keep our promises anyway because …"):
      {Y is the text's reason for the choosing; Y is the chooser's motive, inside what "may choose to" says}. The
      target is the "may choose to <X>" part, whose "may" and choice stay their owners' (modality, commitments);
    - "<agent> <X>, not because <A>, but because <B>" (PE-3's [142485,142713) fixture, "… not because it's told to,
      but because it genuinely cares …"): {B is the text's reason for X; B is the agent's motive}.

    In each, the set sits on the reason's part, and the link and its line stand under both readings: the link says
    only that the text gives Y after "because" for its target, which holds whichever reading is chosen, and the set
    is not on the target (D10a). The motive reading has no content until PE-E2 passes, so every verdict that depends
    on that choice is UNKNOWN. This revision writes no motive content, so a unit whose natural reading is the motive
    still has none. Four other frames are refused, a closed list: "<agent> decide(s) to <X> because <Y>", "<agent>
    choose(s) to <X> because <Y>" without "may", "<agent> tr(ies) to <X> because <Y>", and "<agent> does <X> out of
    <Y>". Each is a named GAP `motive_frame` (owner purpose-explanation; the motive batch that PE-E2 gates): its
    marker part, if it has one, is `unformalised` with that reason, and no link is written, so the reason reading is
    never chosen silently (D1); "out of" is no D2 marker, so it has no link in any case. Every other "because"
    (u0100.s01's "We place … above … because …", for example) stays D2's plain link with no D6 (c) set.
  - PE-E1 may add reading sets or reword lines. It never reduces a D6 reading set to one reading: that needs a
    textual argument for each unit, recorded in its fidelity audit (A4, DRI 4).
- **D7. "We want Claude to …" is attitudes'.** E3 and AT-8 decide report, rule or both. A link targets whatever part
  carries the want or the rule. Synthesis round 2 confirms D7 as a boundary: attitudes' E3 and AT-8 own "we want
  Claude to …"; this plan attaches its links to whatever E3 yields.
- **D8. `prevents` stays events-time-causation's.** A `purposes` link with relation `prevents` is refused. A causal
  claim between events is ET's "contributed to" or "was necessary for", never a link.
- **D8a. What a link asserts** (factivity, R 3.3).
  - An affirmed "because" states both of its sides, so each side is an assertion wherever its own kind makes it one.
  - "In order to" does not state that the purpose is achieved.
  - "Not because" does not state the denied reason.
  - So a purpose side, or the reason side of a denied link, must be inert: never a premise and never a rule (A2).
    The check is positive. `VE.Route.Admission.Kind.inert` (owner: route admission, DRI 2(c)) lists the kinds whose
    content no admission rule reads (`explanation`, `exposition`, `example`, `analogy`, `meta`). Refusing only
    `asserted` would not do, because `norm` and `definition` are active too.
  - The side's own kind and the kind of every candidate of an active reading set on it must be inert. Under PE-4,
    so must every unit a mention on that side resolves to. Such a part may carry content, which is shown and never
    asserted. Lean checks this (`nonfactive`, 2.3).
  - The guarantee is proved from admission's leaf provenance (`asserted | bridge | background`; no leaf names an
    inert unit), from the norm-role table (no inert kind has a norm role) and from the readings route's `inForce`
    (no inert kind puts content in force). It is not proved from the wrapper equality `checkDocPurposes_base`.
  - **Pack premises (PE-R11).** Packs (`weighing@0`, `attitudes@0`, `scales@0`, `events@0`) put premises in `X` too
    (profile-composition's rule 5), outside admission's leaves, so the three sources above do not cover them. The
    guarantee names them in two parts:
    - a stated check, `packsInert` (spec 4.2): no premise a pack puts in `X` is sourced to a part on a link's
      unstated side, or to that part's unit, which holds its bytes. Its fault is 6a, after the nonfactivity fault 6.
      Fixture F2c (PE-1): u0019.s01's F2 with a pack premise sourced to the denied reason's part is refused;
    - a proof obligation on every `layerCovers` entry of `purposes@0` whose list holds a pack: the pack's owner
      proves that each premise the pack puts in `X` names the unit or part it comes from (`packSources_complete`,
      spec 5.1), so the check sees every one. A pack whose premises do not carry their source cannot meet it, and a
      list holding it stays refused by the layer rule. No batch of this plan covers a pack list before PE-7b's
      `events@0`, which carries the obligation (request row in 8).
- **D9. No new relation word.** `Route.Admission.relations`, the generated schema enum and `ve/admission.py`'s
  `RELATIONS` are not touched, so no fourth copy appears (6).
- **D10. Lean writes every sentence a reader sees** (2.4). Python loads files, relays, binds the answer to the
  request and prints Lean's lines. For a marker part, Python prints Lean's line instead of W2's kind description;
  (pe-rev, PE-R8) a row with `under` prints its lines only beside those readings, and a marker whose links' `lines`
  are all empty keeps W2's kind description.
- **D10a. A link's line says no more than the readings and the scope it sits in (PE-R8).** A link has no
  candidate field, so its line must not show under a reading of its target that holds no target. A set on a
  reason's part (D6 (c)) does not limit the line: the link holds under each of its readings.
  - A link's line appears only under the candidates that hold its target. A candidate of an active set on a target
    part holds the target when its kind is the kind the marker's slot gives the target (`holdsTarget`, spec 4.2):
    under u0014.s03's {report; rationale; limiting} only `rationale` and `limiting` hold the rule, and `report` (no
    rule, so no purpose reading) does not. Lean then follows the line with "This holds only under these readings of
    "<target part>": <names>." When no candidate of some target part holds it, the link's lines are withheld.
  - A line under a scope it cannot name says so. When the link's unit has a part that no link of the block names
    and whose kind is not inert (u0289.s05's "Sometimes", a hedge whose formula spans the sentence), the line cannot
    quote the scope that part may put over the link, and Lean adds "The quotes above leave out "<part>" from the same
    sentence, which may limit what they say." A scope from another unit reaches a link only through PE-4's resolved
    sides, and PE-4 applies the same two functions there (2.8).
  - Fixtures F9 (u0014.s03's shape) and F10 (u0289.s05's shape): PE-1 for the facts (`shownUnder`,
    `unlinkedActive`), PE-2 for the lines (spec 9.2, 9.7).
- **D11. Authored English** (PE-3). Each wording below has one reading, and the profile fixes it:

  | The author writes | It means | Formal effect |
  |---|---|---|
  | `<sentence A> This is because <sentence B>.` | B is the text's reason for A; both are stated | link `because`, affirmed, plain; reason B, target A |
  | `<A> This is only because <B>.` / `This is partly because <B>.` / `This is not only because <B>.` | the same, saying B is the only reason / part of the reason / not the only reason | share `sole` / `partly` / `notSole`; `partly` and `notSole` need no other link (A4) |
  | `<A> because <B>.` (one sentence; SR 4) | The text says B, says A, and gives B as its reason for A. | one MIXED unit: parts A, " because ", B; link `because`, affirmed, plain; reason B, target A (PE-1) |
  | `<A> only because <B>.` / `<A> partly because <B>.` (one sentence) | the same, saying B is the only reason / part of the reason | the same MIXED unit; share `sole` / `partly` |
  | `<A> This is not because <B>.` | the text denies that B is the reason for A; B is not stated | link denied; B is an inert part (kind `explanation`), never a premise or a rule (D8a) |
  | `<reason sentence> This is why <sentence A>.` | the previous sentence is the text's reason for A | link `because`; reason = the previous sentence |
  | `<rule> The purpose of this rule is that <sentence Y>.` | Y is the purpose the text gives for the rule; the rule is unchanged | link `in order to`, rationale |
  | `<rule>, if doing so serves the purpose that <Y>` (wording fixed by PE-E1) | the rule applies only where it serves Y | guard conjunct: an open term, decided by its decider, written as a bound judgment over the rule's variables (JT-2's record, profile-composition's rule 12); `judgments@0` joins the `purposes@0` row in PE-3, the batch that first emits this candidate (PE-R10) |

  The inline rows are affirmative only (SR 4). Any negation before an inline "because" ("does not … because", "not
  only because", "not merely because") stays under the first refusal below, and the share `notSole` is written as the
  separate sentence "This is not only because …".

  Refused in authored text, each with its rewrite (rows in english-lean's catalogue):
  - "not … because": "Write which you mean: '<not A>. This is because <B>.' or '<A>. This is not because <B>.'"
  - "in order to", "so that", "so as to", "to the end that", "for the sake of", "for the purpose of" after a rule:
    "Write 'The purpose of this rule is that …' if the purpose does not change what the rule requires, or add the
    condition '…, if doing so serves the purpose that …' if it does."
  - "since", "as" and "given that" in their reason sense: "Write '<A> This is because <B>.'" The reason sense of
    "since" extends ET-5's "since" row (`events-time-causation-PLAN.md` 358): one canonical row (C1, A6).

## 2. Lean: modules and statements for review

The exact statements, their diagnostics and their fixtures are in the item-1 spec,
[purpose-explanation.md](purpose-explanation.md) (cited **spec n**). Draft 2's statements were elaborated against
`main` at `6d0a10526` (spec 11). The statements draft 3 adds or changes were written in a pass with no shell and are
not elaborated yet; spec 11.1 lists them, and the stub elaborates them once before PE-1 starts. This section records
what each file holds and what drafts 2 and 3 changed. The plan and the spec carry one copy of each statement, with one
exception: the support route's signatures (SR 8, SR 12), which the ruling requires verbatim in both, appear in 2.6 as
in spec 6.1, 6.2 and 6.4. New files only, under `lean/VE/Purposes/`, except the hooks listed per
batch and three owners' additions (route admission's nonfactivity file, question-answering's reduced context, the
document model's checked view). Names that already exist on `main` are used as they are:
`VE.Route.Admission.{Kind, decodeKind, relations, NodeAdmitted, admitDocument}`, `VE.Norms.Admission.normRole`,
`VE.Readings.Wire.inForce`, `VE.Ask.{Lead, Row, RowOk, LeadHolds, lead_sound, Reason, Source, sourced,
sourcedAssertions, ruleUnits, usedPositions, usedPositions_sufficient, cited, mem_cited, replayOk, Context,
citationText, leadText, reasonText}`, `VE.Words.situation`, `VE.Norms.{Tree, Node, Role}`, `VE.Closure.{reachEval,
Reachable}`, `VE.Compose.{profileTable, gateOf}`, `VE.Service.Document.{checkDocSets, profilesOf, RowUnit,
unitJson}`.

**Layers.** `Decl`, `Wire` and `WellFormed` are layer 2, so other plans can use the link (S1). `Verdict`, `English`
and `Support` import `VE.Ask` and are layer 4: `tools/layer_policy.py` gains one row for them, as it has for
`VE.Ask.` (spec 10).

### 2.1 `Decl.lean` (PE-1)

`Relation` (`because`, `inOrderTo`; `prevents` stays events', D8), `Polarity`, `Share`, `Ref` (`part`, and PE-4's
`mention`), `Link`, `Block`, `maxLinks` and `NotChecked`, as in draft 1 (spec 1). Changed in draft 2:
- `Share.partial` is renamed `partly`, because `partial` is a Lean keyword (2.3).
- `Decl.lean` no longer imports `VE.Ask.Basic`, and `Support` moves to `Verdict.lean` (2.4), because a layer-2 file
  cannot import `VE.Ask`.

### 2.2 `Wire.lean` (PE-1)

The front-matter `purposes` block (only with `purposes@0`): `decodeBlock` (exact fields; `share` defaults to `plain`
when absent; `prevents` and any word outside `VE.Route.Admission.relations` refused), `renderBlock`, and the round
trip `decodeBlock_render`. Unchanged from draft 1 (spec 1.2).

### 2.3 `WellFormed.lean` (PE-1)

What changed in draft 2 (spec 4):
- **Input: the checked view, not a second compile (A3).** `Units` is now the document's checked units and parts
  *after* the status fold: id, span, W2 kind, status, parent, formula, and the kinds of an active reading set's
  candidates. The document model exports this view (2.5); purposes compiles nothing. Draft 1's `Units` from
  `Loader.compileUnits` is gone: that call throws on norm content (`Discourse/Loader.lean:277`), and it does not see
  the statuses the document mode folds after compiling (`Document.lean:1808-1818`).
- **`sameUnit`** reads the parent of each part from the view. PE-4 replaces it (A3).
- **Nonfactivity is positive (A2).** `factiveOk` is replaced by `nonfactive`. On the unstated side, each part's
  kind and each of its reading candidates' kinds must be `VE.Route.Admission.Kind.inert` (D8a). A mention on that
  side is refused until PE-4 resolves it. The diagnostic now reads "would make a purpose or a denied reason a premise
  or a rule".
- **`Share.partly`.** Draft 1's constructor `partial` is a Lean keyword, so that declaration could not have
  compiled. The stub found this, and the constructor and its wire word are now `partly` (spec 1.1).
- **`shareOk` (A4).** `plain`, `partly` and `notSole` need no other link: "This is partly because B." with no other
  stated reason is ordinary English. `sole` is refused only against another affirmed link with the same relation and
  target and a *different* reason list, so a duplicate link is not a second reason. Draft 1's "says there is another
  reason, and the text gives none" is removed. PE-4 compares resolved reason identities (A6).
- Theorems: `check_ok_iff`, `sameUnit_parent`, `shareOk_iff` (an iff, both directions in fixtures), `markerAgrees_kind`,
  `nonfactive_iff`, `markerHonest_labelled`.

What changed in draft 3 (spec 4.2–4.4, 7.2, 9.2):
- **`sole` against `partly` or `notSole` (SR 5, E-d).** In `shareOk`, the `sole` branch also requires every other
  affirmed link with the same relation and target to have share `plain` or `sole`. A text that says both "only
  because B" and "not only because B" has no one reading of how many reasons it gives. Duplicates stay one reason
  (F7a). The right side of `shareOk_iff` gains the same condition: `M.reason = L.reason ∧ (M.share = .plain ∨
  M.share = .sole)`. Fixture F7e (l1 `sole`, l2 `notSole`, the same reason) is refused with text 8.
- **Ordered, adjacent sides (SR 6).** A new conjunct of `WellFormed`, `sidesAdjacent`: each side's parts are in
  source order and each part starts where the previous one ends. `check_ok_iff`'s right side gains it, and
  `sideAdjacent_iff` characterises it. Its fault, `InvalidPurposes: link <id> has a side whose parts are not adjacent
  and in order`, comes right after fault 4 and is numbered 4a, so every other text keeps its number. `sideText_eq`
  (in `English.lean`, because `sideText` reads `VE.Ask.bytesOf`): when the check passes, the quote is exactly the
  listed parts' bytes, trimmed. Fixtures F8a (a reversed side) and F8b (a side split by text the link does not
  list) are refused with that text. PE-4 replaces `sidesAdjacent` on resolved sides, as it replaces `sameUnit`.

What changed in pe-rev (spec 4.1, 4.2, 4.3, 4.4, 9.2):
- **Pack premises (PE-R11, D8a).** `Units` gains `packSources`, the ids of the units and parts that the premises the
  list's packs put in `X` are sourced to (`[]` on a list with no pack). A new conjunct of `WellFormed`, `packsInert`:
  no part on a link's unstated side, and not that part's unit, is in `packSources`. Its fault, `InvalidPurposes: link
  <id> has a side the text does not state, and a pack takes a premise from it`, comes right after fault 6
  (nonfactivity) and is numbered 6a. `check_ok_iff`'s right side gains it, and `packsInert_iff` characterises it. Fixtures F2c (a pack
  premise sourced to F2's denied reason, refused), F2d (sourced to its unit, refused) and F2e (sourced to F2's
  target part, `.ok ()`).
- **Candidates and unlinked parts (PE-R8, D10a).** `Part` gains `readings`, the names of the candidates whose kinds
  `candidates` lists, in the same order. New functions with their theorems: `holdsTarget` (a candidate kind is the
  kind the marker's slot gives the target), `shownUnder` (for each target part with an active set, the names of the
  candidates that hold the target; `shownUnder_iff`) and `unlinkedActive` (the parts of the link's unit that no link
  of the block names and whose kind is not inert; `unlinkedActive_iff`). They are facts for the lines, not
  conjuncts of `WellFormed`: no well-formed block changes. Fixtures F9 (u0014.s03's shape) and F10 (u0289.s05's
  shape).
- Every earlier fixture has `packSources = []`, no `readings` and no unlinked part, so its value is unchanged.

### 2.4 `Verdict.lean` and `English.lean` (PE-2; PE-5 adds the support lines): the lines a reader sees

What changed in draft 2 (spec 2.3, 6.4):
- **`Support` is NEW under PLANS-INDEX D8 (E6, DRI 2(b))** and lives in `Verdict.lean`. Its outcomes are `alone`,
  `together units definitions`, `without units definitions` (E2's new outcome), `notEnough`, `ruledOut`,
  `notSettled`, `unknown reason` and `notChecked why`. Its wire form round-trips (`decodeSupport_render`), so the
  relay binds a typed answer. `Support` keeps its data type and renders through question-answering's D8 mapping
  table (synthesis round 2).
- **Reuse, where the meaning is the same.** The UNKNOWN line is ask's `leadText .unknown` followed by ask's
  `reasonText`. A situation is `VE.Words.situation` of the replayed countermodel or split, through ask's
  `situationOf`. Sentence numbers are ask's `citationText` over ask's `Context.displayOf`, a part taking its parent's
  number. Quotes follow ask's C1 rule: the source bytes, trimmed. Draft 1's 160-byte cut and its own `sentences`
  are gone.
- **Own frames, where the meaning differs.** The support question is asked of the document without the target, so
  ask's "a situation the document allows" would be false of the whole document. The `notEnough` line says
  "everything else the text says" (E1): "VE found that this reason is not enough: in this situation, everything
  else the text says is true and the claim is false: …". `ruledOut` and `notSettled` say "everything else the text
  says" too.
- `together` names the other sentences and definitions. `without` says "VE checked that the claim follows from …
  without this reason." `summary` stays PE-4's.

What changed in draft 3 (spec 2.3, 9.7):
- **E-a (SR 1).** `without [] []` has its own sentence: "VE checked that the claim follows without this reason, from
  nothing else the text says." It is a row of spec 2.3's table, and a fixture checks that no rendered line has two
  spaces in a row (draft 2's line was "follows from  without this reason").
- **E-c, then E-b (SR 2).** A cited part whose parent is the target's parent is named by its quote (ask's C1 rule,
  `closing`), never by its sentence number, which is the claim's own sentence. Only then are the other sentence
  numbers deduplicated with `eraseDups` before `citationText`. `others` takes a `Naming` (number, quote, own sentence),
  and `stop` ends a line with `closing`'s rule. Fixtures: F3 with both reasons asserted and p5 cited shows the
  quoted line; `together ["u5.p1","u5.p3"] []` prints "sentence 5".
- **Reading clauses exactly as ask's (SR 3).** `supportLines` groups the rows with `VE.Ask.groups`. A line that shows
  a situation names every open set's reading of its witness row (`VE.Ask.readingSuffix`), even when every row has
  the same verdict. With two or more groups, each line starts with ask's R1 clause. Fixtures S9 and S9b (PE-5).

What changed in pe-rev (spec 2.3, 5.4, 9.7; PE-R8, D10a):
- **Lines only under the candidates that hold the target.** `linkLines` wraps `says` and `verdict`: when a target
  part has an active set, the row's lines are followed by `underLine`, "This holds only under these readings of
  "<target part>": <names>." (the names joined by `VE.Senses.andList`); when no candidate of some target part holds
  it, the row's `lines` are empty (withheld). The section row gains `under`, `shownUnder`'s value, so the renderer
  prints the row only beside those readings; Python decides nothing.
- **A scope the line cannot name.** When `unlinkedActive` is not empty, `scopeLine` follows: "The quotes above leave
  out "<part>" from the same sentence, which may limit what they say." (each part's quote, joined by
  `VE.Senses.andList`).
- Fixtures: F9's and F10's lines (spec 9.7), and F9 with every candidate of a non-rule kind, whose lines are
  withheld.

### 2.5 `lean/VE/Service/DocumentPurposes.lean` (PE-2): the document mode under `purposes@0`

What changed in draft 2 (spec 5):
- **The checked view (A3; DRI 2(d)).** The document model (`VE.Service.Document`) exports `checkDocSetsView`, which
  returns the base answer and a typed `CheckedView`: the answer's `RowUnit`s after the status fold, scope's fold
  included, the source, and each active reading set's candidate kinds. Its theorems say the view *is* the answer:
  `checkDocSetsView_answer` (its first component is `checkDocSets`'s answer) and `checkDocSetsView_rows` (the rows
  render to the answer's `units`). This is one refactor in the document-mode queue, owned by the document model and
  delivered before PE-2. `purposesUnits` projects the view onto `VE.Purposes.Units`. It refuses a `rights@0` kind,
  because the profile row does not admit `rights@0` yet. Q2 is settled by this.
- `checkDocPurposes` reads the view instead of compiling the units again. `checkDocPurposes_absent` and
  `checkDocPurposes_base` keep their meaning: no premise, verdict, status or coverage row changes, and the answer is
  the base answer plus `purposes`.
- **Metadata keys (synthesis round 2).** No new `profileKeys` map. The `purposes` key is added through definitions'
  PD-1a mechanism for front-matter keys: one row `("purposes", false)` of `metadataKeys`, the one table of
  front-matter keys in `VE.Discourse.Loader` (as PD-1a adds `("definitions", false)`), so the discourse route still
  rejects the key. Lean's table owns the keys; Python gets no copy of the row (6). Spec 5.2's `profileKeys`,
  `documentMetadataFor` and `purposes_key_iff` (and fixture 9.5) are superseded by this and are restated over
  `metadataKeys` with PE-2.
- The profile row in `VE.Compose.profileTable`: `purposes@0` requires `documents@1`, and its slot is the document
  mode's outer wrapper (after scope). Its composition proof for each newly admitted combination is
  `checkDocPurposes_base`: the wrapper only adds a member to whatever answer the combination already gets.
- **Layer coverage (PE-R5).** `purposes@0` is a `.layer` row (profile-composition's plan, 3.1), so PC-4's layer rule
  refuses with E1 every list its own `LayerFacts` does not cover. PE-2's row batch adds the `layerCovers` entries, with
  their case of `layer_evidence`, for the lists the constitution documents carry, and these name `acts@0` and
  `definitions@0`, which every constitution document on `main` carries beside `documents@1`. The covered lists are
  derived from the profile table as PC-4 requires (`documentLayersOf`); `documentLayers` is not edited by hand, and
  `purposes@0` is not a document record. **Composes argument:** on every covered list `checkDocPurposes` reads the
  checked view after the status fold (`checkDocSetsView`), which already holds `acts@0`'s split and `definitions@0`'s
  admitted statements, and `checkDocPurposes_base` says the answer is the base answer plus the `purposes` member: no
  premise, verdict, status or coverage row changes, so the list's own answer is untouched, which is what `LayerFacts`
  asks. **Fixture** (PE-2): a constitution part document whose list holds `acts@0`, `definitions@0`, `documents@1` and
  `purposes@0` is admitted (no E1), and its answer without the `purposes` member is byte-identical to the answer for
  the same list without `purposes@0`. Main's refusal stays until that batch lands.
- **`judgments@0` (PE-R10).** D6 (a)'s limiting candidate puts a bound judgment in the rule's guard (D11;
  profile-composition's rule 12), so `judgments@0` sits beside `purposes@0` from the first batch that emits that
  candidate: PE-3, whose source-word rows generate D6's sets. A candidate that holds content needs the readings
  route, so PE-3's row batch adds the `layerCovers` entries for the lists holding `documents@1`, `judgments@0` and
  `readings@1`, and for PE-2's lists with `judgments@0` and `readings@1` added where their stack is listed (`acts@0`
  with `readings@1`, profile-composition's PC-6c), derived from the table in the same way. PE-3 waits for PC-1
  (order step 4). PE-7b no longer adds `judgments@0`.
  **Composes argument:** `judgments@0` composes with every admitted list through G3 (profile-composition's rule 4;
  PC-1's statement over every list), and its reader `judgedIn` reads the guard conjunct inside the `limiting`
  candidate's content on the readings route. `checkDocPurposes` reads only the checked view after the status fold,
  which already holds that answer, readings and judgment included, and `checkDocPurposes_base` says the answer is the
  base answer plus the `purposes` member: no premise, verdict, status or coverage row changes, so the list's own
  answer is untouched. Purposes never reads the judgment. **Fixture** (PE-3): a synthetic rule in u0146.s01's shape
  with no attitude, whose set is {rationale; limiting}: `rationale` holds the rule as written, and `limiting` holds
  the rule whose guard gains the bound judgment (its content, read by `judgedIn`). In a part document whose list
  holds `documents@1`, `judgments@0`, `purposes@0` and `readings@1` (and the rule's own profile, as the readings
  fixtures carry it), it is admitted (no E1), `limiting`'s rows read the judgment, and the answer without the
  `purposes` member is byte-identical to the answer for the same list without `purposes@0`. A seeded bug that drops
  the conjunct from `limiting`'s content must change that answer.
- **Other lists.** No batch of this plan names a list holding `attitudes@0`, `hedges@0`, `modality@0`, `scales@0`,
  `weighing@0` or `commitments@0`, because none has its composes argument here; every such list stays refused with E1
  until a batch names it with its argument ("later batches", spec 5.3; profile-composition accepts that refusal until
  each family's coverage lands). An entry for a list holding a pack also carries D8a's pack obligation
  (`packSources_complete`, PE-R11).

### 2.6 `Support.lean` (PE-5): is the stated reason enough?

What changed in draft 2 (spec 6):
- **The reduced support context (E1; DRI 2(b)).** Question-answering gains `VE.Ask.withoutAssertion D t`. It drops
  each fixed assertion item of the target unit `t` and keeps every other item, a formula-equal assertion of another
  unit included. It also gains `supportSourced N t c`: ask's `sourced` over the reduced document. The theorems:
  - the rules, fills and background are unchanged (`withoutAssertion_rules`, `choiceU_withoutAssertion`,
    `ruleUnits_withoutAssertion`);
  - the assertions are exactly the original ones minus the target's (`sourcedAssertions_withoutAssertion`,
    `supportSourced_eq`);
  - no premise of the support question has the target as its source (`supportSourced_target`).

  Evidence is generated and replayed against this reduced context, and its sources and request identities are bound
  to it (Astra round 3).
- **One shared adapter (synthesis round 2).** `VE.Ask.withoutAssertion D t` is the singleton case `withoutUnits [t]`
  of the one shared adapter `VE.Ask.withoutUnits N X` (with `replayReduced` and `withoutUnitsPlain`), in
  question-answering's `VE.Ask`. Whichever of PE-1/PE-2 and definitions' PD-2 lands first builds the adapter; the
  other reuses it. There is no second copy.
- **Every author-supplied source is named (E2).** `named` maps each cited source to the units and definitions it
  names. A sentence names itself. An author's rule names its units, through `VE.Ask.ruleUnits` under the row's choice.
  A definition names itself, until the definitions owner supplies its unit. The background, pair and fill premises
  name nothing. Draft 1's `othersCited` hid rules and definitions as machinery.
- **`supportOf`** gives `alone` only when a reason unit is cited and nothing else the author wrote is. It gives
  `together os ds` when a reason unit is cited together with other units `os` or definitions `ds`. It gives
  `without os ds` when no reason unit is cited (E2's new outcome). Each comes with an exact iff over `citedUnits` and
  `citedDefinitions`, and a soundness theorem over the replayed certificate: `alone_sound`, `together_exact`,
  `without_sound`. `notEnough_sound`, `ruledOut_sound` and `notSettled_sound` are stated over the reduced document,
  so they say "everything else the text says". `supportOf_lead` keeps UNKNOWN honest.
- **`eligible`** returns the target part, its formula and the reason parts, or the `NotChecked` that applies, in a
  fixed order: purpose, denied, rule target, readings, no formula. A reason part must itself be a stated, checked
  formula. Otherwise "not enough" would only report that a side was never formalised. It lands with PE-2 in
  `Verdict.lean`, so the document section can name each eligible link's question before PE-5 answers it.

**Where the row comes from (Q1, resolved as ask's case, SR 7).** The document mode's `purposes` section lists each
eligible link with its target and reason ids. Python sends each as an `ask` request with `support: {"target",
"reasons"}` in place of `question`, and the case that ask's relay builds for the document's adapter. That case's
`conclusion` is the target part's formula, and no English question is read. Ask's runner gains one hunk
(`VE.Ask.Run.askCase`): it selects the adapter by `routeOfDocument`, exactly as `answered` does, and calls
`VE.Purposes.replaySupport`. A document with no reading set therefore goes to the plain or zero-set adapter, never to
the enumerated one (S1 is plain). The query's units are the flattened parts, so part ids are `Source.unit` ids. The
existing producer supplies the evidence for the reduced premises. Lean builds the reduced context itself and replays
against it. The answer's `support` member is computed by `supportOf` from each replayed row and `cited` over that
row's reduced sources, with the lines of `supportLines`. The reduced context lives in `VE.Ask`; the verdict and the
wire live in `Support.lean`.

What changed in draft 3 (spec 6.1, 6.2, 6.4, 7.3):
- **One reduction over sourced premises (SR 7).** `VE.Ask.dropTarget t as := as.filter (·.1 != .unit t)`. Each
  adapter's reduced premises are its own sourced premises filtered by it: `PlainParts.without`, `ZeroParts.without`
  and `withoutAssertionN` agree with `dropTarget` (`PlainParts.sourced_without`, `ZeroParts.sourced_without`,
  `supportSourced_eq`).
- **Adapter-specific theorems, in full (SR 8).** Soundness on each adapter's Γ after `dropTarget`: `PlainRowOk`
  (plain), `RowOkU` (zero-set) and `RowOk` (enumerated); the plain adapter never gives `notSettled`
  (`plain_never_split`). The source-to-formula correspondence is the pair of columns of one filtered list. The
  signatures follow, verbatim as in spec 6.1 and 6.2.
- **No soft premise (SR 11).** Support is answered only through ask's three adapters, and on each the soft premises
  are empty. The enumerated adapter admits only `normsShaped` documents, so `choiceX N c = []`
  (`choiceX_normsShaped` with `normsShaped_of_ND`); the plain and zero-set types carry no X. Spec 7.3 adds no text
  for soft documents: fixture S10 gets ask's own refusal, word for word. Support on soft documents waits until ask
  serves them, which is question-answering's work (DRI 2(b)).
- **A tighter support request (SR 12).** The case has no premises and no assumed reading (ask's own text, spec 7.3).
  The answer's rows equal the replayed rows as lists, so order and multiplicity both count. `support_wire_sound`,
  stated in full below, links each row's verdict, sources and reduced premises, so the theorems above apply to it.
- **Past 64 compatible choices (SR 13).** Support keeps ask's limit refusal: the `ResourceLimit` text of
  `replayError`, word for word, with no support rows. No aggregate `unknown .tooMany` verdict is added, because the
  support shape carries verdicts only inside rows. Exhaustion never becomes a negative verdict.

```lean
namespace VE.Ask
open VE.Readings

/-- SR 7: the one reduction, the sourced premises without those sourced to the target `t`. -/
def dropTarget (t : String) (as : List (Source × VE.Formula)) : List (Source × VE.Formula) :=
  as.filter (·.1 != .unit t)

/-- Exactly the target's entries go: every other entry stays, in order. -/
theorem mem_dropTarget (t : String) (as : List (Source × VE.Formula)) (x : Source × VE.Formula) :
    x ∈ dropTarget t as ↔ x ∈ as ∧ x.1 ≠ .unit t

/-- No premise of the support question comes from the target. -/
theorem dropTarget_target (t : String) (as : List (Source × VE.Formula)) : ∀ x ∈ dropTarget t as, x.1 ≠ .unit t

/-- VE's own premises (definitions, background, pairs, fills, rules) are never a unit's, so the reduction commutes
    with ask's `sourced`. -/
theorem sourced_dropTarget (U : UDoc) (t : String) (as : List (Source × VE.Formula)) :
    dropTarget t (sourced U as) = sourced U (dropTarget t as)

/-! The plain adapter: Γ is the Background, then the asserted units' formulas in unit order. -/

def PlainParts.without (p : PlainParts) (t : String) : PlainParts := { p with units := p.units.filter (·.1 != t) }

/-- Its reduced premises are its premises filtered, each with its source. -/
theorem PlainParts.sourced_without (p : PlainParts) (t : String) : (p.without t).sourced = dropTarget t p.sourced

/-- Source to formula: the reduced case's sources and Γ are the two columns of the filtered list, over the same
    environment and conclusion. -/
theorem PlainParts.without_columns (p : PlainParts) (t : String) :
    (p.without t).sources = (dropTarget t p.sourced).map (·.1) ∧
    (p.without t).Γ = (dropTarget t p.sourced).map (·.2) ∧ (p.without t).V = p.V ∧ (p.without t).ψ = p.ψ

/-! The zero-set adapter: Γ is the asserted units' formulas; the premises are `premisesU U Γ`. -/

def ZeroParts.without (p : ZeroParts) (t : String) : ZeroParts := { p with units := p.units.filter (·.1 != t) }

theorem ZeroParts.assertions_without (p : ZeroParts) (t : String) :
    (p.without t).assertions = dropTarget t p.assertions

theorem ZeroParts.sourced_without (p : ZeroParts) (t : String) : (p.without t).sourced = dropTarget t p.sourced

theorem ZeroParts.without_columns (p : ZeroParts) (t : String) :
    (p.without t).U = p.U ∧ (p.without t).E = p.E ∧ (p.without t).ψ = p.ψ ∧
    (p.without t).Γ = (dropTarget t p.assertions).map (·.2) ∧
    (p.without t).premises = (dropTarget t p.sourced).map (·.2)

/-! The enumerated adapter: one row per compatible choice, over the choice's filled document. `withoutAssertion`,
    `withoutAssertionN` and the theorems that leave the rules, sets and rule units unchanged are as in spec 6.1. -/

/-- Exactly the target's assertions go: every other entry stays, in order. -/
theorem sourcedAssertions_withoutAssertion (D : Doc) (u : String) (c : Choice)
    (hu : ∀ R ∈ D.sets, R.unit ≠ u) :
    sourcedAssertions (withoutAssertion D u) c = dropTarget u (sourcedAssertions D c)

/-- The support question's premises under choice `c`, each with its source. -/
def supportSourced (N : NDoc) (u : String) (c : Choice) : List (Source × VE.Formula) :=
  sourced (choiceU (withoutAssertionN N u) c) (sourcedAssertions (withoutAssertionN N u).D c)

/-- Its reduced premises are ask's row premises (`rowSourced`'s list) filtered, each with its source. -/
theorem supportSourced_eq (N : NDoc) (u : String) (c : Choice) (hu : ∀ R ∈ N.D.sets, R.unit ≠ u) :
    supportSourced N u c = dropTarget u (sourced (choiceU N c) (sourcedAssertions N.D c))

/-- No premise of the support question comes from the target. -/
theorem supportSourced_target (N : NDoc) (u : String) (c : Choice) (hu : ∀ R ∈ N.D.sets, R.unit ≠ u) :
    ∀ x ∈ supportSourced N u c, x.1 ≠ Source.unit u

/-- Source to formula: the second column is `premisesU` of the reduced choice document. -/
theorem supportSourced_premises (N : NDoc) (u : String) (c : Choice) :
    (supportSourced N u c).map (·.2) =
      VE.NormDefaults.Wire.premisesU (choiceU N c) (choiceDoc (withoutAssertion N.D u) c).2
end VE.Ask

namespace VE.Purposes
open VE.Ask (Lead Source Reason)

/-! The negative outcomes, one theorem per adapter (SR 8), each over that adapter's row on its Γ after `dropTarget`. -/

/-- The plain adapter: `notEnough` is a checked failure of entailment from everything else the text says. -/
theorem notEnough_sound_plain (p : VE.Ask.PlainParts) (t : String) (r : VE.Ask.PlainRow) (reasons : List String)
    (ru : String → List String) (cs : List Source) (why : Option VE.Ask.Reason)
    (hr : VE.Ask.PlainRowOk.{u} p.V ((VE.Ask.dropTarget t p.sourced).map (·.2)) p.ψ r)
    (h : supportOf reasons ru r.lead cs why = .notEnough) :
    r.lead = .notNecessarily ∧ ¬ VE.Entails.{0} p.V ((VE.Ask.dropTarget t p.sourced).map (·.2)) p.ψ

theorem ruledOut_sound_plain (p : VE.Ask.PlainParts) (t : String) (r : VE.Ask.PlainRow) (reasons : List String)
    (ru : String → List String) (cs : List Source) (why : Option VE.Ask.Reason)
    (hr : VE.Ask.PlainRowOk.{u} p.V ((VE.Ask.dropTarget t p.sourced).map (·.2)) p.ψ r)
    (h : supportOf reasons ru r.lead cs why = .ruledOut) :
    r.lead = .no ∧ VE.Ask.Consistent p.V ((VE.Ask.dropTarget t p.sourced).map (·.2)) ∧
      VE.Entails.{u} p.V ((VE.Ask.dropTarget t p.sourced).map (·.2)) (.not p.ψ)

/-- The plain adapter never splits (`plain_never_split`), so its support is never `notSettled`. -/
theorem notSettled_never_plain (r : VE.Ask.PlainRow) (reasons : List String) (ru : String → List String)
    (cs : List Source) (why : Option VE.Ask.Reason) : supportOf reasons ru r.lead cs why ≠ .notSettled

open VE.Readings VE.NormDefaults in
/-- The zero-set adapter: a checked situation of the conflict-free document in which everything else the text says
    is true and the claim is false. -/
theorem notEnough_sound_zero (p : VE.Ask.ZeroParts) (t : String) (r : VE.Ask.Row) (reasons : List String)
    (ru : String → List String) (cs : List Source) (why : Option VE.Ask.Reason)
    (hr : VE.Ask.RowOkU.{u} p.U ((VE.Ask.dropTarget t p.assertions).map (·.2)) p.ψ r)
    (h : supportOf reasons ru r.lead cs why = .notEnough) :
    r.lead = .notNecessarily ∧ ConflictFreeU.{u} p.U ∧ CounterU p.U ((VE.Ask.dropTarget t p.assertions).map (·.2)) p.ψ

open VE.Readings VE.NormDefaults in
theorem ruledOut_sound_zero (p : VE.Ask.ZeroParts) (t : String) (r : VE.Ask.Row) (reasons : List String)
    (ru : String → List String) (cs : List Source) (why : Option VE.Ask.Reason)
    (hr : VE.Ask.RowOkU.{u} p.U ((VE.Ask.dropTarget t p.assertions).map (·.2)) p.ψ r)
    (h : supportOf reasons ru r.lead cs why = .ruledOut) :
    r.lead = .no ∧ ConflictFreeU.{u} p.U ∧ ConsistentU p.U ((VE.Ask.dropTarget t p.assertions).map (·.2)) ∧
      EntailsU.{u} p.U ((VE.Ask.dropTarget t p.assertions).map (·.2)) (.not p.ψ)

open VE.Readings VE.NormDefaults in
theorem notSettled_sound_zero (p : VE.Ask.ZeroParts) (t : String) (r : VE.Ask.Row) (reasons : List String)
    (ru : String → List String) (cs : List Source) (why : Option VE.Ask.Reason)
    (hr : VE.Ask.RowOkU.{u} p.U ((VE.Ask.dropTarget t p.assertions).map (·.2)) p.ψ r)
    (h : supportOf reasons ru r.lead cs why = .notSettled) :
    r.lead = .notSettled ∧ ConflictFreeU.{u} p.U ∧
      VE.Ask.SplitU p.U ((VE.Ask.dropTarget t p.assertions).map (·.2)) p.ψ

open VE.Readings VE.NormDefaults in
/-- The enumerated adapter, per compatible choice: `notEnough` (E1) is a checked situation of the conflict-free
    document in which everything else the text says is true and the claim is false. -/
theorem notEnough_sound (N : NDoc) (t : String) (ψ : VE.Formula) (r : VE.Ask.Row) (reasons : List String)
    (ru : String → List String) (cs : List Source) (why : Option VE.Ask.Reason)
    (hr : VE.Ask.RowOk.{u} (VE.Ask.withoutAssertionN N t) ψ r)
    (h : supportOf reasons ru r.lead cs why = .notEnough) :
    r.lead = .notNecessarily ∧ ConflictFreeU.{u} (choiceU N r.choice) ∧
      CounterU (choiceU N r.choice) (choiceDoc (VE.Ask.withoutAssertion N.D t) r.choice).2 ψ

open VE.Readings VE.NormDefaults in
theorem ruledOut_sound (N : NDoc) (t : String) (ψ : VE.Formula) (r : VE.Ask.Row) (reasons : List String)
    (ru : String → List String) (cs : List Source) (why : Option VE.Ask.Reason)
    (hr : VE.Ask.RowOk.{u} (VE.Ask.withoutAssertionN N t) ψ r)
    (h : supportOf reasons ru r.lead cs why = .ruledOut) :
    r.lead = .no ∧ ConflictFreeU.{u} (choiceU N r.choice) ∧
      ConsistentU (choiceU N r.choice) (choiceDoc (VE.Ask.withoutAssertion N.D t) r.choice).2 ∧
      EntailsU.{u} (choiceU N r.choice) (choiceDoc (VE.Ask.withoutAssertion N.D t) r.choice).2 (.not ψ)

open VE.Readings VE.NormDefaults in
theorem notSettled_sound (N : NDoc) (t : String) (ψ : VE.Formula) (r : VE.Ask.Row) (reasons : List String)
    (ru : String → List String) (cs : List Source) (why : Option VE.Ask.Reason)
    (hr : VE.Ask.RowOk.{u} (VE.Ask.withoutAssertionN N t) ψ r)
    (h : supportOf reasons ru r.lead cs why = .notSettled) :
    r.lead = .notSettled ∧ ConflictFreeU.{u} (choiceU N r.choice) ∧
      VE.Ask.SplitU (choiceU N r.choice) (choiceDoc (VE.Ask.withoutAssertion N.D t) r.choice).2 ψ
end VE.Purposes

namespace VE.Purposes
open Lean VE.Ask (Lead Source Reason Row)

/-- The adapter ask selected (`VE.Ask.Run.routeOfDocument`), with what Lean decoded for it. -/
inductive Adapter
  | plain (p : VE.Ask.PlainParts)
  | zero (p : VE.Ask.ZeroParts) (case : Json)
  | enumerated (N : VE.Readings.NDoc)

def Adapter.route : Adapter → String
  | .plain _ => "plain" | .zero _ _ => "norm-defaults" | .enumerated _ => "readings"

/-- One answered row of a support request: the adapter's row, its reduced sourced premises under its choice, the
    environment its certificates replay in, the units of the rules on each predicate, and, for a yes or no lead, the
    certificate's conclusion (ψ or ¬ψ) and certificate. -/
structure SupportRow where
  row     : Row
  sources : List (Source × VE.Formula)
  E       : VE.Environment
  ru      : String → List String
  cert    : Option (VE.Formula × VE.Tableau.Certificate)

/-- SR 12: the row's verdict is `supportOf` over the row's reduced sources. -/
def SupportRow.verdict (reasons : List String) (x : SupportRow) : Support :=
  supportOf reasons x.ru x.row.lead
    (match x.cert with
     | some (φ, k) => VE.Ask.cited (x.sources.map (·.1)) (VE.Ask.usedPositions x.E (x.sources.map (·.2)) φ k)
     | none => [])
    x.row.reason

/-- A yes or no row rests on a certificate for the claim or its negation that replays on exactly the row's reduced
    premises; no other row has one. -/
def CertOk (ψ : VE.Formula) (x : SupportRow) : Prop :=
  (x.row.lead = .yes → ∃ k, x.cert = some (ψ, k)) ∧ (x.row.lead = .no → ∃ k, x.cert = some (.not ψ, k)) ∧
  (x.row.lead ≠ .yes → x.row.lead ≠ .no → x.cert = none) ∧
  ∀ φ k, x.cert = some (φ, k) → VE.Ask.replayOk x.E (x.sources.map (·.2)) φ k = true

/-- What a row claims, by adapter (SR 8): its sources are the adapter's sourced premises after `dropTarget`, and its
    row holds on that reduced Γ, so 6.2's theorems for the adapter apply to it. -/
def SupportRowOk (t : String) (ψ : VE.Formula) : Adapter → SupportRow → Prop
  | .plain p, x => p.ψ = ψ ∧ x.sources = VE.Ask.dropTarget t p.sourced ∧ x.E = p.V ∧ x.ru = (fun _ => []) ∧
      ∃ r : VE.Ask.PlainRow, x.row = r.toRow ∧ VE.Ask.PlainRowOk.{0} p.V (x.sources.map (·.2)) ψ r
  | .zero p case, x => p.ψ = ψ ∧ x.sources = VE.Ask.dropTarget t p.sourced ∧ x.E = p.E ∧
      x.ru = VE.Ask.zeroRuleUnits case ∧ x.row.choice = [] ∧
      VE.Ask.RowOkU.{0} p.U ((VE.Ask.dropTarget t p.assertions).map (·.2)) ψ x.row
  | .enumerated N, x => x.sources = VE.Ask.supportSourced N t x.row.choice ∧
      x.E = VE.Readings.Wire.fullEnv (VE.Ask.withoutAssertionN N t) x.row.choice ∧
      x.ru = VE.Ask.ruleUnits N.D x.row.choice ∧ VE.Ask.RowOk.{0} (VE.Ask.withoutAssertionN N t) ψ x.row

/-- A support request Lean accepted (7.3) and replayed on the reduced context. -/
structure SupportAsked where
  request  : Json
  adapter  : Adapter
  target   : String
  reasons  : List String
  ψ        : VE.Formula          -- the target's formula, the case's conclusion
  replayed : List Row            -- the adapter's rows on the reduced context, in its order
  rows     : List SupportRow

/-- The support request of ask's runner, on the adapter `route` names. -/
def replaySupport (route : String) (j : Json) : Except String SupportAsked

/-- SR 12: what an accepted support request establishes. The target and reasons are the request's; the case has no
    premises and assumes no reading; the answer's rows are the replayed rows, as lists, so order and multiplicity
    both count; the replayed choices are exactly `[[]]` on a one-choice adapter and exactly the compatible choices
    on the enumerated adapter; and every row satisfies its adapter's `SupportRowOk` and `CertOk`. With
    `SupportRow.verdict`, each row's verdict is `supportOf` over that row's reduced sources, and 6.2's theorems apply
    to it. -/
theorem support_wire_sound (route : String) (j : Json) (a : SupportAsked) (h : replaySupport route j = .ok a) :
    a.request = j ∧ a.adapter.route = route ∧
    (j.getObjValD "support").getObjValD "target" = .str a.target ∧
    (j.getObjValD "support").getObjValD "reasons" = Json.arr (a.reasons.map Json.str).toArray ∧
    ((j.getObjValD "case").getObjValD "premises" = .null ∨
      (j.getObjValD "case").getObjValD "premises" = Json.arr #[]) ∧
    ((j.getObjValD "case").getObjValD "assumed" = .null ∨
      (j.getObjValD "case").getObjValD "assumed" = Json.arr #[]) ∧
    a.rows.map (·.row) = a.replayed ∧
    (match a.adapter with
     | .enumerated N => ∀ c, VE.Readings.Compatible N.D c ↔ c ∈ a.replayed.map (·.choice)
     | _ => a.replayed.map (·.choice) = [[]]) ∧
    ∀ x ∈ a.rows, SupportRowOk a.target a.ψ a.adapter x ∧ CertOk a.ψ x

/-- The `support` member: each row's choice and verdict, then the lines. -/
def supportJson (a : SupportAsked) (lines : List String) : Json

theorem supportJson_rows (a : SupportAsked) (lines : List String) :
    (supportJson a lines).getObjValD "rows" = Json.arr (a.rows.map fun x =>
      Json.mkObj [("choice", VE.Readings.choiceJson x.row.choice),
        ("verdict", renderSupport (x.verdict a.reasons))]).toArray
end VE.Purposes
```

How they bind (spec 6.2): `alone_sound`, `together_exact` and `without_sound` take `E`, `srcs` and `P` from the
row: `p.V` and `dropTarget t p.sourced` (plain); `p.E` and `dropTarget t p.sourced` (zero-set);
`fullEnv (withoutAssertionN N t) c` and `supportSourced N t c` (enumerated). `ru` is `fun _ => []`, `zeroRuleUnits
case` and `ruleUnits N.D c` respectively.

### 2.7 `Shapes.lean` (PE-6): claims about the document's own rules

Not part of the item-1 statement review. S3's owner is decided at synthesis round 2: discourse's validity claims or
purposes (DRI 2(e)). PE-6 does not start until then, and until Q3, the evidence repair below and the acts ×
alternatives lift (act-phrases; PE-6's gate, PE-R3) are settled. The
sketch stays as draft 1 wrote it, with three corrections:
- **An explicit, audited rule list (E4).** `Claim.rules` is a list of W1 rule names written in the claim and checked
  by the targeted audit. It is not resolved through scope's governed lists or discourse's content names. Those
  compositions are refused today: `scope@0` refuses `alternatives@0` and `ve.discourse@1`
  (`ve/profile_table.json:127-131`). With the explicit list, PE-6 needs neither composition.
- **`supportOfFollowable` is removed (Astra rounds 2–3).** FOLLOWABLE's `conditional_on` is `res.src.labels`
  (`Alternatives/Run.lean:220`): every source label, not the ones the certificate used. Filtering it cannot say which
  reason the argument used, and `followable_sound` establishes the conclusion under its assumptions, not that the
  shape claim supplied the stated argument. Until alternatives exposes the premises a FOLLOWABLE certificate used (the
  alternatives owner's change, named as a dependency), PE-6 shows the existing conditional FOLLOWABLE result
  ("FOLLOWABLE, conditional on …"), separately from the author's explanation, and the link gets no support verdict.
- **No bytes are claimed (E4).** Draft 1's "+306 B" is struck; any figure comes back only with its audit.

```lean
import VE.Norms.Tree
import VE.Purposes.Decl

namespace VE.Purposes.Shapes
open VE.Norms (Tree Node Role)

def roleOf (T : Tree) (p : String) : Option Role := (T.regulated.find? (·.name == p)).map (·.role)
def nodeOf (T : Tree) (n : String) : Option Node := T.nodes.find? (·.name == n)

/-- A rule forbids: it denies a permission (`sign = false` on a permission-role predicate). -/
def forbids (T : Tree) (n : String) : Bool :=
  match nodeOf T n with
  | some r => !r.sign && roleOf T r.pred == some .permission
  | none => false

/-- A rule requires: it imposes an obligation (`sign = true` on an obligation-role predicate). -/
def requires (T : Tree) (n : String) : Bool :=
  match nodeOf T n with
  | some r => r.sign && roleOf T r.pred == some .obligation
  | none => false

inductive Shape where
  | eachForbids                 -- "Each of <the rules> forbids an action."
  | noneRequires                -- "None of <the rules> requires an action."
  | oneForbids (pred : String)  -- "One of <the rules> forbids <the act of pred>."
  | noneRequiresAct (pred : String)  -- "None of <the rules> requires <the act of pred>." (PE-R3: the denied aim)
  deriving DecidableEq, Repr

structure Claim where
  unit  : String         -- the unit or part that states it
  rules : List String    -- W1 rule names, written in the claim and audited (E4); no list resolution
  shape : Shape
  deriving DecidableEq, Repr

def holds (T : Tree) (c : Claim) : Bool :=
  !c.rules.isEmpty && c.rules.all (fun n => (nodeOf T n).isSome) &&
  match c.shape with
  | .eachForbids => c.rules.all (forbids T)
  | .noneRequires => c.rules.all (fun n => !requires T n)
  | .oneForbids p => c.rules.any (fun n => forbids T n && (nodeOf T n).map (·.pred) == some p)
  | .noneRequiresAct p => c.rules.all (fun n => !(requires T n && (nodeOf T n).map (·.pred) == some p))

theorem holds_eachForbids (T : Tree) (c : Claim) (hu : (T.nodes.map (·.name)).Nodup) (h : c.shape = .eachForbids) :
    holds T c = true ↔ c.rules ≠ [] ∧
      ∀ n ∈ c.rules, ∃ r ∈ T.nodes, r.name = n ∧ r.sign = false ∧ roleOf T r.pred = some .permission

theorem holds_noneRequires (T : Tree) (c : Claim) (hu : (T.nodes.map (·.name)).Nodup) (h : c.shape = .noneRequires) :
    holds T c = true ↔ c.rules ≠ [] ∧ (∀ n ∈ c.rules, ∃ r ∈ T.nodes, r.name = n) ∧
      ∀ n ∈ c.rules, ∀ r ∈ T.nodes, r.name = n → ¬ (r.sign = true ∧ roleOf T r.pred = some .obligation)
end VE.Purposes.Shapes
```

**The denied aim (PE-R3).** "They do not direct Claude to always act so as to prevent such attacks" (u0171.s02)
denies one aim, not every requirement: `noneRequires` says more than the source. The claim is
`noneRequiresAct <the prevention predicate>` ("None of <the rules> requires <the act of pred>"), which states only that
no listed rule is an obligation on that act. `noneRequires` is kept for a source that denies every requirement.

**The tree PE-6 reads (PE-R3).** PE-6 reads the norms tree after acts' split: the tree the document's check builds
under `acts@0`, which every constitution document carries, so the hard-constraint rules are named as that tree names
them and the targeted audit checks each name against it.

A shape claim's unit carries no formula. Its status is set from `holds`, as discourse's validity claims are a
checker verdict (`discourse.md` 4.7): CHECKED with a true line, or CHECKED with a false line ("The text says each of
these rules forbids an action; rule <n> does not."). It is expressed either way, as a false assertion is. Whether
W2's loader accepts an explicit CHECKED status on a unit without content is open question Q3 (7).

### 2.8 Cross-unit links (PE-4)

`Ref.mention m` resolves through the discourse manifest (owner discourse; nothing re-resolved here). The mention's
form must be `demonstrative`, `navigation`, `section_ref` or `pronoun`, its target kind `unit` or `anchor`, and it must
lie inside the link's marker part, so it is a location binding in a unit without meaning (`discourse.md` 1.4). A
`pronoun` is accepted only with a `unit` target, as main's discourse binds it (`discourse.md` 178-179, 188-190;
PE-R4); a pronoun naming an entity stays refused. An
`anchor` reason ("we discuss why below") gives `notChecked .noFormula`.

PE-4 replaces PE-1's `sameUnit` explicitly (A3). On the *resolved* sides it checks what PE-1 checks on parts:
- every resolved unit exists in the checked view;
- its kind agrees with the marker's slot (`markerAgrees`);
- coverage (`covered`, `markerHonest`);
- nonfactivity: every resolved unit on the unstated side, and every candidate of an active reading set on it, is
  `Kind.inert` (D8a);
- (pe-rev, PE-R11) `packsInert`: no pack premise is sourced to a resolved unit on the unstated side, or to its
  parent. Before PE-4 a mention there never reaches fault 6a, because fault 6 refuses it first;
- (pe-rev, PE-R8) `shownUnder` over the resolved target units, so a line shows only under their candidates that
  hold the target; and `unlinkedActive` over the marker's unit and each resolved side's unit, so `scopeLine` names
  every part there that no link names and that is not inert. Until PE-4 lands, a link joins parts of one unit only,
  and that unit's parts are all the scope the line can leave out.

`sole` is compared on resolved reason identities (A6), so two mentions of the same units are one reason.

```lean
/-- *new*: the units a side names, mentions resolved by `VE.Discourse` (an anchor contributes none). -/
def sideUnits (D : VE.Discourse.Manifest) (s : List Ref) : Except String (List String)

/-- *new*: every (target unit, reason unit) pair of one link, sides resolved by `sideUnits`. -/
def targetReasonPairs (D : VE.Discourse.Manifest) (L : Link) : List (String × String)

/-- Affirmed `because` links as edges from each reason unit to each target unit. -/
def edges (D : VE.Discourse.Manifest) (B : Block) : List (String × String)

/-- Links on a cycle of affirmed reasons. They are reported, not refused (R 3.3); `VE.Closure.reachEval`, no new
    closure. -/
def circular (D : VE.Discourse.Manifest) (B : Block) : List String

theorem mem_circular (D : VE.Discourse.Manifest) (B : Block) (i : String) :
    i ∈ circular D B ↔ ∃ L ∈ B.links, L.id = i ∧ L.relation = .because ∧
    L.polarity = .affirmed ∧ ∃ t r, (t, r) ∈ targetReasonPairs D L ∧
      VE.Closure.Reachable .star (fun a b => (a, b) ∈ edges D B) t r

/-- The summary: the rules (units of kind `norm`) that are the target of at least one affirmed link. -/
def rulesWithReason (U : Units) (D : VE.Discourse.Manifest) (B : Block) : List String
```

## 3. Batches

Each batch lists: shared files (every file outside its new files), what it deletes or does not duplicate, fixtures,
seeded bugs (each in a language whose product code the batch changes, with the test that must fail), and its bar.
Generated files are never edited by hand: `uv run python tools/regen_generated.py --write`, and `--resolve` after a
merge.

### PE-M0. Re-measure the need on the full unit text (measurement, 2 h, model-free, any time)

Run R 2.1's markers over `source[span]` of every unit of the newest constitution and UDHR runs, plus the PF and RSP
ledgers once `infra/usecase-safetyfw` produces them. Classify the new units by R 2.1's kinds (a)–(i) and split the
constitution by USECASE-WEIGHTS.tsv's core ranges. The script lives in the pilot directory, not the repository.
**Output**: a table that replaces R 2.1's excerpt floors. **Trigger**: if any kind's full-text bytes exceed its
excerpt bytes by more than 50%, the DRI revisits PE-3 to PE-7's order. *Estimate*: about 89 units, 17,627 B on the
constitution (the brief's scan).

### PE-0p. UDHR aim rules u101 and u102 (pilot, 3 h, no product code; the first batch)

Convention (this design's ruling on R 2.1 kind c): an aim rule ("Education shall be directed to …", "shall
promote …", "shall further …") is an obligation on the course of education whose act keeps the source's own verb.
The end is a W2 open term with decider `unstated`. No causal claim is asserted: whether education in fact promotes
understanding is not part of the rule. This follows u100a's audited encoding (`readings/u100a.unassigned.ve.md`)
exactly, including its decider `unstated`. That is contradiction C2 with judgment-terms D7: PE-0p, a W2 pilot without
`judgments@0`, keeps W2's `unstated`. Any batch under `judgments@0` follows judgment-terms D7's admission convention
instead (JT-R3 stands; E7, DRI 3(b)).

Fixtures, in `translation-part03.ve.md`, beside u100a and u100b:
- **u101** [9285,9389): predicate `education_promotes_understanding_required` (`course_of_education`), regulated
  obligation, default `unspecified`, act "{0} promote understanding, tolerance and friendship among all nations,
  racial or religious groups". Open term `understanding_tolerance_and_friendship_among_groups` (factors: "what
  promoting understanding, tolerance and friendship among all nations, racial or religious groups requires").
  Rule guard `top`; meaning `{"open": [...]}`.
- **u102** [9389,9475): predicate `education_furthers_un_peace_activities_required`, act "{0} further the
  activities of the United Nations for the maintenance of peace". Open term
  `activities_of_the_united_nations_for_the_maintenance_of_peace`. The act is fixed as "{0} further the
  peace-keeping activities of the United Nations": the ledger notes "'for' is reserved", so the source's "for the
  maintenance of peace" is not used, and the audit judges the rewording (statement check, synthesis round 2).

**Bar** (pre-registered):
1. part03 loads and checks: premises `model`, CONFLICT-FREE.
2. No reading set is added, so the whole declaration stays within its 64 joint readings.
3. Every carried probe is byte-identical.
4. The targeted audit judges u101 and u102 FAITHFUL.
5. A unit the lint or the audit refuses stays UNFORMALISED, with the reason recorded.

**Answer key (synthesis round 2).** PE-0p's fixtures are the frozen answer key of this plan. Expected, verbatim:
- the document (part03): premises `model`; CONFLICT-FREE;
- **u101**: status `OPEN`; regulated obligation `education_promotes_understanding_required` on `course_of_education`,
  default `unspecified`, guard `top`; act "{0} promote understanding, tolerance and friendship among all nations,
  racial or religious groups"; meaning `{"open": ["understanding_tolerance_and_friendship_among_groups"]}`; the open
  term's record: name `understanding_tolerance_and_friendship_among_groups`, factors ["what promoting understanding,
  tolerance and friendship among all nations, racial or religious groups requires"], `decided_by` `unstated`;
- **u102**: status `OPEN`; regulated obligation `education_furthers_un_peace_activities_required` on
  `course_of_education`, default `unspecified`, guard `top`; act "{0} further the peace-keeping activities of the
  United Nations"; meaning `{"open": ["activities_of_the_united_nations_for_the_maintenance_of_peace"]}`; the open
  term's record: name `activities_of_the_united_nations_for_the_maintenance_of_peace`, `decided_by` `unstated`.

Quality: key partial (two units).

**Shared files**: none in the repository; the pilot run directory and its ledger only, between pilot windows.
**Deletes or does not duplicate**: nothing; no new predicate pattern. **Seeded bugs**: none (no product code).
*Estimate*: **UDHR +190 B** (1.74% of 10,916 B), or +104 B with u101 alone, claimed only when the audit passes.

### PE-1. The `VE.Purposes` core (Lean, 5 h, new files only; after the statement review of 2.1–2.6 and its gate check, SR 14)

**New files**: `lean/VE/Purposes/{Decl,Wire,WellFormed,Examples}.lean` (2.1–2.3), and route admission's
`lean/VE/Route/Inert.lean` (namespace `VE.Route.Admission`; `Kind.inert` and its four theorems, D8a). The latter is a
new file in the owner's namespace, so `Route/Admission.lean` itself is not edited. With PE-1, the one-sentence S5
amendment (D3) is proposed to `docs/spec/document.md`'s owner. If an existing W2 fixture or a merged plan uses the
opposite slot order, the existing order wins and this plan adapts (DRI 2(g)).

**Fixtures** (`Examples.lean`, `#guard` and `example`; every expected value below was computed by `#eval` in the
spec's stub, spec 9, except F7e, F7f and F8, which draft 3 derives by hand, spec 11.1). Each source is the sentence
alone; offsets are bytes into it.
- **F1, u0146.s01** "We want Claude to figure out the most plausible interpretation of a query in order to give the
  best response." (109 B).
  - Parts: p1 [0,73) kind `norm`; p2 [73,86) " in order to " kind `["causal","in order to","norm","explanation"]`;
    p3 [86,109) kind `explanation` (a purpose is not stated as achieved, D8a).
  - All three are UNFORMALISED: p1 with reason `attitudes-E3`, p3 with `judgment-best-response`, p2 with
    `purposes-side-unformalised`.
  - Link l1: `inOrderTo`, affirmed, plain, reason [p3], target [p1], marker p2.
  - Expected: `check = .ok ()`. Mutants:
    - swap the marker's two slot kinds → "unit p2 is not marked as this link's reason or purpose";
    - give p3 kind `asserted`, `norm` or `definition` (and the marker the matching slot) → "link l1 would make a
      purpose or a denied reason a premise or a rule" (A2: `norm` and `definition` were let through by draft 1);
    - give p3 an active reading set with an `asserted` candidate → the same refusal; with only inert candidates →
      `.ok ()`;
    - set p2 LABELLED → "link words are counted as covered, but what they link is not formalised";
    - drop l1 → "a unit marked as a reason or purpose has no link".
- **F2, u0019.s01** "Although we're asking Claude to prioritize not undermining human oversight of AI above being
  broadly ethical, this isn't because we think being overseeable takes precedence over being good."
  - Parts: target "Although … broadly ethical, " (kind `norm`), marker "this isn't because " (kind
    `["causal","because","explanation","norm"]`), reason "we think … being good." (kind `explanation`: denied, so
    never stated).
  - Link: `because`, denied, plain. Expected `.ok ()`. Mutants: share `sole` → "link … denies a reason and also says
    how much of the reason it is"; reason kind `asserted` → "link … would make a purpose or a denied reason a
    premise or a rule".
- **F3, [176186,176365)** "We think this kind of self-endorsement matters not only because it is good for Claude
  itself but because values that are merely imposed on us by others seem likely to be brittle."
  - Parts: target, marker " not only because ", reason 1, marker " but because ", reason 2.
  - Links: l1 `notSole` (reason 1), l2 `plain` (reason 2). Expected `.ok ()`. Mutants: l1 `sole` → "link l1 says
    this is the only reason, and the text gives another"; drop l2 → "a unit marked as a reason or purpose has no
    link" (its marker is left unlinked; `notSole` itself needs no other link, A4).
- **F4, [125508,125756)** "… warrant caution before acting unilaterally—not because Claude's reasoning is
  inherently worse than a human's, but because Claude's situation differs in important ways:".
  - Links: one denied, one affirmed. Expected `.ok ()`.
- **F5, synthetic.** A `prevents` link → the decoder refuses it (D8). A link whose sides are parts of two different
  units, a part on both sides, or a mention (before PE-4) → "must join distinct parts of one unit".
- **F6, synthetic (A4).** "A, partly because B." with one link: `.ok ()` for every share (`plain`, `sole`,
  `partly`, `notSole`).
- **F7, synthetic (A4).** A `sole` link and a second affirmed link with the same reason → `.ok ()` (a duplicate is
  not a second reason); with a different reason → refused as F3's mutant; a *denied* second link with a different
  reason → `.ok ()`.
  - **F7e, F7f (SR 5).** The second link with the same reason and share `notSole` (F7e) or `partly` (F7f) → "link l1
    says this is the only reason, and the text gives another" (text 8).
- **F8, synthetic (SR 6).** h "A because B, C." (15 B): p1 [0,1) "A" `asserted`; p2 [1,10) " because "
  `causal because asserted asserted`; p3 [10,12) "B," and p4 [12,15) " C." `asserted`; l1 `because`, affirmed,
  plain, reason [h.p3, h.p4], target [h.p1], marker h.p2 → `.ok ()`, and the reason quotes "B, C.".
  - **F8a.** Reason [h.p4, h.p3], reversed → "link l1 has a side whose parts are not adjacent and in order".
  - **F8b.** p3 [10,11) "B", p4 [11,12) "," `unformalised x`, p5 [12,15) " C."; reason [h.p3, h.p5], split by p4,
    which the link does not list → the same text.
- **F2c, F2d, F2e (PE-R11, D8a).** F2 with `packSources = ["u0019.s01.p3"]`, a pack premise sourced to the denied
  reason (for example a weighing rank edge or an attitude written from it) → "link l1 has a side the text does not
  state, and a pack takes a premise from it" (fault 6a). F2d: `packSources = ["u0019.s01"]`, its unit → the same.
  F2e: `packSources = ["u0019.s01.p1"]`, the target part → `.ok ()`.
- **F9, u0014.s03's shape (PE-R8, PE-R7).** f "In order to be safe, we believe every model should be honest." (61 B):
  p1 [0,12) "In order to " `causal "in order to" norm explanation`; p2 [12,21) "be safe, " `explanation`; p3 [21,61)
  `norm`, under an active set with readings [`report`, `rationale`, `limiting`, `in-attitude`] of kinds
  [`asserted`, `norm`, `norm`, `asserted`]; l1 `inOrderTo`, affirmed, plain, reason [f.p2], target [f.p3], marker
  f.p1. Expected: `check = .ok ()`; `shownUnder = [("f.p3", ["rationale", "limiting"])]`; `unlinkedActive = []`.
  Mutant: every candidate of kind `asserted` → `shownUnder = [("f.p3", [])]` (PE-2 withholds the lines).
- **F10, u0289.s05's shape (PE-R8, PE-R9).** g "Sometimes we may choose to keep a promise because we value our
  word." (68 B): p1 [0,10) "Sometimes " `asserted` (a hedge's formula over the sentence, pending); p2 [10,41)
  `exposition`; p3 [41,50) " because " `causal because exposition exposition`; p4 [50,68) `exposition`, under D6 (c)'s
  set [`reason`, `motive`], both `exposition`, content pending; l1 `because`, affirmed, plain, reason [g.p4], target
  [g.p2], marker g.p3. Expected: `check = .ok ()`; `shownUnder = []` (the target part has no set);
  `unlinkedActive = ["g.p1"]`.

**Shared files**: generated only. `lean/VE.lean` (lean-roots, merge union), `lean/VE/Audit.lean` and the statement
inventories (lean-audit-manifests, lean-statements), via `regen_generated.py --write`.

**Deletes or does not duplicate**: it reads W2 kinds as the checked view decoded them (no second kind parser, no
second loader), reuses `relations` (D9), and adds the nonfactivity predicate once, in its owner's namespace.

**Seeded bugs** (Lean):
- `shareOk` counting a duplicate link as a rival: F7's duplicate case must fail.
- `markerAgrees` ignoring slot order: F1's swap mutant must fail.
- `nonfactive` checking only `asserted`: F1's `norm`-purpose mutant must fail.
- `nonfactive` ignoring reading candidates: F1's candidate mutant must fail.
- `markerHonest` always true: F1's LABELLED mutant must fail.
- `Kind.inert` admitting `norm`: `normRole_inert`'s proof breaks, and so does F1's mutant.
- `shareOk` ignoring the other link's share (SR 5): F7e must fail.
- `sideAdjacent` checking only that the parts touch, not their order (SR 6): F8a must fail.
- `sideAdjacent` checking only the order, not that each part starts where the previous one ends: F8b must fail.
- `packsInert` reading only the parts, not their unit (PE-R11): F2d must fail.
- `packsInert` always true: F2c must fail.
- `holdsTarget` reading the reason's slot instead of the target's (PE-R8): F9's `shownUnder` must fail.
- `unlinkedActive` keeping inert parts or parts another link names: F10's value, and F3's `[]`, must fail.

**Bar**: every statement of spec 1–4 proved; `python3 lean/audit.py` clean; all fixtures and mutants as stated.
*Estimate*: 0 B.

### PE-2. The `purposes` block in the document mode, relayed and shown (Lean + Python, 6 h; after PE-1)

**Before PE-2 admits the profile** (step 3 of the order):
- **The checked-view refactor** (owner: the document model; one item in the document-mode queue, DRI 2(d)):
  `checkDocSetsView` and its theorems `checkDocSetsView_answer`, `checkDocSetsView_rows` and
  `checkDocSetsView_candidates` (spec 5.1), and (pe-rev) the view's candidate names (`checkDocSetsView_readings`,
  PE-R8) and pack sources (`checkDocSetsView_packs`, PE-R11). It changes no answer: `checkDocSets` becomes its first
  component.
- **The C6 wire-contract item** (owner: wire-contract; DRI 3(c)): the diagnostics contract for `purposes@0`, in
  shadow mode and off the verdict and identity paths, as S10's "contract first" rule asks
  (`wire-contract-PLAN.md` 471). PE-2 does not wait for the contract to be switched on.
- **Nonfactivity**: `VE.Route.Admission.Kind.inert` and its theorems, delivered by PE-1.

**Lean**:
- `lean/VE/Service/DocumentPurposes.lean` (2.5), `lean/VE/Purposes/Verdict.lean` (`Support`, its wire form and
  `eligible`, which reads only the checked view, so the section names each eligible link's question; spec 12,
  choice 4) and `lean/VE/Purposes/English.lean` (2.4, `says` and the `notChecked` lines only, and (pe-rev, PE-R8)
  `linkLines`, `underLine` and `scopeLine`: a link's lines only under the candidates that hold its target, and a line
  naming the parts it leaves out). The section row gains `under` (spec 5.4).
- The document mode's dispatch calls `checkDocPurposes` instead of `checkDocSets`: one line.
- `profileTable` gains the `purposes@0` row, with composition proved by `checkDocPurposes_base`.
- `VE.Discourse.Loader`'s `metadataKeys` gains the row `("purposes", false)` through definitions' PD-1a mechanism
  (2.5); no `profileKeys` map.
- The `layerCovers` entries for `purposes@0` (2.5, PE-R5).
- The document response shape gains the optional member `purposes`, with its encoder theorem (ROUTE-RECIPE steps
  2–3).
- `tools/layer_policy.py` gains a layer-4 row for `VE.Purposes.{Verdict, English, Support}` (they import `VE.Ask`).

**Python**:
- `ve/document/source.py` `_split` loses its hand-written `allowed` set and reads the Lean-exported list instead.
  The list is a new generated file `ve/document_metadata.json`, written by a Lean main like `ProfilesMain.lean` and
  registered as one `Generated` row in `tools/regen_generated.py`.
- The document relay binds the `purposes` member to the request: every link id, ref id and marker id exists in the
  request's block and units; no row is empty or extra.
- `tests/test_relay_binding_inventory.py` gains the rows for the `purposes` member (rd-9 inventory, D9; DRI 3(d)).
- `ve/document/render.py` prints Lean's line for a marker part instead of its kind description; (pe-rev, PE-R8) a
  row with `under` only beside those readings, and a marker whose links' `lines` are all empty keeps its kind
  description.
- (pe-rev, PE-R8) The binding checks `under`: exactly one entry per target part with an active set, each naming
  candidates of that part's set, and `lines` empty exactly when some entry's `readings` is empty; otherwise
  `CheckerUnavailable`.
- No Python logic decides anything.

**Fixtures**: F1–F8 as documents through `ve document check`; recorded route cases (`tests/route_case_recorder.py`);
`tests/test_purposes_lean.py` (new); `tests/test_purposes_answer.py` (new, ROUTE-RECIPE step 7: each member dropped,
emptied, retyped, duplicated, reordered, an index pushed out of range → `CheckerUnavailable` or no visible change).
The line fixtures of spec 9.7, as `#guard`s in `Examples.lean`:
- no rendered line contains two consecutive spaces (SR 1);
- `together ["u5.p1","u5.p3"] []` prints "sentence 5" (SR 2, E-b);
- F3 with both reasons asserted and p5 cited quotes p5, never "sentence N" for the claim's own sentence (SR 2, E-c);
- F8's reason quotes "B, C." (`sideText_eq`, SR 6);
- (pe-rev, PE-R8) F9's lines: `says`, `verdict`, then "This holds only under these readings of "we believe every
  model should be honest.": rationale and limiting."; F9's all-`asserted` mutant: `lines = []`; F10's lines: `says`,
  `verdict`, then "The quotes above leave out "Sometimes" from the same sentence, which may limit what they say.";
  F1 to F8 keep their lines (no set on a target, no unlinked active part).

**Shared files**:
- Lean: `lean/VE/Service/Protocol.lean` (or wherever the document mode dispatches; one line);
  `lean/VE/Compose/Dispatch.lean` (one row and its `layerCovers` entries); `lean/VE/Discourse/Loader.lean` (one
  `metadataKeys` row); `lean/ResponseShape/Schemas/Document.lean`; `lean/ResponseShape/Encoders/Document.lean`.
- Python: `ve/document/source.py`; `ve/document/render.py`; the document relay
  (`uv run python tools/repo_map.py route document` lists it); `tools/regen_generated.py` (one row);
  `tools/layer_policy.py` (one row); `tests/test_relay_binding_inventory.py` (rows).
- Generated, never hand-edited: `ve/profile_table.json`, `ve/backends/lean_service_schema/document.json`,
  `ve/document_metadata.json`, the Lean roots, audit and inventories.

**Deletes**: `_split`'s hand-written key set, so the metadata keys get one owner.

**Seeded bugs**:
- Lean: `checkDocPurposes` changing a coverage row (`checkDocPurposes_base`'s test must fail).
- Python: the relay accepting a link id that is not in the request (the binding fuzz test must fail); `_split`
  accepting `purposes` without `purposes@0` (the metadata test must fail).

**Bar**: ROUTE-RECIPE steps 2–7; every existing document fixture byte-identical without `purposes@0`
(`checkDocPurposes_absent`); F1–F8 lines as in spec 2.3 and 9.7. *Estimate*: 0 B alone. From now on, a unit with a reason can
be claimed with its link once its sides are expressible.

### PE-3. Source-word rows and authored wordings (Lean rows, 4 h; after PE-2, `en-sw`, ET-5's "since" row, PE-E1, PC-1)

**Rows in english-lean's catalogue** (`lean/VE/EnglishGrammar/SourceWords.lean`, en-sw's row type; rows only, C1,
DRI 3(e)):
- the D2 markers, each with its reading-set generator per D6, its distinguishing situation and its authored-text
  refusal with rewrite (D11). "since" is not a new row: its reason sense extends ET-5's canonical "since" row
  (A6);
- the share words ("only", "solely", "simply", "just", "partly", "in part", "not merely", "not only", "not just").

The D11 wordings are registered as `purposes@0` profile wordings in the owner of wordings, as `alternatives@0`'s and
`events@0`'s are, so the author lint does not judge them.

**Layer coverage (PE-R10, 2.5)**: the row batch adds `judgments@0` to the `purposes@0` row's `layerCovers` entries,
with 2.5's composes argument, because PE-3's generator is the first to emit D6 (a)'s limiting candidate and its bound
judgment (`Dispatch.lean`, one row's entries).

**Fixtures**:
- u0146.s01 as the reading set {rationale; limiting; in-attitude} (D6 (a), PE-R7: "We want Claude to …" is an
  attitude whose content holds the rule; `in-attitude` pending, attitudes' slot). The distinguishing situation is one
  in which figuring out the most plausible interpretation would not serve the best response: required under
  rationale, not required under limiting.
- (PE-R10) 2.5's fixture: a synthetic rule in u0146.s01's shape, `limiting` holding the bound judgment, on a list
  with `documents@1`, `judgments@0`, `purposes@0` and `readings@1`: admitted, no E1, the answer without the member
  byte-identical.
- [142485,142713) "… not because it's told to, but because it genuinely cares …" as the attachment reading set, with
  the motive candidate without content (UNKNOWN for any verdict that depends on the choice).
- (PE-R9) Synthetic "Sometimes we may choose to keep a promise because we value our word." (F10's source): D6 (c)'s
  second frame, the set {reason; motive} on the reason's part, the motive candidate without content. Synthetic "We
  decided to keep the promise because we value our word.": no D6 (c) frame, so the named GAP `motive_frame`, the
  marker part `unformalised`, and no link.
- Authored "Claude does not refuse because the user is rude." refused, with both rewrites.
- The inline rows (SR 4): authored "Every request from a user is logged because every request from a user is a
  message." is one MIXED unit with an affirmed, plain `because` link from p3 to p1; "… only because …" gives `sole`
  and "… partly because …" gives `partly`. Authored "Claude refuses not only because the user is rude." is a negation
  before an inline "because" and is refused with the "not … because" rewrite.

**Shared files**: `SourceWords.lean` and the wording owner's file, in the english-lean queue (SYNTHESIS 4.1 item 7)
after en-sw, in landing order; `lean/VE/Compose/Dispatch.lean` (the `judgments@0` entries of the `purposes@0` row,
PE-R10). **Does not duplicate**: no catalogue of its own (DRI decision 2026-10-28 18:15Z).
**Seeded bug** (Lean): the "not … because" row generating one candidate (its fixture must fail); (pe-rev) the
"in order to" row beside an attitude generating only {rationale; limiting} (u0146.s01's fixture must fail).
*Estimate*: 0 B alone.

### PE-4. Cross-unit links, cycles and the summary (Lean, 5 h; after PE-2)

2.8.

**Fixtures**:
- u0019.s05 "This is why we want Claude to currently prioritize human oversight above broader ethical principles."
  (reason: the preceding units of u0019 through a `demonstrative` mention).
- u0222.s06 "This is why we are currently asking Claude to prioritize broad safety over its other values."
- u0213.s04 "… and we discuss why below." (an `anchor` reason).
- [130557,130799) "This is partly because … and partly because …" (two `partly` links, cross-unit target).
- Resolved-side checks: a mention on a purpose side that resolves to an `asserted` unit is refused (nonfactivity);
  one that resolves to a unit of the wrong kind is refused (`markerAgrees`); two links whose mentions resolve to
  the same units are one reason for `sole`.
- The UDHR preamble. Reasons u003–u010, target u013a, marker u011 "Now, therefore," (17 B, LABELLED, claimed). One
  link per reason kind shares the marker. The purpose ", to the end that …" is marked inside u013ba.
- A synthetic two-unit cycle, reported in `circular`.
- **u0094.s02's shape (PE-R4).** "Rather, they're meant to assist Claude in forming its own holistic judgment about how
  to balance … in order to avoid being overcompliant …": the link `meant to` whose target side is the pronoun "they",
  a `pronoun` mention with a `unit` target (the preceding unit), accepted and resolved by discourse. The inner purpose
  ("in order to avoid being overcompliant") sits inside a "how to" complement, which has no event at PE-7b's {0}: it is
  a named GAP `nested_purpose` (owner purpose-explanation, PE-7b, once its event argument can be the complement's act,
  after AP-3), never plain content. A pronoun mention whose target is an entity is refused (`sideUnits`).

**Shared files**: `lean/VE/Compose/Dispatch.lean` (the `purposes@0` row admits `ve.discourse@1`, with its
composition proof); the document response shape (the summary member). Reads `VE.Discourse` without editing it.

**Does not duplicate**: anaphora (discourse) and closure (`VE.Closure`).

**Seeded bugs** (Lean): `mem_circular`'s `circular` missing self-loops; `sideUnits` accepting a pronoun naming an
entity; nonfactivity skipping resolved mentions (each fixture must fail).

**Risk**: the constitution translation is `ve-document@1`, and discourse needs `@2`. The fixtures run as part
documents until the translation moves. *Estimate*: 0 new B; u010 and u011 (149 B, claimed) gain their role.

### PE-5. The support check (Lean + one relay hunk, 6 h; after PE-2, `feature/q1-4b` and the support-context review)

2.6, and `verdict`'s other lines and `supportLines` in `English.lean`. Question-answering's reduced context
(`dropTarget`, `PlainParts.without`, `ZeroParts.without`, `withoutAssertion`, `supportSourced` and their theorems)
lands in `VE.Ask` as one hunk owned by question-answering (DRI 2(b)). The support wire (`replaySupport`,
`support_wire_sound`) lands in `Support.lean`, and ask's runner gains the one hunk that calls it (2.6).

**Fixtures** (spec 9.6; draft 1's S1 is replaced, because its first sentence restated the reason and so made the
verdict depend on which of two equal premises the certificate used). Each names its adapter (SR 9). The plain
fixtures share one pinned environment (SR 10): `relational-fol@0` with `documents@1` and `purposes@0`, and no
`norms@0` and no `readings@1`. One sort, `item`, which may be empty (P0); unary predicates `request`, `from_user`,
`message` and `logged`. ψ (u2.p1) is `∀x:item. request(x) ∧ from_user(x) → logged(x)` and ρ (u2.p3) is
`∀x:item. request(x) ∧ from_user(x) → message(x)`. M1 is `{i1}` with request, from_user, message and logged true; M2
is `{i1}` with request, from_user and message true and logged false. Γ′ is the Background, then the listed units'
formulas in unit order. PE-5 records each certificate's bytes from the producer, as `tools/ask_fixtures.py` records
ask's.
- **S1 (plain).** "Every message is logged." (`∀x:item. message(x) → logged(x)`) and "Every request from a user is
  logged because every request from a user is a message." Γ′ = [u1, ρ]; a `certificate` for ψ using u1 and u2.p3; a
  `model` M1. The proof cites the reason and sentence 1: `together ["u1"] []`, "VE checked that this reason is
  enough to conclude the claim together with sentence 1."
- **S2 (plain).** The same without sentence 1: Γ′ = [ρ]; a `countermodel` M2; `notEnough`, with M2's situation.
- **S3 (plain; SR 10).** S1's u2, with u0 "Some request is from a user." (`∃x:item. request(x) ∧ from_user(x)`) and
  u1 "No request from a user is logged." (`∀x:item. request(x) ∧ from_user(x) → ¬logged(x)`). Γ′ = [u0, u1, ρ]; a
  `negation` certificate for ¬ψ using u0 and u1; a `model` M2. `ruledOut`, decided from everything else the text
  says, not from the whole document, which contradicts itself.
- **S3′ (plain; SR 10).** S3 without u0. Γ′ = [u1, ρ]; a `countermodel` M2, which contains a qualifying, unlogged
  request. With no qualifying request both universals hold, so no negation certificate exists: `notEnough`. Never
  `notSettled`, which `plain_never_split` rules out on the plain adapter.
- **S4.** A link to a rule: `notChecked .ruleTarget`; no request is sent.
- **S5 (plain).** S1 with the producer's budget exhausted (a `model` M1 only): `unknown noResult`, with ask's reason.
- **S6 (plain; E2).** Sentence 1 replaced by "Every request is logged." (`∀x:item. request(x) → logged(x)`): a
  `certificate` for ψ using u1 only; `without ["u1"] []`, "VE checked that the claim follows from sentence 1 without
  this reason."
- **S7 (zero-set; E2).** `norms@0` under `norm-defaults@0`; a norm unit u3 "Logging a message is required." (an
  obligation on `logging_required(item)` under the guard `message(x)`); ψ is `∀x:item. request(x) ∧ from_user(x) →
  logging_required(x)`. A proof that uses the rule names its unit: `together ["u3"] []` (`zeroRuleUnits`). One that
  uses a definition names it ("together with the definition of adult").
- **S8 (plain; Astra round 3).** S1 plus u3 with ψ itself. The target unit is never cited, and the formula-equal unit
  may be.
- **S9 (enumerated; SR 3, SR 9).** `readings@1`, `norms@0` and `norm-defaults@0`; S2's u2 (sentence 1) and u3
  (sentence 2) with the open set `rs_u3`: "Some request is a message" or "Some message is logged". Both rows are
  `notEnough` with a countermodel; one group and one line, which names the witness row's reading although the
  verdicts coincide: "…: S, reading sentence 2 as "Some request is a message"."
- **S9b (enumerated; 12, choice 5).** S9 with candidate 0 "Every message is logged": two groups, each line starting
  with ask's R1 clause ("If sentence 2 means "Every message is logged", VE checked that this reason is enough to
  conclude the claim together with sentence 2.").
- **S10 (enumerated by profiles; SR 11).** A soft-chain document (`soft-norms@0` under `norm-defaults@0`, with
  `readings@1`) with a default rule that has an exception, and an eligible target. Its support request gets ask's
  existing refusal for the same case, word for word (`admitNDFull`'s "InvalidInput: norm-defaults document is not
  well formed"). The fixture replays ask on the same case and compares the two texts.
- **S11 (zero-set; SR 10).** `norms@0` under `norm-defaults@0`, with `documents@1` and `purposes@0`, no `readings@1`;
  the vocabulary above plus `checked` and `logging_required` on `item`. A norm unit u1 "Logging a message is
  required." (an obligation on `logging_required(item)` under the guard `message(x)`, default `unspecified`), and u2
  "Logging every request from a user is required because every request from a user is checked.": ψ is
  `∀x:item. request(x) ∧ from_user(x) → logging_required(x)` and the reason `∀x:item. request(x) ∧ from_user(x) →
  checked(x)`. Γ′ = [the reason];
  conflict packages; a `split`: base model `{i1}` (request, from_user, checked true; message false), with fillings
  that set `logging_required`'s unsaid entry at i1 to true and to false. `notSettled`, with the split's situation.
- **S12 (enumerated; SR 13).** S9 with seven further two-candidate open sets on other units, 128 compatible choices:
  refused with ask's `ResourceLimit` text from `replayError`, with no support rows and no verdict.
- **S13, S14 (enumerated; SR 12).** S9's request with the case's `premises` `[ψ]`, or with `assumed`
  `[["rs_u3", 0]]`: each refused with "InvalidInput: the case does not ask this question (premises or assumed
  readings)".
- **E-f (`rfl`; SR 9).** Over the flattened parts u1, u2.p1 (the target) and u2.p3, `withoutAssertion … "u2.p1"`
  keeps u2.p3 and u1: sources [u1, u2.p3], exactly `dropTarget "u2.p1"` of the original. `PlainParts.without p
  "u2.p1"` keeps the same two units.

**Shared files**: one hunk in ask's runner, `lean/VE/Ask/Run.lean` (`askCase` takes `support` in place of `question`
and calls `replaySupport`, SR 7), and the `support` answer member; one hunk in `VE.Ask` (the reduced context); its
response shape and encoder; the Python ask relay (sends `support`, binds the answer); generated schemas;
`tests/test_relay_binding_inventory.py` (rows, D9; DRI 3(d)).

**Does not duplicate**: no prover and no "reasons of an answer" code. `usedPositions`, `cited`, `sourced`,
`ruleUnits` and `lead_sound` are reused unchanged, and premise assembly stays with question-answering.

**Seeded bugs**:
- Lean: `named` treating `.rules` as machinery (S7 must fail: `alone` instead of `together ["u3"]`).
- Lean: `supportOf` returning `alone` without a cited reason (S6 must fail).
- Lean: `withoutAssertion` keeping the target (`supportSourced_target`'s fixture must fail).
- Lean: `PlainParts.without` dropping the whole parent unit u2 instead of the part u2.p1 (E-f's `rfl` fixture and S1
  must fail).
- Lean: `replaySupport` accepting a case with `premises` (S13 must fail).
- Lean: `supportLines` dropping the reading suffix when all rows agree (S9 must fail).
- Python: the relay showing `support` for a link whose target or reasons differ from the request (the binding fuzz
  test must fail).

*Estimate*: 0 B on the pinned pilots now. The 3 argument units (411 B) and PF's Safeguards claims become claimable
when their sides are.

### PE-6. Claims about the rules' own shape; the hard-constraint argument (Lean + pilot, 6 h; after PE-5, ET-1's audit, S3's owner, Q3, the evidence repair, the acts × alternatives lift)

2.7. **Gates** (E4, DRI 2(e)): S3's owner, decided at synthesis round 2 (discourse validity claims or purposes); Q3
(an explicit CHECKED status on a unit without content); and the evidence repair (alternatives exposes the premises a
FOLLOWABLE certificate used, or PE-6 keeps showing the conditional result on its own). PE-6 does not start before
all three. **Gate (PE-R3, statement check):** main's `acts@0` row refuses `alternatives@0` ("acts@0 with
alternatives@0 is not implemented", `ve/profile_table.json:77`), and the pilot part document holds both. PE-6 does not
start until the owner of `acts@0`'s row (act-phrases) lifts that refusal for this list with its own composes argument;
if act-phrases does not take it, the combination is a named GAP (owner act-phrases) and PE-6 withdraws its claim on
this unit kind.

**Pilot part document**: ET-1's component (`alternatives@0`, `documents@1`, `norms@0`, `relational-fol@0`) plus
`acts@0` (the tree after acts' split, PE-R3) and `purposes@0`, with these fixtures:
- **u0171.s01** [105881,106028), 147 B: shape claims `eachForbids` and `noneRequires` over the seven hard-constraint
  rules. The rule list is written in the claim as the seven W1 rule names and checked by the targeted audit (E4).
  It needs no scope or discourse composition, both of which `scope@0` refuses today.
- **u0171.s02** [106028,106187), 159 B: `oneForbids <the bioweapons uplift predicate>` and
  `noneRequiresAct <the attack-prevention predicate>` (PE-R3; `noneRequires` says more than the source).
- **u0172.s01** [106602,106721), 119 B, ET-1's.
  - Split into reason part "Because hard constraints are restrictions on Claude's actions," (a shape claim,
    `eachForbids`) and target part "it should always be possible to comply with them all." (ET-1's FOLLOWABLE),
    with the link `because`.
  - The link gets `notChecked`; no support verdict is derived from `conditional_on` (2.7). The reader sees the
    existing conditional result separately: "FOLLOWABLE, conditional on …", as alternatives words it.

**Bar**:
1. Every shape claim `holds`, or its false line is shown and the targeted audit judges that right.
2. The targeted audit judges u0171.s01 and u0171.s02 FAITHFUL, and their explicit rule lists right.
3. u0172.s01's link line and the separate FOLLOWABLE line are judged faithful to "Because …, it should always be
   possible …", without saying that the reason was checked.
4. The seven rules are read, never edited. They stay in the hard-constraint queue (SYNTHESIS 4.4). PE-6 starts from
   the translation as the queue's latest step left it. If a step has changed a rule's sign or role, PE-6 waits.

**Shared files**: `lean/VE/Compose/Dispatch.lean` (the `purposes@0` row admits `alternatives@0` and `acts@0`); the pilot
directory. **`acts@0` in PE-6's row (PE-R3), composes argument:** `holds` is a function of the tree alone and a shape
claim's unit carries no formula, so the claim adds a status line and changes no other unit's premise, verdict or
status; the list's own answer is the base answer, as `checkDocPurposes_base` states for the other rows.
**Does not duplicate**: no followability proof (`followable_sound` is reused); no list resolution (scope or
discourse).

**Seeded bugs** (Lean): `forbids` ignoring the role (an obligation with `sign = false` counted as forbidding; the
u0171 fixture must fail); `holds` accepting a rule name that is not in the tree.

*Estimate*: none claimed (E4). Draft 1's "+306 B" is struck, and any figure returns only with its audit.
Fidelity for u0172.s01's 119 B, which ET-1 claims.

### PE-7b. Purposes of acts on events (Lean rows + pilot, 5 h; after the C21 bridge, ET-5, JT-5r, AP-3, events' `packSources_complete`)

**Gate** (C21, DRI 3(a)): a named, audited bridge batch, for events and judgment terms in documents and for
speech-acts × `documents@1`. Synthesis round 2 names it: the bridge PE-7b waits for is speech-acts' `documents@1`
lift, after commands' CI-2 (owner speech-acts; commands-imperatives' plan draft 3 carries C21 for CI-7b). Until it
lands, a purpose clause on an instruction is refused under `speech-acts@0`, never read as plain content, and main's
refusal stays. CI-7's purpose integration waits for the same bridge.

**Writer rule (PE-R2).** Until that bridge exists, a purpose that belongs to an instruction is a named GAP (owner
speech-acts, C21's `documents@1` lift), never plain content: never an atom over an "instructing event" or a
`purposes` link under `speech-acts@0`. Fixture from u0058.s04's shape ("… would probably assume it was intended to
avoid giving the impression of authoritative advice …"): the purpose of the manager's instruction is recorded as
that GAP.

**A purpose that is only being considered (PE-R6).** The bridge does not cover it, and this plan withdraws it from
its claim on an instruction's purpose (8, boundaries). A purpose inside a "whether" or "which" complement ("Claude
should consider whether the instruction was intended to … or if it was intended to …", u0077.s03's shape) is
asserted by the text in neither alternative: `Polarity` has only `affirmed` and `denied`, and an affirmed link's line
("The text gives this purpose for …") would overstate it. It is commands-imperatives' question object, recorded as a
named GAP `considered_purpose` (owner commands-imperatives; its row "question object, polar or single-wh", CI-E3
hypothesis A, `commands-imperatives-PLAN.md` 12.2 (a); request row in 8), with no `purposes` link and no atom over an
instructing event. C21 alone gives this kind no route in such a document: the lift removes only main's
`speech-acts@0` × `documents@1` refusal, and main still refuses `speech-acts@0` beside `acts@0`, `ve.discourse@1`,
`readings@1`, `scope@0` and `soft-norms@0` (`ve/profile_table.json` at `d8f58bf3b`, lines 25, 78, 118, 138, 150),
with profile-composition's grid keeping the discourse, readings and scope cells `g→X`. Fixture (writer rule, 4):
u0077.s03's shape, the two considered purposes recorded as that GAP.

The profile wording "{0} is aimed at {1}" is registered in the owner of wordings. It is a binary judgment term
between an event sort and an outcome sort, with a decider.

**The outcome argument (PE-R1).** {1}'s sort is `outcome`, which purpose-explanation owns and declares in
`VE.Purposes`: an outcome description, one constant per described outcome (for example `generating_revenue`), with no
internal structure and no event roles. It is what the act is aimed at, not an event that occurred, so it borrows no
events-time-causation sort; {0} keeps events' event sort. Numbered fixture **PE7b-1**, from u0275.s04's shape
("… in deploying Claude to users and operators in order to generate revenue …"): an event `e` of events' sort with
`deploys(anthropic, claude, e)`, the outcome constant `generating_revenue : outcome`, and the unit
`is_aimed_at(e, generating_revenue)`, a bound judgment term with decider `unstated`; expected (after
judgment-terms' backlog row `syn2code-judgment-terms-1`, which makes JT-1 admit `unstated`; until then main's
`Decl.lean` refuses it): admitted, the unit OPEN, the line "The deploying is aimed at generating revenue." with its judgment legend line.

**Fixtures**:
- u0185.s05 "Concealing material information … in order to gain market advantage or influence policy." (with
  scope's list item);
- UDHR u114 "… any act aimed at the destruction of any of the rights …" (fidelity);
- PE7b-1 (u0275.s04's shape, above).

**Shared files**: the english-lean wording owner's file (queue); the `purposes@0` row admits `events@0`
(`Dispatch.lean`); `judgments@0` is already admitted by PE-3 (PE-R10). `events@0` is a pack, so its `layerCovers`
entries carry D8a's pack obligation, `packSources_complete` for `events@0` (PE-R11), proved by events' owner; without
it those lists stay refused. **Does not duplicate**: event sorts and roles (events-time-causation; "other plans
add roles", SYNTHESIS 2.8). *Estimate*: 0 B alone; u0185.s05's 154 B once scope's list and events land.

### Experiments (pre-registered)

- **PE-E1. Purpose role, "not … because", attachment and display** (3 h; Sonnet 5.5 as the human proxy, authorised
  by DRI 4 when PE-E1 runs; after PE-1's statements, before PE-3 writes rows). 30 items, drawn with
  `random.Random("PE-E1")`:
  - the 7 kind-(a) units, u087 and u111 (u111's item tests the reading only; its encoding stays rights' `L29`);
  - 6 negated or contrastive "because" units: u0019.s01, [125508,125756), [142485,142713), u0038.s05,
    [176186,176365), [130557,130799);
  - 5 attachment units: u0025.s03, u0227.s04, u0019.s05, [54694,54981), [53286,53443);
  - 10 display-line items from 2.4, with questions such as "Does VE say this reason is true?" and "Does VE say the
    rule serves this purpose?".

  **Bar** (A4, DRI 4): PE-E1 may add reading sets and reword lines; it never removes a reading. A kind-(a) unit where
  at least 30% of readers choose "limits the rule" becomes a reading set {rationale; limiting} (with `in-attitude` beside an attitude, D6 (a)) if it is not one
  already. A D6 reading set is never reduced to one reading because readers agree. Agreement thresholds do not
  justify deleting a supported reading; a reduction needs a textual argument for that unit, recorded in its
  fidelity audit. Each display line needs at least 90% correct answers, or it is reworded before PE-3. Model results
  are early evidence, not proof about human readers.
- **PE-E2. Motive rules** (4 h; model-free writing plus one blind audit).
  - Write 10 units with an open relation "<agent> does <act> out of <motive>", decider named or `unstated`: the 5
    kind-(g) constitution units, the 2 RSP motive rules ("simply because we are unable to achieve them", "merely
    because it is sensitive"), [53286,53443), and 2 drawn from PE-M0's new units.
  - **Bar**: at least 7 of 10 judged FAITHFUL by an auditor who did not write them. Then a motive batch (wording rows
    and the attachment reading's content) is planned. Otherwise motives stay residual and the reason is recorded.
    The batch also needs ET-D2 for an agent's own act.
- **PE-E3. Means-end transmission** (2 h, model-free). Count units in the constitution, UDHR, PF and RSP where the
  text states a goal rule and elsewhere that an act is necessary for that goal. **Bar**: 5 or more units start a
  design batch for a stated, printed transmission convention. Otherwise the question is closed and VE never derives
  a rule from a purpose.
- **PE-E4. Safety-case arguments** (2 h, model-free; after `infra/usecase-safetyfw`'s ledgers). Count PF and RSP
  "because" arguments whose target is an assertion and both of whose sides are expressible after PE-5. **Bar**: 5
  or more units become PE-5b fixtures and claims. Otherwise record the count.

## 4. Fixtures from the pilots, in one table

| Fixture | Unit | Batch | Expected |
|---|---|---|---|
| aim rule | U u101, u102 | PE-0p | OPEN obligations; audit FAITHFUL; +190 B claimed at the audit |
| purpose on a want or rule | C u0146.s01 | PE-1, PE-3 | link `in order to`; a `norm`, `definition` or `asserted` purpose refused; reading set {rationale; limiting} kept |
| denied reason | C u0019.s01 | PE-1 | link denied; line "The text says this is not the reason for …" |
| not only … but | C [176186,176365) | PE-1 | `notSole` plus `plain`; `sole` with the second link refused |
| not because … but because | C [125508,125756) | PE-1 | denied plus affirmed |
| partly, alone; a duplicate link | synthetic F6, F7 | PE-1 | `.ok ()` (A4); a different reason under `sole` refused |
| This is why | C u0019.s05, u0222.s06 | PE-4 | cross-unit through a demonstrative mention; resolved sides checked |
| we discuss why below | C u0213.s04 | PE-4 | anchor reason; `notChecked .noFormula` |
| preamble | U u003–u013bb | PE-4 | recitals → proclamation via u011; "to the end that" purpose |
| `sole` with `notSole`, same reason | synthetic F7e | PE-1 | refused, text 8 (SR 5) |
| a reversed or split side | synthetic F8a, F8b | PE-1 | refused, fault 4a (SR 6) |
| enough with | synthetic S1 | PE-5 | plain; `together ["u1"] []`, the target removed |
| ruled out, and not enough without existence | synthetic S3, S3′ | PE-5 | plain; `ruledOut`; `notEnough` with a checked countermodel (SR 10) |
| follows without the reason | synthetic S6 | PE-5 | plain; `without ["u1"] []` (E2) |
| another unit's readings | synthetic S9, S9b | PE-5 | enumerated; reading clauses as ask's (SR 3) |
| soft document | synthetic S10 | PE-5 | ask's refusal, word for word (SR 11) |
| not settled | synthetic S11 | PE-5 | zero-set; `notSettled` from a checked split (SR 10) |
| past 64 readings | synthetic S12 | PE-5 | ask's `ResourceLimit`, no rows (SR 13) |
| shape of the hard constraints | C u0171.s01, s02 | PE-6 | `eachForbids`, `noneRequires` (s01), `oneForbids` and the denied aim `noneRequiresAct` (s02, PE-R3) over an explicit audited list of acts' split tree; no bytes claimed |
| the hard-constraint argument | C u0172.s01 | PE-6 | link `notChecked`; the conditional FOLLOWABLE result shown separately |
| limiting purpose | U u111 | — | rights' `L29` (PE-7a removed) |
| act with a purpose | C u0185.s05, U u114; PE7b-1 (C u0275.s04's shape) | PE-7b | "is aimed at" with the outcome sort `outcome` (PE-R1), after the C21 bridge |
| purpose of an instruction | C u0058.s04's shape | PE-7b's writer rule | a named GAP (C21's bridge), never plain content (PE-R2) |
| pronoun mention; nested purpose | C u0094.s02's shape | PE-4 | `pronoun` with a unit target accepted; the "how to" purpose a named GAP `nested_purpose` (PE-R4) |
| layer coverage | a constitution part document with `acts@0`, `definitions@0`, `documents@1`, `purposes@0` | PE-2 | admitted, no E1; answer without the member byte-identical (PE-R5) |
| a pack premise from an unstated side | C u0019.s01 (F2c, F2d, F2e) | PE-1 | sourced to the denied reason or its unit: refused, fault 6a; to the target part: `.ok ()` (PE-R11) |
| a purpose clause beside an attitude | C u0014.s03's shape (F9); C u0146.s01 | PE-1, PE-2, PE-3 | D6 (a)'s set gains `in-attitude`, pending (PE-R7); the line only under `rationale` and `limiting`, with its readings line; withheld when no candidate holds the rule (PE-R8) |
| a link inside a scope it cannot name | C u0289.s05's shape (F10) | PE-1, PE-2 | `unlinkedActive = ["g.p1"]`; the line names "Sometimes" as left out (PE-R8) |
| "may choose to … because"; another choice frame | C u0289.s05's shape; synthetic "decided to" | PE-3 | D6 (c)'s second frame, the motive pending; "decided to … because" a named GAP `motive_frame`, no link (PE-R9) |
| the limiting candidate's judgment | synthetic, u0146.s01's shape; list with `documents@1`, `judgments@0`, `purposes@0`, `readings@1` | PE-3 | `limiting` holds the bound judgment; admitted, no E1; answer without the member byte-identical (PE-R10) |
| a purpose only being considered | C u0077.s03's shape | PE-7b's writer rule | a named GAP `considered_purpose`, owner commands-imperatives (question object), no link (PE-R6) |
| motive | C u0227.s04, [142485,142713) | PE-E2 | research |

## 5. Dependencies and merge safety

| Depends on | Branch or owner | For | How this plan avoids conflicts |
|---|---|---|---|
| events decoder, then events in documents | `feature/et-4`; ET-5 | PE-7b | PE-7b waits; it adds wording rows, not files of `lean/VE/Events` |
| defeasible "should" | `feature/df-3` and later df items | the rule side of kinds (a), (e) | no code dependency; bytes only |
| the typed checked-document view | the document model (`VE.Service.Document`); one item in the document-mode queue (DRI 2(d)) | PE-2 | PE-2 reads `checkDocSetsView` and compiles nothing; the refactor changes no answer (`checkDocSetsView_answer`) |
| the wire contract for `purposes@0` | wire-contract owner; S10 "contract first" (C6, DRI 3(c)) | PE-2 | assigned before PE-2 admits the profile; shadow, off the verdict and identity paths; PE-2 does not wait for the switch |
| the nonfactivity predicate | route admission (`VE.Route.Admission`, DRI 2(c)) | PE-1, PE-4 | a new file in the owner's namespace (`Route/Inert.lean`); `Route/Admission.lean` is not edited |
| the reduced support context | question-answering (`VE.Ask`, DRI 2(b)) | PE-5 | one hunk in `VE.Ask`, reviewed with the support context; `Support.lean` calls it |
| the relay-binding inventory | rd-9 (`tests/test_relay_binding_inventory.py`; catalogue-owner item 4) | PE-2, PE-5 | rows added, in landing order (D9, DRI 3(d)) |
| act identity | `feature/ap-1bd`, AP-3 | PE-7b | waits |
| `VE.Ask` fixes | `feature/q1-4b` (blocked) | PE-5 | PE-5 lands after it; its code is in `Support.lean`; one hunk in `VE.Ask` and one in the runner |
| source-word catalogue | en-sw (ready) | PE-3 | rows only, in the english-lean queue (C1) |
| ET-5's "since" row | events-time-causation | PE-3 | "since" in its reason sense extends that one canonical row (A6, DRI 3(e)) |
| S3's owner | synthesis round 2 (DRI 2(e)) | PE-6 | PE-6 does not start before the decision |
| `acts@0` with `alternatives@0` (main refuses it, `ve/profile_table.json:77`) | act-phrases (the owner of `acts@0`'s row) | PE-6 | PE-6 waits for the lift; without it the combination is a named GAP and PE-6 withdraws its claim on this unit kind (PE-R3) |
| FOLLOWABLE's used premises | alternatives (`conditional_on` is every source label, `Alternatives/Run.lean:220`) | PE-6 | until alternatives exposes them, PE-6 shows the conditional result separately (2.7) |
| the speech-acts × `documents@1` bridge | speech-acts: its `documents@1` lift, after commands' CI-2 (C21, named by synthesis round 2; commands-imperatives' plan draft 3) | PE-7b, CI-7's purpose integration | both wait; until then a purpose clause on an instruction is refused under `speech-acts@0`, and the writer records it as a named GAP (PE-R2) |
| rights' `L29` | rights (`rights-PLAN.md` 217–223) | u111 / Art. 29(2) | PE-7a removed; purposes adds nothing there (DRI 3(f)) |
| judgment terms in documents | JT-5r (not started) | PE-7b | waits |
| attitudes E3 and AT-8 | `research/attitudes-p1` (refresh) | kind (a) targets that are wants | D7: the link attaches to whatever E3 yields |
| weighing's priorities | `research/weighing-p1` (refresh) | kind (e) targets that are rankings | the link's target is weighing's part |
| ET-1's audit | events-time-causation | PE-6 | PE-6 adds `purposes@0` to ET-1's part document; it does not edit u0165.s01–s07 |
| the document-mode queue | SYNTHESIS 4.2: AT-3b, SC-1b, QT-A4, ET-5, WG-4, ME-10 | PE-2 | joins in landing order. Its Lean is a new file `DocumentPurposes.lean`; the only edit to the mode is one dispatch line, rebased onto whichever entry function is current (today `checkDocSets`) |
| AR-10's table | `lean/VE/Compose/Dispatch.lean` | PE-2, PE-3 (`judgments@0`, PE-R10), PE-4, PE-6, PE-7b | one row, extended by later batches in landing order |
| the response-shape queue | `lean/ResponseShape/Schemas/Document.lean` | PE-2, PE-4 | one optional member per batch; schemas regenerated |
| sibling waves | `design/commands-imperatives`, `design/definitions`, commitments (queued) | boundaries (8) | none of their files is touched |

**Shared files, all batches**:
- **Lean**: `lean/VE/Service/Protocol.lean` (one line, PE-2); `lean/VE/Compose/Dispatch.lean` (one row, PE-2/3/4/6/7b);
  `lean/VE/Discourse/Loader.lean` (one `metadataKeys` row, PE-2); `lean/ResponseShape/Schemas/Document.lean`
  and `Encoders/Document.lean` (PE-2, PE-4); ask's runner `lean/VE/Ask/Run.lean` (one hunk, PE-5, SR 7) and the ask
  response shape; one hunk in `VE.Ask` (the reduced context, PE-5); `lean/VE/EnglishGrammar/SourceWords.lean` and the
  wording owner's file (PE-3, PE-7b). The checked-view refactor in `lean/VE/Service/Document.lean` is the document
  model's item, not this plan's.
- **Python**: `ve/document/source.py`, `ve/document/render.py`, the document relay (PE-2); the ask relay (PE-5); `tools/regen_generated.py` (one row, PE-2); `tools/layer_policy.py` (one row, PE-2);
  `tests/test_relay_binding_inventory.py` (rows, PE-2 and PE-5).
- **Pilot directories**: PE-0p, PE-6, PE-7b, between pilot windows, with `changed_units` for the audit.
- **Generated, regenerated only**: `lean/VE.lean`, `lean/VE/Audit.lean`, `lean/statements.txt` and the other
  inventories, `ve/profile_table.json`, `ve/backends/lean_service_schema/*.json`, `ve/document_metadata.json` (new).

## 6. What is deleted or not duplicated

- **Not duplicated** (PE-2, synthesis round 2): the front-matter key. Lean's `metadataKeys` owns the keys, and the
  `purposes` row joins it by definitions' PD-1a mechanism; Python gets no copy of the row, and no `profileKeys` map is
  added.
- **Deleted from this plan** (draft 2): PE-7a (a second encoding of rights' `L29`, E3); `supportOfFollowable` (a
  support verdict without used-premise evidence); draft 1's `Units` from a second `compileUnits` call (A3); draft 1's
  `othersCited` (it hid rules and definitions, E2).
- **Not duplicated**: premise assembly stays with question-answering (the reduced context is `VE.Ask`'s); the "never a
  premise or rule" predicate is route admission's, proved from its leaf provenance; the checked units are the
  document model's view; sentence numbers, quotes, situations and UNKNOWN reasons are ask's and `VE.Words`'.
- **Not added**: a relation word. The three existing copies of the relation list (Lean, the generated schema enum,
  `ve/admission.py` `RELATIONS`, pinned by a test) stay as they are. A consolidation row is proposed: Python's
  `RELATIONS`, `ACTS`, `MODALITIES` and `ATOMIC_KINDS` should read the generated enum. That is for the consolidation
  pass, not this plan.
- **Reused, never rewritten**:
  - the "reasons of an answer" (`VE.Ask`) and the provers and certificates behind it;
  - closure (`VE.Closure`), anaphora (discourse) and governed lists (scope);
  - open terms (W2, `judgments@0`) and the source-word catalogue (english-lean);
  - causal links (events), attitude semantics (attitudes), priority semantics (weighing), derivations in papers
    (math-evidence);
  - FOLLOWABLE's proof and its own conditional wording (`alternatives@0`).
- **Python wording**: none added. Lean writes each line. Python prints Lean's line for a marker part instead of W2's
  kind description, so one relation is never worded twice on one screen.

## 7. Risks and open questions for the statement review

- **Q1. Entry point for PE-5** (settled by SR 7: ask's case). A readings-verdicts request alone cannot serve S1,
  because `Readings.routeOf` sends a document with no content-bearing reading set to `w2`, and the readings-verdicts
  replay serves only the enumerated route. So the support request is ask's request with `support` in place of
  `question`, answered on whichever of ask's plain, zero-set and enumerated adapters ask selects, with a formula in
  and no English parsing (2.6). The reduced context is `VE.Ask`'s.
- **Q2. `purposesUnits`** (settled by A3). It reads the document model's checked view after the status fold
  (`checkDocSetsView`); purposes compiles nothing. Draft 1's direct `Loader.compileUnits` call is gone: it throws on
  norm content and misses the folded statuses.
- **Q3. Shape-claim units** (a PE-6 gate). Does W2's loader accept an explicit `CHECKED` status on a unit without
  content? If not, PE-6 carries the claim as a unit content `{"shape": …}` under `purposes@0`, which touches the
  content decoder: another shared hunk, in the document-mode queue.
- **Q4. UDHR's 64-reading ceiling** (DRI 3(h)). PE-0p adds no reading set by design, and PE-7a is removed. Any later
  UDHR reading set for a purpose role (u087) needs a ceiling decision first.
- **Q5. Attitudes E3** may make many kind-(a) and kind-(e) targets reports, not rules. The link is unaffected (D7),
  but the bytes that later become claimable move with E3's answer.
- **Q6. "Since" and "as"** (settled for "since" by C1 and A6). The reason sense of "since" extends ET-5's canonical
  "since" row; "as" is a row of its own in PE-3. Readers' splits add reading sets, never remove one (D6).
- **Q7. Marker honesty and existing documents** (S4, DRI 2(f)). D4 applies only under `purposes@0`, so no existing
  document's coverage changes. A legacy LABELLED `causal` part with unformalised sides stays as it is until its
  document adds the profile. Extending D4 to every connective part is a W2 question for synthesis round 2.
- **Q8. Points the item-1 spec chose** (spec 12), as the statement review settled them. `sole` against a `partly` or
  `notSole` link with the *same* reason is refused (SR 5; duplicates with share `plain` or `sole` stay one reason).
  The reason parts of an eligible link must be stated, checked formulas. The support line names a part by its parent's
  sentence number, except a part of the target's own sentence, which it names by its quote (SR 2).

## 8. Shared pieces

**Reused (existing owners)**:
- W2's `causal` kind and MIXED parts (W2, `document.md`);
- W2 open terms and `judgments@0` (judgment-terms);
- discourse's `unit`, `anchor` and `rule` targets and content names (discourse);
- `VE.Ask`'s cited sources, `sourced`, `sourcedAssertions`, `ruleUnits`, its leads, reasons, sentence numbers,
  quoting rule, grouping and reading clauses, its three adapters (plain, zero-set, enumerated) with their bindings,
  replays and refusals, and its limit refusal `replayError` (question-answering, RD-3);
- `VE.Words.situation` (the situation wording);
- route admission's leaf provenance, the norm-role table (`Norms.Admission.normRole`) and the readings route's
  `inForce`, from which nonfactivity is proved;
- the document model's `RowUnit` rows and status fold;
- `alternatives@0`'s FOLLOWABLE with `conditional_on` and its own wording (alternatives; ET-1), shown, never
  re-derived;
- `VE.Closure` (closure; QS-1's adapters);
- AR-10's profile table;
- english-lean's source-word catalogue (en-sw) and ET-5's "since" row;
- events' sorts and roles (events-time-causation);
- attitudes' E3 and AT-8;
- scope's document-mode wrapper pattern (`checkDoc`, `checkDocSets_absent_unchanged`);
- the generated profile-table pattern (`ProfilesMain.lean` → `ve/profile_table.json`).

**NEW, with the owners the acting DRI assigned** (DRI 2; one owner each, the module that holds the data today):

- **S1. A link between source units that adds no premise** (`VE.Purposes.Link`, `Block`, `check`). Owner:
  `VE.Purposes` (DRI 2(a)). Closest existing: discourse's manifest (mentions, reading groups and constraints over
  units) and, outside VE, BMM's means–ends links. commitments, definitions, weighing, commands-imperatives and
  math-evidence use it and do not define their own link:
  - commitments: a commitment's stated reason (a trigger is never a purpose link: commitments' rule, synthesis
    round 2, N5);
  - definitions: "this is why we call it …";
  - weighing: a precedent's stated reasons;
  - commands-imperatives: the purpose clause of an instruction (after C21's bridge);
  - math-evidence: prose "hence" outside calculations.
- **S2. A support verdict over a certificate's cited sources** (`Support`, `supportOf`). **NEW under PLANS-INDEX D8**,
  as a new answer vocabulary over `VE.Ask.Lead` (E6). Owner: purposes (`Verdict.lean`, `Support.lean`; DRI 2(b)). Its
  lines reuse `VE.Ask`'s leads and reasons and `VE.Words` where the meaning is the same (spec 2.3). `Support` keeps
  its data type and renders through question-answering's D8 mapping table (synthesis round 2). Closest existing:
  `VE.Ask.cited` ("the reasons of an answer"). Possible users: math-evidence's derivations in prose, weighing's
  precedents, the safety-framework use cases. It is answered only through ask's three adapters, on which the soft
  premises are empty (SR 11). Support on soft documents waits until ask serves them; that extension is
  question-answering's, and doing it here would give soft replay a second owner.
- **S2a. The reduced support context** (`VE.Ask.dropTarget`, `PlainParts.without`, `ZeroParts.without`,
  `withoutAssertion`, `supportSourced`; `withoutAssertion D t` is `withoutUnits [t]` of the one shared adapter
  `VE.Ask.withoutUnits N X`, built by whichever of PE-1/PE-2 and definitions' PD-2 lands first). **NEW within S2, owned by question-answering** (`VE.Ask`), because premise
  assembly has one owner (DRI 2(b)). One reduction over sourced premises (`dropTarget`, SR 7), and one form of it per
  adapter. `Support.lean` calls it.
- **S2b. The nonfactivity predicate** ("never a premise or rule", `VE.Route.Admission.Kind.inert`). Owner: route
  admission (DRI 2(c)). Its theorems are proved from admission's leaf provenance, the norm-role table and the
  readings route's `inForce`. It applies to resolved mentions (PE-4) and to every reading candidate. Pack premises
  are covered by purposes' check `packsInert` and the pack obligation on `layerCovers` (D8a, PE-R11), not by this
  predicate.
- **S2c. The typed checked-document view** (`VE.Service.Document.CheckedView`, `checkDocSetsView`). **NEW under W2**,
  owned by the document model and exported after the status fold (DRI 2(d)). One refactor in the document-mode queue,
  before PE-2. Purposes compiles nothing.
- **S3. Claims about the document's own rules** (`VE.Purposes.Shapes`). Synthesis round 2 decides between discourse's
  validity claims (`discourse.md` 4.7) and purposes (DRI 2(e)). PE-6 does not start until then. Possible users:
  scope ("the hard constraints"), weighing ("hard constraints are not weighed"), commitments ("we will not weaken
  these rules").
- **S4. Link-word honesty in coverage** (D4). It applies under `purposes@0` only (DRI 2(f), Q7). Extending it to
  every connective part (attribution bridges, scope lead-ins) is a W2 question for synthesis round 2.
- **S5. W2's `causal` slot order** (D3). This is not a new abstraction; it pins an existing one. The one-sentence
  amendment to `docs/spec/document.md` goes in with PE-1. If an existing W2 fixture or a merged plan uses the
  opposite order, the existing order wins and this plan adapts, so no verdict changes (DRI 2(g)).

**Requests to other families (pe-rev).** Each states the slot this plan needs; none edits the other plan, and none
designs what fills the slot.

| Request | To | The slot | Until it lands |
|---|---|---|---|
| a considered purpose (PE-R6) | commands-imperatives | the alternatives of a question object ("whether … or if …"), row "question object, polar or single-wh" (CI-E3 hypothesis A, its plan 12.2 (a)), holding a purpose clause the text asserts in neither alternative; whether an alternative question is in that row's polar class is that plan's to state | a named GAP `considered_purpose`, owner commands-imperatives, no `purposes` link |
| a means-end relation inside an attitude (PE-R7) | attitudes | the content position of the holder's attitude node (AT-3a; an attitude candidate read at its node's content, PC-11's `KindReaderCovers`), holding a content-level purpose (D1) | D6 (a)'s `in-attitude` candidate is pending, its rows `unknown` |
| pack premises' sources (PE-R11) | the pack owners: weighing, attitudes, scales, events | the unit or part each premise in `X` formalises, exported in the checked view's `packSources` (`packSources_complete`, spec 5.1) | `purposes@0` covers no list holding that pack; the layer rule refuses it |
| candidate names and pack sources in the view (PE-R8, PE-R11) | the document model (S2c) | `CheckedView.readings` and `CheckedView.packSources` with their theorems (spec 5.1), in the same refactor | PE-2 does not start (S2c is before PE-2) |

**Contradictions and cross-plan rules** (DRI 3; for PLANS-INDEX section 4, which records them):
- **C21 (new).** CI-7 (commands-imperatives, `commands-imperatives-PLAN.md` 592–597) expects a purpose reader and
  goal-conditional integration, but `speech-acts@0` refuses `documents@1` (`ve/profile_table.json:18`). CI-7's
  purpose integration and PE-7b wait for a named, audited bridge batch. Synthesis round 2 names it: speech-acts'
  `documents@1` lift, after commands' CI-2. Until then a purpose clause on an instruction is refused under
  `speech-acts@0`; it is never read as plain content, and the writer records it as a named GAP (PE-R2). A purpose
  only being considered is outside C21: commands-imperatives' question object (PE-R6, PE-7b).
- **C2.** PE-0p follows u100a's `unstated`. Any batch under `judgments@0` takes judgment-terms D7's convention
  (JT-R3 stands).
- **C6.** A named wire-contract item for `purposes@0` (wire-contract owner, shadow, off the verdict and identity
  paths) is assigned before PE-2 admits the profile. PE-2 does not wait for the contract to be switched on.
- **D9.** PE-2 and PE-5 add rows to the rd-9 relay-binding inventory (catalogue-owner item 4).
- **C1.** PE-3 adds rows only to `SourceWords.lean` (en-sw); the reason sense of "since" extends ET-5's "since" row.
- **D8.** `Support` is registered as a NEW answer vocabulary (S2 above).
- **Rights.** u111 / Art. 29(2) belongs to rights' `L29` (`solely_for_permitted_purpose`); purposes adds nothing
  there.

**Boundaries** (confirmed by DRI 3(g)):
- **commands-imperatives**: owns what an instruction means; the purpose clause of an instruction is this plan's link,
  or a limiting condition by D6's reading question, once C21's bridge exists. (pe-rev, PE-R6) A purpose that is
  only being considered, inside a "whether" or "which" complement, is withdrawn from that claim: the text asserts
  neither purpose, so it is commands-imperatives' question object, a named GAP `considered_purpose` (PE-7b; request
  row above). C21 alone gives it no route in such a document.
- **definitions**: a "because" inside a definition's body is content, owned by events or judgment terms; "this is
  why we call it X" is this plan's link with a definition target. (pe-rev, C point) Under `purposes@0`,
  `markersLinked` refuses a part of kind `causal because …` or `causal in order to …` that marks no link, so such a
  causal "because", or any other family's unlinked causal "because", cannot carry main's `causal` label (u0133.s03):
  it takes its owner's kind, or `unformalised` with its reason. This is a refusal with a working route, recorded
  here; the check is unchanged.
- **commitments**: owns "we try to explain our reasoning". PE-4's summary ("the text states a reason for 12 of its 40
  rules") is a measurable fact a commitments check could cite, never a verdict that a commitment was kept.

## 9. The statement review's ruling → sections

The ruling (`manage-agents/debates/purpose-explanation-spec/DRI-RULING.md`) asks for every item in both documents.
The gate check (SR 14) reads this table and spec 13's together.

| Item | This plan | The spec |
|---|---|---|
| SR 1 (E-a: `without [] []`; no two spaces) | 2.4, PE-2 fixtures | 2.3, 9.7 |
| SR 2 (E-c before E-b) | 2.4, PE-2 fixtures, Q8 | 2.3, 9.7, 12 (choice 9) |
| SR 3 (reading clauses exactly as ask's) | 2.4, PE-5 (S9, S9b) | 2.3, 6.4, 9.6, 12 (choice 5) |
| SR 4 (E-e: inline rows; negation refused) | D11, PE-3 fixtures | 2.1, 2.2, 9.8 |
| SR 5 (E-d: `sole` against `partly`/`notSole`; F7e) | 2.3, PE-1 (F7e, F7f, seeded bug), 4, Q8 | 4.2, 4.4, 7.2, 9.2, 9.3, 12 (choice 2) |
| SR 6 (`sidesAdjacent`, `sideText_eq`, fault 4a, two fixtures) | 2.3, PE-1 (F8, F8a, F8b, seeded bugs), PE-2, 4 | 2.3, 4.2–4.4, 7.2, 9.2, 9.7, 12 (choice 10) |
| SR 7 (Q1 as ask's case; flattened parts; `dropTarget`) | 0, 2.6, PE-5 shared files, 5, Q1, 8 | 0, 6.1, 6.4, 9.6, 12 (choice 11) |
| SR 8 (adapter theorems in full; filtered premises; source to formula) | 2.6 (verbatim) | 6.1, 6.2 |
| SR 9 (fixtures name adapters; S9; E-f `rfl`) | PE-5 fixtures | 9.6 |
| SR 10 (S3, S3′, a split fixture; all pinned) | PE-5 fixtures (S3, S3′, S11, pinned environment), 4 | 9.6 |
| SR 11 (soft support deferred; no new text; S10) | 0, 2.6, PE-5 (S10), 4, 8 (S2) | 0, 6.1, 6.4, 7.3, 8, 9.6 |
| SR 12 (no premises or assumed; rows equal as lists; `support_wire_sound`) | 2.6 (verbatim), PE-5 (S13, S14, seeded bug) | 6.4, 7.3, 8, 9.6 |
| SR 13 (past 64: ask's `ResourceLimit`, no rows) | 2.6, PE-5 (S12), 4 | 2.3, 6.4, 7.3, 8, 9.6 |
| SR 14 (one gate check, then PE-1) | header, order step 2, PE-1 heading | header, 11.1 |

## 10. Synthesis round 2 and the fidelity-pilot revision (2026-10-31)

Applied from `manage-agents/debates/plan-synthesis-2/edits-purpose-explanation.md` (DRI-decided; sources: that
debate's `SYNTHESIS.md` sections 2 (Reduced context, Front-matter keys, Purpose bridge, Answer vocabulary), 3 (C21,
N5) and 5 (quality)) and `manage-agents/reviews/dri-decisions-20261031-fp-purpose-explanation.md` item 1 (the
fidelity pilot's REVISE, findings PE-R1 to PE-R5 only).

### 10.1 The synthesis round 2 edits

| Edit | What changes | Where |
|---|---|---|
| 1 (N5) | commitments' use of S1 is a commitment's stated reason; a trigger is never a purpose link | 8 (S1) |
| 2 | `VE.Ask.withoutAssertion D t` is the singleton case `withoutUnits [t]` of the one shared adapter `VE.Ask.withoutUnits N X` (with `replayReduced`, `withoutUnitsPlain`); whichever of PE-1/PE-2 and definitions' PD-2 lands first builds it, the other reuses it | 2.6, 8 (S2a); spec 6.1 |
| 3 | no `profileKeys` map; the `purposes` key joins `metadataKeys` in `VE.Discourse.Loader` by definitions' PD-1a mechanism | 2.5, PE-2, 5, 6 |
| 4 | choosing D6 (a)'s limiting reading is an author narrowing, recorded as such; VE never chooses it silently | D6 |
| 5 | PE-0p's fixtures are the frozen answer key with expected lines (quality: key partial) | PE-0p |
| 6 (C21) | the bridge PE-7b waits for is speech-acts' `documents@1` lift, after commands' CI-2 | 0, order, PE-7b, 5, 8 (C21) |
| 7 | synthesis round 2 confirms D7 as a boundary: attitudes' E3 and AT-8 own "we want Claude to …"; links attach to whatever E3 yields | D7 |
| 8 | `Support` keeps its data type and renders through question-answering's D8 mapping table | 2.4, 8 (S2) |
| 9 | PLANS-INDEX quality row: soundness reads "typed, unproved" until PE-1 proves the statements | the plan steward's row (`manage-agents/plans/PLANS-INDEX.md`), not this file |

### 10.2 The fidelity-pilot revision (PE-R1 to PE-R5)

| Finding | What changes | Where |
|---|---|---|
| PE-R1 | PE-7b's outcome argument has a declared sort, `outcome`, owned by purpose-explanation; numbered fixture PE7b-1 from u0275.s04's shape | PE-7b, 4 |
| PE-R2 | C21's owner and item named (speech-acts' `documents@1` lift, after CI-2; commands-imperatives' plan draft 3 carries C21); writer rule: until it exists, a purpose of an instruction is a named GAP, never plain content; main's refusal stays | PE-7b, 5, 8 (C21), 4 |
| PE-R3 | the denied-aim form `noneRequiresAct pred`, no stronger than the source; PE-6 reads the tree after acts' split; `acts@0` in PE-6's row with its composes argument; PE-6 gated on act-phrases lifting main's `acts@0` × `alternatives@0` refusal, else a named GAP and PE-6 withdraws its claim on this unit kind | 2.7, PE-6, 4, 5 |
| PE-R4 | PE-4 accepts main's `pronoun` mention with a `unit` target; a purpose inside a "how to" complement is a named GAP `nested_purpose` with its owner; fixture from u0094.s02's shape | 2.8, PE-4, 4 |
| PE-R5 | `purposes@0`'s layer coverage names `acts@0` and `definitions@0`, derived from the table per PC-4 (no hand edit of `documentLayers`), with its composes argument and fixture; main's refusal stays until then | 2.5, PE-2, 4 |

The statement check (`manage-agents/debates/syn2-apply-dri-syn2-0401`) added: PE-0p's answer key written out with
u102's act fixed (edit 5); PE-6's acts × alternatives gate (PE-R3); PE7b-1's dependency on judgment-terms'
`syn2code-judgment-terms-1` (PE-R1). The second check added that gate to the batch table, the order and 2.7.

**Condition.** The family-scoped re-pilot on a fresh draw shows at least 8 of 10 FAITHFUL and COMPOSES, with DOC
COMPOSES in both seats. Until then the PE build rows stay held (FIDELITY_PILOT_GATE).

### 10.3 The second fidelity-pilot revision (PE-R6 to PE-R11, pe-rev, 2026-11-02)

Applied from `manage-agents/reviews/dri-decisions-20261102-fp-purpose-explanation.md` item 1 (the 2026-11-02
re-pilot's REVISE, 7 of 10; findings PE-R6 to PE-R11 and the decision's two C points only). PE-R1 to PE-R5 stand as
in 10.2.

| Finding | What changes | Where |
|---|---|---|
| PE-R6 | a purpose only being considered, inside a "whether"/"which" complement, is withdrawn from the claim on an instruction's purpose and given to commands-imperatives' question object as a named GAP `considered_purpose` (owner and row named); no new polarity; C21 alone gives this kind no route in such a document | PE-7b (writer rule), 4, 8 (boundaries, C21, requests) |
| PE-R7 | D6 (a) beside an attitude gains the candidate `in-attitude`, the means-end relation inside the attitude's content; the slot is attitudes' and is stated, not designed; the candidate is pending; never "ought Y"; no set reduced | D6 (a), PE-3, 4, 8 (requests) |
| PE-R8 | one stated rule: a link's line appears only under the candidates that hold its target, and a line under a scope it cannot name says so; `holdsTarget`, `shownUnder`, `unlinkedActive` (PE-1), `linkLines`, `underLine`, `scopeLine` and the section's `under` (PE-2); fixtures F9 and F10 from u0014.s03's and u0289.s05's shapes | D10a, 0 (table), 2.3, 2.4, PE-1, PE-2, 4 |
| PE-R9 | D6 (c) covers exactly "want(s) … to … because" and "may choose to … because"; every other motive frame is a named GAP `motive_frame`; no motive content (PE-E2) | D6 (c), PE-3, 4 |
| PE-R10 | `judgments@0` joins the `purposes@0` row in PE-3, the batch that first emits D6 (a)'s limiting candidate, with its composes argument and fixture; PE-7b adds only `events@0`; the other layer lists are not named, so they stay refused | D11, 0 (table), 2.5, PE-3, PE-7b, 5 |
| PE-R11 | D8a's guarantee names pack premises: the stated check `packsInert` (fault 6a) and the proof obligation `packSources_complete` on any `layerCovers` entry whose list holds a pack; fixture F2c, a pack premise from F2's denied reason, refused | D8a, 0 (table), 2.3, PE-1, PE-7b, 4, 8 (S2b, requests) |
| C (rule 12) | the reading set sits on the rule's part, the clause on its own part; profile-composition's rule 12 is read as this placement | D6 (a) |
| C (`markersLinked`) | an unlinked causal "because" of another family cannot carry main's `causal` label under `purposes@0`; recorded as a refusal with a working route | 8 (boundaries) |

Nothing signed changes: D6's sets only gain candidates or frames, every new refusal refuses rather than admits, and
no DELTA row, trust line or signature is involved. u0289.s05's natural motive reading still has no content (PE-E2).

**Condition** (decision item 1). The next re-pilot's RESULT.md shows at least 8 of 10 family-scoped FAITHFUL and
COMPOSES, with DOC COMPOSES in both seats. Until then the PE build rows stay held (FIDELITY_PILOT_GATE).
