# Events, time, durations and causation (`events@0`, and `alternatives@0` on documents): buildable plan

> Status: plan draft 2 (2026-10-13). Draft 2 applies the converged Astra + Fable review of draft 1
> (`manage-agents/debates/design-events-time-causation/{astra,fable}.md`, CONVERGED in round 3: **REVISE now, BUILD
> after ET-2's statement review**) and the DRI's cross-plan synthesis edits of 2026-10-13 (same files, last section;
> `manage-agents/debates/plan-synthesis/SYNTHESIS.md`), which supersede the rounds where they differ. Debate items are
> cited **A** to **J** (draft-2 items of the round-2 position, as corrected in round 3) and **R1-R4** (the four round-1
> edits Astra accepted); synthesis edits are cited **X1** to **X10**. ET-2's statement spec is
> [events-time-causation.md](events-time-causation.md); where this plan and that spec differ, the spec is the reviewed
> text. Draft 1's status follows.
>
> Draft 1 (2026-10-12), branch `design/events-time-causation` from `main` at `49de179e`. Research wave
> of 2026-10-12 (DRI). It is the plan for the design recommended in
> [docs/research/events-time-causation.md](../research/events-time-causation.md) (cited `research n`), which must be
> read first: it holds the evidence, the measured need, the prior art and the comparison of candidates. Planning only:
> no code, proof, test or generated file changed, and no model was called. The Lean blocks below are the statements
> the batches prove. They were written against `main` at `49de179e` and against RD-9's branch `rd-9/integrate` (read
> 2026-10-12) and were **not elaborated**; ET-2 elaborates them in an untracked stub before any Lean batch starts, as
> RD-9's SC-0 did. As in [alternatives.md](alternatives.md) 7, the blocks are statement schemata: a helper name not
> found on `main` or `rd-9/integrate` is defined by the batch that proves the statement. Numbers are measured (the
> method is named beside each) or labelled *estimate*.
>
> Inputs: [alternatives.md](alternatives.md) (cited `alt n`), [causation-PLAN.md](causation-PLAN.md),
> [lean/ALTERNATIVES.md](../../lean/ALTERNATIVES.md), [units-schema.md](units-schema.md) (cited `W6 n`) and
> [docs/W6A-STATUS.md](../W6A-STATUS.md), [norm-defaults.md](norm-defaults.md) (cited `nd n`) and
> [lean/NORMDEFAULTS.md](../../lean/NORMDEFAULTS.md), [composition.md](composition.md), [risk.md](risk.md),
> [document.md](document.md), [norms.md](norms.md), RD-9's plan `docs/spec/rd-9-soft-chain-PLAN.md` on `design/rd-9`
> and its build on `rd-9/integrate` (`lean/VE/NormDefaults/{LayeredEntail,Report,Evidence}.lean`), the sibling plan
> `docs/spec/weighing-PLAN.md` on `design/weighing`, `usecases/{asimov-laws,asimov-extended,eligibility,agent-policy,
> safety-framework}`, and the pinned pilots of run `20261012T1800Z`.

## 0. Summary

VE already has dates (W6a, `time@0`), choices with preventable harm (`alternatives@0`) and possible harm
(`risk@0`), merged and proved, and none of them reaches a pilot: the pilots' chain (`documents@1`, `norms@0`,
`norm-defaults@0`, `readings@1`, `relational-fol@0`) has two-place predicates only, no day, no order, and refuses
`alternatives@0` and `time@0` (research 1.4). The measured primary need is UDHR 9 units, 1,116 B, and constitution 85
units, 13,293 B, almost all co-blocked (research 2).

This plan does four things, in this order:

1. **Move pilot numbers with what is merged, no product code** (ET-0, ET-1). UDHR u042 ("at the time when it was
   committed") with an event sort and a day sort, which needs no order. The constitution's own argument about its
   hard constraints (u0171.s01, u0171.s03, u0172.s01, u0172.s02) as a component document on the merged
   alternatives route: refusal is the inaction, "it should always be possible to comply with them all" is a
   FOLLOWABLE certificate, and "even if doing so would prevent ... a much more dangerous bioweapons attack" is a
   checked consequence. ET-0 and ET-1 are audited pilots with no promised byte gains; the *estimates* (UDHR 200 to
   318 B, constitution 755 to 1,126 B) are what their bars would move, not a claim.
2. **A timeline profile, `events@0`** (ET-2 to ET-6): a day sort counted in whole days; `before` with three generated
   premises; event sorts whose elements happen on at most one day; state sorts that begin and end; named dates from
   1970 on whose order Lean computes from the proved W6a calendar; an optional "date of this document"; causal links
   (item 4). All premises are universal and function-free and form PK-1's `events` pack, the last pack of the layered
   route's extra premises `X` (RD-9), so no checker changes (X1). The day domain is fixed: every civil day from
   1970-01-01 to 9999-12-31. A witness or countermodel is reported only when the calendar completion theorem covers
   it: adding the missing calendar days keeps every formula the evidence check read (the whole assembled `X`, the
   expanded rules and definitions, the admissible fillings and the conclusion) at its value (A, X2); otherwise the
   answer is UNKNOWN with `NotCalendar`, while an independently sound certificate still stands. Plain wordings;
   "until", "during", "by", "within" and the other source words of 2.7 in sources become reading sets, and in
   authored text are rejected with explicit rewrites. *Estimate*: UDHR 201 to 548 B on its own.
3. **`alternatives@0` with the completion** (ET-7, ET-8): wire the branch whose semantics `followableU_sound` already
   proves (nd 282-301), so a silent permission is UNDECIDED (two validated fillings with opposite answers) or UNKNOWN
   instead of allowed by a modeling choice (Asimov, and the ET-1 component); a Kleene "unknown" alone is never
   UNDECIDED (C).
4. **Causal links between events as named open relations** (ET-9): "<event> contributed to <event>", "<event> was
   necessary for <event>", each with a decider and support, never decided by the checker; two universal premises,
   stated as explicit conventions (D): a cause does not start after the day of an effect that is an event, nor after
   the end of an effect that is a state (only when it ends); a necessary condition contributes. *Estimate*: UDHR
   127 B; constitution 600 to 1,500 B of a 6,059 B upper bound, measured by ET-9's bar.

Integer durations over variables, deadline obligations, multi-step choices, actual causation, dates before 1970 and
`events@0` beside `data@0` are **experiments and triggers** (ET-E1 to ET-E3, ET-T1 to ET-T4), each with a
pre-registered bar or trigger. The act-performance predicate other plans need is a design batch here (ET-D2), not a
build.

**The first batch that moves a pilot number** is ET-0 (UDHR u042, 2 to 3 h, no product code); ET-1 (constitution,
3 h, no product code) is independent and may run beside it.

## 1. Decisions

| # | Decision | Why | Rejected |
|---|---|---|---|
| D1 | Time on the chain is a **day sort** of whole civil days with a declared `before`, not integers | the chain is first-order with two-place atoms and no arithmetic (research 1.4); W6a already counts civil days and excludes clock time (W6 6.2); days are what the pilot sentences need | integer days on the chain (candidate B, research 4.2): a norms × order checker for a need measured at about zero; dense time, clock time |
| D2 | **Events and states are things** with two-place roles: an event sort's `on` predicate, a state sort's `begins` and `ends`. Names are the author's; argument orders are fixed by the block (as alt 1.1); each role's verbalisation is the author's, of the form "{0} <verb phrase> on {1}" ("{0} happens on {1}", "{0} is committed on {1}", "{0} begins on {1}", "{0} is dissolved on {1}"), which Lean checks; the role's meaning comes from its place in the block, never from its words (R3) | Davidson and Parsons (research 3.1); fits the two-place chain; it is what the UDHR translators already do without days (research 1.4) | a time argument on every predicate (three places: `nary@0`, which the chain lacks) |
| D3 | The profile is a **premise pack**: its block regenerates closed base premises `Ev_V`, which are PK-1's `events` pack, the last pack of the layered route's extra premises `X` (order `soft, rights, weighing, attitudes, scales, events`; `VE.NormDefaults.Wire.premisesX`, `EntailsX`, `acceptanceX`, `modelCheckX_sound`). The pack's `decls` are the named-date constants, its `labelled` list is `Ev_V` with labels `events:<name>`, its `origins` map each label and date to its request path in the block, and `date__` is in PK-1's `reservedPrefixes`. No new checker, no new route, no new service mode, no events-local X assembly (X1) | RD-9 proves the checkers sound for any typed `X`; PK-1 is the one assembler of `X` for every pack | a new route `ve_events_route` (a copy of the layered dispatch); inlining defined words into guards (unneeded: every wording elaborates to base formulas over the roles) |
| D4 | The premises are **universal and function-free**: `before` is irreflexive, transitive and linear; each event on at most one day; a state never ends before it begins; consecutive named dates ordered, and no day between two named dates one day apart; the two link conventions (D10); necessary implies contributed. Membership of norms.md 7.1 is reported per document after expansion (`fragment: yes \| no (<first reason>)`); the day-quantified wordings ("happens before", "is in progress on") put a document outside it, and there an answer comes from a certificate or is UNKNOWN. No completeness is claimed beyond norms 7.1's own (B) | finite models exist for every premise set (`eventsPremises_satisfiable`); the existing fragment conditions stay the only completeness claim | "every day has a next day" (forces infinite models); existence of an event's day as a premise (validated on situations instead, as alt 4.2 E1-E3) |
| D5 | **Named dates** are constants of the day sort generated from the block's ISO list (`date__YYYY_MM_DD`, reserved prefix), read and rendered by W6's date-literal class ("12 October 2026", "2026-10-12"); Lean orders them with `VE.Time.Calendar` (`Civil.num`, `before_iff`). Dates run from 1970-01-01 to 9999-12-31 (`Civil.Valid`); a date before 1970 is `DateRange`, a stated limit until ET-T3 fires, so UDHR's own date cannot be named (G, X8). At most 64 per document | one calendar, one date grammar (W6), no Python computation of dates; 64 keeps the generated premises under `MAX_NODES` | a second calendar; Python date order; all-pairs order facts (quadratic; transitivity derives them) |
| D6 | **The day domain is fixed**: the intended reading has every civil day `0..dateMax` as a day. A witness or countermodel (any route, weighing's zone completions included) is reported only when (i) it is **calendar-embeddable** (its days can be numbered as civil days, keeping the order and the named dates) and (ii) ET-2's **calendar completion theorem** covers it: adding the missing calendar days (in the gaps and at both edges, up to the calendar's bounds) with no facts except their order keeps every formula the evidence check read at its value: every pack's premises in the assembled `X`, the expanded rules and definitions, the admissible fillings and the queried or refuted conclusion. Otherwise the answer is UNKNOWN with `NotCalendar`; independently sound certificates are not suppressed (A, X2). Order-derived predicates ("is in progress on", "between") are never guards | the premises admit structures no calendar realises (a day squeezed between two consecutive dates), and an embeddable finite situation can still refute a quantified claim the calendar makes true ("there is a day between 12 and 14 October 2026"; "there is a day after 12 October 2026"); a refutation there would be about no real situation | dropping the check (wrong refutations); embedding alone (not enough: the numbering is one-to-one, not onto); adding counting premises for every gap (expensive) |
| D7 | Certificates are sound for every structure satisfying the premises, hence for every **calendar reading**, whose days are all the civil days (`events_certificate_calendar`) | the intended reading is the calendar; it satisfies the premises (`calendar_sat`) | — |
| D8 | **Reader-facing English has no temporal operators**: no "until", "always", "eventually", "while", "by" (deadline), "within" (window), "since" in VE text. Quantification over days is written out ("on each day", "there is a day such that", "no later than that day"). In a **source**, each of those words becomes a reading set with a distinguishing situation; in **authored** text it is rejected with the explicit rewrites | one reading per sentence; readers misread LTL (research 3.3); "until" alone has at least two readings (silent after the end, or ending), and "by 10 December" two (before, or no later than). "Before" is strict day precedence, never "no later than": a source such as "confirmed before the action" that needs order within a day keeps the `time-of-day` gap, and same-day facts alone never make a point UNDECIDED (E) | fixed FRET-style meanings for "until" and "within" |
| D9 | "until" reads as a reading set **per modality** (R2). For a rule of modality m ("may", "must", "must not", "need not") "m X until E": {U1: m X on each day before the day E happens (the text is silent from that day); U2: U1, and the opposite of m on each day from the day E happens}, where the opposite of "may" is "must not", of "must" is "need not" (the obligation stops; nothing is forbidden), of "must not" is "may", of "need not" is "must". For "until <date>" the inclusive candidates are added (U1 and U2 with "on each day no later than <date>" and the opposite "from the day after"), four in all. Under `norm-defaults@0` with the predicate unspecified, U1's silence is UNDECIDED, so the distinguishing situation is "E happens on 5 January 2027; 4, 5 and 7 January 2027": the day before E, E's own day and a later day (U1 UNDECIDED on 5 and 7 January, U2 SETTLED to the opposite there, both SETTLED to m on 4 January). Under a deny or allow completion U1 and U2 may coincide; then the set has no distinguishing situation and the translator must choose (nd's "grounded" line) | the completion already gives "the text does not say"; no new machinery; whole days cannot say whether E's own day is covered, so E's day is in every distinguishing situation, and "valid until Friday" is often inclusive | a single cessation reading; one cessation rule for every modality (wrong for obligations: "must X until E" never means "must not X" afterwards) |
| D10 | **Causal links** are base predicates between event or state sorts, declared in the block with a form (`contributed`: "{0} contributed to {1}"; `necessary`: "{0} was necessary for {1}") and a decider; they are open: the checker never decides a link, lists every stated link in the residual with its support and decider, and adds only two premises, each an explicit convention shown in the legend (D): `link_forward` (the cause does not start after the day of an effect that is an event; the cause does not start after the end of an effect that is a state, which binds only when that state ends, so a later event may contribute to a state already in progress) and `link_weaker` | VISION converged rule 8 (no unsupported causal assumptions certified); Lewis: dependence suffices for causation; no backward causation for ordinary events, while a cause may join a state that is already in progress | deciding causation (structural models are research, ET-E3); reusing `leads to` outside a declared decision model |
| D11 | The link wordings are disjoint from `alternatives@0`'s and `risk@0`'s fixed wordings (`leads to`, `allows ... to happen`, `prevents`, `causes`, `might lead to`, `cannot lead to`); "resulted in", "led to", "caused", "brought about" in a source become a reading set over the two link forms (and `leads to` where a decision model is declared) | one owner per wording; alternatives already rejects "results in" and "brings about" with a rewrite to `leads to` (alt 2.2), which stays | a third causal vocabulary |
| D12 | `events@0` is **one row of AR-10's profile-gate table** (`requires`, `refuses` with its texts, `slot`), with the composition proof for the combinations it admits; no gate theorem is re-proved in `Dispatch.lean` (X3). It requires `relational-fol@0`, `norms@0` and `norm-defaults@0` (the layered route that carries `X`; a predicate may still take the `deny` or `allow` default), with or without `soft-norms@0`, `rights@0` and `readings@1`; it is refused with `order@0`, `time@0`, `closure@0`, `nary@0`, `alternatives@0`, `risk@0`, `reports@0`, `speech-acts@0` and **`data@0`** (`UnsupportedProfile: events@0 with <p>`). `data@0` is refused, not admitted, so agent-policy's R3 becomes the trigger ET-T4 (R1). Documents without norms are out of the first build, so eligibility's own environment (`order@0`, `time@0`, no norms) is not a route for R1, which is restated on the norms chain (4.3) | the hook is RD-9's layered `X`; each refused pair is a later design batch with its own trigger; refusing `data@0` costs no pilot unit and needs no new composition proof | a frozen-route Background slot now; admitting `data@0` now (a composition proof for a use case that also needs order within a day) |
| D13 | **Alternatives with the completion** (ET-7) wires the branch `fill (inlineTree A)` that `followableU_sound` already proves, in a new file beside the alternatives wire; the refusal `alternatives@0 with norm-defaults@0 is not implemented` is deleted, not kept as a fallback. Its **evidence contract** (C): FOLLOWABLE from a certificate; DILEMMA from a witness and a filling; per alternative, clear or not clear only when settled under every admissible filling (a definite Kleene value, or enumeration of the cone), **UNDECIDED only from two validated fillings with opposite answers**, and UNKNOWN otherwise; a Kleene "unknown" is shown as UNKNOWN; the excluded-middle case (nd fixture u12's guard) is a fixture | nd 282-301 specified it; `lean/NORMDEFAULTS.md` lists it as still open; the Asimov case waits for it; nd 2.5 requires two validated fillings for UNDECIDED, and `kleene_sound` justifies definite values only | a Python-side classification of silent permissions; Kleene "unknown" as UNDECIDED |
| D14 | ET-0 and ET-1 change **no product code**: they rewrite pilot units with merged features and measure | the smallest batches that move a pilot number (as weighing's WG-0) | waiting for `events@0` before any pilot movement |
| D15 | Durations over variables ("within 30 days after each request"), deadline obligations, finite traces, multi-step choices and actual causation are **experiments or triggers** with bars (ET-E1 to ET-E3, ET-T1, ET-T2) | measured need about zero in the pilots (research 2.3: four duration phrases in 184,893 B; UDHR none); each is a large core change | building candidate B or C now |
| D16 | Lean owns the block, the premises, the date order, the calendar check, the link residual and every diagnostic; Python checks shape only where it already does, relays and displays; Rust evaluates untrusted as today | CLAUDE.md "Who owns what" | any Python premise or date computation |

## 2. Design

### 2.1 What an events document is

A document on a chain list (D12) whose environment carries the `events` block (2.2) and whose profile list contains
`events@0`. Its vocabulary declares a day sort, the `before` predicate, the event and state sorts with their role
predicates and any other predicates the author needs, some of them over days ("{0} constitutes a penal offence under
national or international law on {1}"). Its rules, assertions and reading sets are ordinary chain content over that
vocabulary. Lean decodes the block, regenerates the named-date constants into the environment, regenerates `Ev_V`
(2.3) and registers it as PK-1's `events` pack, which PK-1 places last in `X` on whichever branch of the layered
route checks the list (X1). Everything the route answers
(elaborate, conflict, status, report, certificate, admission, readings verdicts) is unchanged in kind; certificates
bind `Ev_V` by meaning id like every other regenerated premise.

### 2.2 The block (wire form, identity-bound like `regulated`)

```json
"events": {
  "day": "day", "before": "before",
  "events": [{"sort": "act", "on": "committed_on"}, {"sort": "conviction", "on": "convicted_on"}],
  "states": [{"sort": "marriage", "begins": "marriage_begins", "ends": "marriage_ends"}],
  "dates": ["2027-01-05"],
  "anchor": "2026-10-12",
  "links": [{"predicate": "contributed_to", "form": "contributed", "decided_by": "the drafters"}]
}
```

The values are an example (the anchor is the date the document gives for itself); each role predicate's verbalisation
in the vocabulary has the form "{0} <verb phrase> on {1}" ("{0} is committed on {1}"), checked by Lean (D2). Unknown
fields are rejected. `dates` are ISO strings parsed by `VE.Time.parseIso` and admitted only when `Civil.Valid`
(1970-01-01 to 9999-12-31, W6 6.1; earlier dates are `DateRange`, as in W6, a stated limit until ET-T3 fires: there is
no second calendar and no events-local date code, G and X8). `anchor`, when present, is a valid ISO
date; it adds the named date with the fixed verbalisation "the date of this document" (and its long form as an alias).
`decided_by` is a string of at most 64 bytes or `unstated`. The block is part of the canonical environment bytes, so
it changes `environment_id`; an environment without it is unchanged.

### 2.3 The generated premises `Ev_V`

In this order, each labelled `events:<name>` (one label per generated formula, with the sort or date pair in the
label):

```text
irreflexive        ∀t. ¬ before(t, t)
transitive         ∀t u v. before(t, u) ∧ before(u, v) → before(t, v)
linear             ∀t u. before(t, u) ∨ t = u ∨ before(u, t)
date:<D>:<D'>      before(c_D, c_D')                                            consecutive named dates, D.num < D'.num
adjacent:<D>:<D'>  ∀t. ¬ (before(c_D, t) ∧ before(t, c_D'))                     consecutive named dates with D'.num = D.num + 1
one_day:<E>        ∀x. ∀t. on_E(x, t) → ∀u. on_E(x, u) → t = u                  each event sort E
one_begin:<S>      ∀x. ∀t. begins_S(x, t) → ∀u. begins_S(x, u) → t = u          each state sort S
one_end:<S>        ∀x. ∀t. ends_S(x, t) → ∀u. ends_S(x, u) → t = u              each state sort S
not_before_begin:<S> ∀x. ∀t. begins_S(x, t) → ∀u. ends_S(x, u) → ¬ before(u, t)  each state sort S
link_forward:<L>   ∀x y. L(x, y) → ∀t. start(x, t) → ∀u. bound(y, u) → ¬ before(u, t)   each link; start = on (event) or begins (state); bound = on (event effect) or ends (state effect)
link_weaker:<N>:<C> ∀x y. N(x, y) → C(x, y)                                     a `necessary` link N and a `contributed` link C on the same sort pair
```

All are closed, universal and function-free. The first five are the **calendar premises** (true in every calendar
reading, `calendar_sat`); the rest are the **conventions**, written with each day quantifier guarded by a role
atom, so the calendar completion theorem covers them (A). `link_forward` for a state effect binds only when the
state ends (D). Existence facts are **validated on situations, never assumed** (as alt
4.2): a situation in which a stated event has no day, or a state no beginning, is accepted, and the report says the
fact is missing where a wording needed it.

### 2.4 Named dates and the anchor

The decoder sorts the named dates by `Civil.num`, removes none silently (`DuplicateDeclaration: date <iso>`), and
generates one constant `date__YYYY_MM_DD` of the day sort per date with the verbalisation of W6's long form. Only
consecutive pairs get a `date` premise; transitivity entails every other pair (`datesOrder_iff`). No declared name
may start with `date__` (`EventsReserved: <name>`; `date__` is registered in PK-1's `reservedPrefixes`, X1). The
anchor is a named date; "in the future" in a source is "on some day after the date of this document". The anchor
"the date of this document" is the one indexical day for every plan; quantities' QT-0p "at the moment" refers to it
once `events@0` lands (X9).

### 2.5 The calendar check (`embeddable`) and the calendar completion

**The day domain is fixed** (A): the intended reading's days are all the civil days `0..dateMax`. On every finite
situation the route would report (a CONFLICT witness, a countermodel, a NONE or SOME model of readings, a status, a
scenario, weighing's zone completions), Lean checks, after the existing checks:

1. `before` restricted to the day domain is a strict linear order;
2. each named date denotes a day, in increasing `Civil.num` order;
3. sorting the days by `before`, the number of unnamed days strictly between two consecutive named dates `D < D'`
   is at most `D'.num - D.num - 1`; before the first named date at most `D.num`; after the last at most
   `dateMax - D.num`; with no named date, at most `dateMax + 1` days;
4. **the calendar completion fragment**: every formula the evidence check reads (every pack's premises in the
   assembled `X`, `Fill_T`, the base background, the premises `Γ` and the queried or refuted conclusion, after the
   rules and definitions are expanded) is in the class that ET-2's completion theorem proves keeps its value when the
   missing calendar days are added (in the gaps and at both edges) with no facts except their order. The class is
   syntactic and polarity-aware: a day quantifier that must range over the added days is guarded by an atom that is
   false on them (a role, link or author predicate, never `before` or a predicate derived from the order, such as
   "is in progress on" or "between", and never an unsaid table), while a universal claim refuted at a day the
   situation lists, or an existential claim witnessed at one, needs no guard.

If a check fails, the result is UNKNOWN with `NotCalendar: <first failing condition>`, never a refutation; an
independently sound certificate is not suppressed (X2). `embeddable_sound` (3.2) gives the numbering, and the
completion theorem turns the numbered situation into a calendar situation with every civil day. Fixtures: a situation
with 12 and 14 October 2026 and no day between them never refutes "there is a day between them" (UNKNOWN); a
situation whose last day is 12 October 2026 never refutes "there is a day after 12 October 2026" (UNKNOWN). ET-2 says
where R1 falls (inside: its refutations are universal claims refuted at listed days; events-time-causation.md 1.8).

### 2.6 Causal links

A link is a base predicate between two event or state sorts, declared in the block with a form and a decider, and
listed as a W2 open term (document.md) with the same decider. The route never decides a link: a link atom is true in
a situation only if the situation says so, and certificates use links only as the author states them. The report
gains `causal_links`: each link predicate with its decider, and each unit that states or denies a link with its
support. The two premises `link_forward` and `link_weaker` are the only causal content the checker adds, and each is
an explicit convention printed in the legend (D): "A cause does not start after the day of an event it contributed
to, and does not start after the last day of a state it contributed to, when that state ends." A later event may
contribute to a state already in progress.

### 2.7 English (one reading each; rejected as today when `events@0` is off)

Role and derived wordings (registered with `profiles=("events@0",)` in the catalogue that owns wordings when the
batch runs, 6):

| Wording | The one reading (the IDE's paraphrase) | Formal effect |
|---|---|---|
| `<event> <vp> on <day>` (the role's own wording, "happens on", "is committed on") | the day the event happens | `on_E(x, t)` |
| `<state> <vp> on <day>` (its `begins` and `ends` wordings, "begins on", "ends on") | its first day / its last day (the state is still in progress on it) | `begins_S`, `ends_S` |
| `<day> is before <day>` | strictly earlier: an earlier day, never the same day (E) | `before(t, u)` |
| `<day> is after <day>` | strictly later | `before(u, t)` |
| `<day> is no later than <day>` | earlier or the same day | `before(t, u) ∨ t = u` |
| `<day> is on or after <day>` | the same day or later | `before(u, t) ∨ t = u` |
| `each day from <day> through <day>` | every day from the first to the second, both included | `∀t. ¬before(t, a) ∧ ¬before(b, t) → …` |
| `<event> <vp> before <day>` / `... no later than <day>` / `... after <day>` / `... on or after <day>` (the role's verb phrase) | the event happens, on a day so placed | `∃u. on_E(x, u) ∧ …` |
| `<event> <vp> before <event>` / `... no later than ...` / `... after ...` / `... on the same day as ...` | both happen, on days so placed | `∃t u. on_E(x, t) ∧ on_F(y, u) ∧ …` |
| `<state> is in progress on <day>` | it has begun on or before that day and has not ended before that day (F) | `∃b. begins_S(x, b) ∧ ¬before(t, b) ∧ ¬∃e. ends_S(x, e) ∧ before(e, t)` |
| `<cause> contributed to <effect>` | an open causal link, decided by its decider | `L(x, y)` (form `contributed`) |
| `<cause> was necessary for <effect>` | an open but-for link: without the cause the effect would not have happened, decided by its decider | `N(x, y)` (form `necessary`) |
| named dates: `12 October 2026`, `2026-10-12`, `the date of this document` | the named day | `c_D` |

Persistence is never assumed (F): a state with no stated end day is in progress on a later day only in situations
that give it no end; a certificate that it is in progress there needs a stated premise that it has not ended ("there
is no day such that that stay ends on that day", or "that stay does not end on any day before 28 September 2026"),
which the report shows with its support.

Days are quantified with the existing forms ("each day", "there is a day such that", "that day"), so no new binder is
added. A regulated predicate may take a day argument ("{0} be presumed innocent on {1}"), which keeps it two-place.
The legend generated from the block says, in plain English: "Times are counted in whole days: two things on the same
day happen on the same day, and neither is before the other." and "A state is in progress from the day it begins
through the day it ends." and, when the block declares links, the convention of 2.6. "Ends on" is inclusive because
that is the common English reading ("the offer ends on Friday") and the one the eligibility answer key needs (4.3, R1:
C26's stay ends on 27 September 2026 and is in progress throughout the qualifying week); a source whose end day is
exclusive becomes a reading set.

Rejected in authored text, each with its rewrites (advice rows in english-lean's catalogue, X9; the plan adds rows
only):

| Pattern | Advice |
|---|---|
| `until <...>` | "Write the rule for each day with the guard 'if it is not the case that <event> happens no later than that day'; the text then says nothing about later days. If it means the rule stops, add a second rule with the opposite wording ('must not' for 'may', 'need not' for 'must', 'may' for 'must not') for the days on which <event> happens no later than that day. For a date, say whether the date itself is included: 'before <date>' or 'no later than <date>'." |
| `by <day or event>` (as a deadline) | "Write 'before <day>' or 'no later than <day>'." |
| `within <n> days` | "Durations over events are not available here; name the dates, or use the quantity wordings in a quantity document." |
| `during <state>` | "Write the rule for each day with the guard '<state> is in progress on that day'." |
| `since <...>`, `while <...>`, `always`, `eventually`, `whenever` | "Write the days explicitly: 'on each day, if ...', 'there is a day such that ...'." |
| `resulted in`, `led to`, `caused` between events | "Write '<cause> contributed to <effect>' or '<cause> was necessary for <effect>'; in a decision model write 'leads to'." |

In translation, each of these source words opens a reading set whose candidates are the explicit wordings, with the
distinguishing situation shown (D9). ET-5's rows go into english-lean's catalogue and the plan adds rows only (X9):
the source-word reading sets for "until", "by", "within", "during", "since", "while", "always", "eventually",
"whenever", "resulted in", "led to" and "caused", and their authored-text refusals with rewrites. Quantifier scope
inside a sentence ("every day before") is the phrase grammar's (english-lean's engine and act-phrases), not this
plan's (X7). The wordings are checked with readers by ET-E1 before ET-5 writes them (R4).

### 2.8 Identity and binding

The block is in the canonical environment bytes (`environment_id` changes only for environments that carry it). The
regenerated date constants are part of the regenerated environment, as `unsaid__p` declarations are (nd, NORMDEFAULTS
"`E‴_base` on the wire"); Python builds the same bytes for certificate bindings by relaying Lean's
`baseEnvironmentJson`, never by computing them. `Ev_V` enters `premisesX` as PK-1's `events` pack, after every other
pack (PK-1's order `soft, rights, weighing, attitudes, scales, events`, X1), so every certificate binds it by meaning
id. A replay against a changed block, a changed date list or a changed link decider is stale.

### 2.9 Well-formedness, in order (`WellFormedEvents`)

1. The profile list satisfies D12, as AR-10's `events@0` row (`UnsupportedProfile: events@0 with <p>`;
   `UnsupportedProfile: events@0 requires norm-defaults@0`).
2. The block decodes with no unknown field (`InvalidInput: events.<field>`).
3. The day sort is declared; `before` is a base predicate `(day, day)` with verbalisation `{0} is before {1}`
   (`EventsSort: before`, `EventsVerbalisation: before`), not regulated, not defined (`EventsRegulated: <p>`).
4. Each event sort is declared, is not the day sort, appears once among event and state sorts
   (`DuplicateDeclaration: event sort <s>`); its role predicate has sorts `(s, day)` and a verbalisation of the form
   "{0} <verb phrase> on {1}", with a nonempty verb phrase and no other slot (`EventsVerbalisation: <p>`, R3).
   Likewise for state sorts with `begins` and `ends`. All role predicates are pairwise distinct.
5. Each link names a base predicate over two event or state sorts with its form's verbalisation; its decider is at
   most 64 bytes or `unstated`; the link is declared as an open term with the same decider (`LinkNotOpen: <p>`); no
   link predicate is a role predicate.
6. Dates parse and are valid (`DateRange: <iso>`, `InvalidInput: events.dates`), are unique, at most 64
   (`ResourceLimit: events dates`); no declared name starts with `date__` (`EventsReserved: <name>`).
7. The regenerated premises are typed over the regenerated environment and within `MAX_NODES` each
   (`ResourceLimit: events premise <label>`).

### 2.10 `alternatives@0` with the completion (ET-7)

The alternatives route accepts `norm-defaults@0` beside `alternatives@0` and `norms@0`. It decodes `unspec` (the
regulated predicates whose `default` is `unspecified`), builds `fill ⟨inlineTree A, unspec⟩`, and answers:
FOLLOWABLE from a certificate over `backgroundBaseAltU A unspec ++ A.Γ` (`followableU_sound`, proved); DILEMMA from a
witness situation and a filling; scenario evaluation in which each alternative is clear, not clear, "undecided: the
text does not say whether it may be performed", or UNKNOWN; the untrusted diagnosis gains `UNSETTLED(<alternatives>)`
before NONE-PERMITTED (nd 286-290), listing only alternatives with UNDECIDED evidence. **Evidence contract** (C): an
alternative is clear or not clear only when its `clear` formula is settled under every admissible filling (a definite
Kleene value, `kleene_sound`, or enumeration of its cone, as nd's `settled_of_enumeration`); it is UNDECIDED only from
two validated fillings with opposite values (nd 2.5, as `undecided_witness_sound`); otherwise UNKNOWN, naming the
budget when it was exhausted. A Kleene "unknown" alone is shown as UNKNOWN, and the excluded-middle guard of nd
fixture u12 is a fixture (Kleene unknown, enumeration settles it). A document without `unspecified` decodes exactly
as today (`decodeAltSourceU_conservative`). `risk@0` with the completion is not in this plan (nd 293-298; its own
batch).

### 2.11 One owner, and what is deleted or not duplicated

- **Calendar**: `VE.Time.Calendar` only (`parseIso`, `Civil.Valid`, `Civil.num`, `before_iff`). The events decoder
  calls it; nothing in Python or Rust computes a date order or a day number for this profile.
- **Date literals in English**: W6's literal grammar (ISO and long form), wherever the catalogue holds it; the events
  surface reuses that class.
- **Outcome tables and the four alternatives words**: `VE.Alternatives` only. `events@0` adds no causal word that
  overlaps (D11); the catalogue's disjointness check covers the link wordings.
- **The W2 `causal` kind**: unchanged (`ve/admission.py` `RELATIONS`, `lean/VE/Route/Admission.lean`); links are
  content, the kind stays a label for causal text that is not formalised.
- **The profile gate**: AR-10's profile-gate table owns it (its scope includes `Dispatch.lean:417–474`). `events@0` is
  one table row (`requires`, `refuses` with its texts, `slot`) with its composition proof; AR-10's generic lemma shows
  the table runs as written, and no gate theorem is re-proved in `Dispatch.lean`. ET-5 adds no `ve/profiles.py` row
  and no gate mirror: Python reads AR-10's generated data (H, X3).
- **X assembly**: PK-1's one assembler (X1). `events@0` registers one provider line (its pack), not a copy of the
  layered dispatch and no `assembleX` of its own.
- **Deleted by ET-7**: the refusal `alternatives@0 with norm-defaults@0 is not implemented` (Lean
  `VE.Compose.Dispatch`, Python mirror if present) and the alternatives route's `UnsupportedProfile: Unsupported
  profile norm-defaults@0`; the test that asserts both refusals is rewritten to assert the branch. The deletion in
  `Dispatch.lean` is serialised with AR-10's table: whichever lands second rebases. If ET-7 lands first, AR-10's
  legacy proofs take ET-7's gate as the baseline; if AR-10 lands first, ET-7 edits the table row and proves the newly
  admitted combination (X3).
- **Pilot workarounds** (no product code): one-occurrence sorts with no day, and days baked into predicate names, are
  retired for every unit ET-6 restates.

### 2.12 What stays open (the residual, never certified)

The truth of every link and of every day an event is said to happen on (with their support); the completeness of
stated events and alternatives; whether "periodic", "constantly", "progressive", "of full age" and the like are met
(open terms); clock time within a day (two things on the same day are on the same day; risk's `Q-clock`; a source
that needs order within a day keeps the `time-of-day` gap, E); whether a state without a stated end has ended (F);
durations over events; deadline fulfilment; branching futures; dates before 1970 (ET-T3).

## 3. Lean statements

Files (new): `lean/VE/Events/{Decl,Premises,Calendar,Completion,Conservative,Wire,Chain}.lean`, `lean/EVENTS.md`;
ET-7: `lean/VE/Alternatives/FillWire.lean`. Names have prefix `VE.Events.` (ET-7: `VE.Alternatives.`); no theorem
name contains a prime, and no name or comment contains a word `lean/audit.py` rejects. Without Mathlib
(`lean/lakefile.toml` has no `require`), order lemmas are proved locally.

The blocks below are draft 1's statement schemata, corrected only where the review requires it (A, X1, X2). The
reviewed statements, with the calendar completion theorem (`dayExtension_transfer`, `completion_extension`,
`completion_reading`), the fragment (`up`, `down`, `hits`, `vacuous`) and the answer-level theorems
(`events_model_calendar`, `events_witness_calendar`, `events_settled_calendar`, `events_undecided_calendar`), are in
[events-time-causation.md](events-time-causation.md) 6, which supersedes these blocks.

### 3.1 Definitions (ET-3)

```lean
namespace VE.Events
open VE.Norms (Sat tupleVal)
open VE.Time (Civil parseIso dateMax)

structure EventSort where
  sort : String          -- a declared user sort
  on   : String          -- base predicate (sort, day); verbalisation "{0} happens on {1}"

structure StateSort where
  sort   : String
  begins : String        -- (sort, day); "{0} begins on {1}"
  ends   : String        -- (sort, day); "{0} ends on {1}"

inductive LinkForm where
  | contributed          -- "{0} contributed to {1}"
  | necessary            -- "{0} was necessary for {1}"
  deriving DecidableEq, Repr

structure Link where
  predicate : String     -- base predicate (cause sort, effect sort); an open term
  form      : LinkForm
  decidedBy : Option String   -- none = "unstated"

structure EventsEnv where
  day     : String
  before  : String
  events  : List EventSort
  states  : List StateSort
  dates   : List Civil    -- decoded, valid, sorted by Civil.num, no duplicates (anchor included)
  anchor  : Option Civil
  links   : List Link

def dateName (D : Civil) : String                       -- "date__YYYY_MM_DD"
def regenEnv (E : VE.Environment) (V : EventsEnv) : VE.Environment
  -- E plus one constant `dateName D` of sort V.day for each D ∈ V.dates
def WellFormedEvents (E : VE.Environment) (V : EventsEnv) : Bool   -- 2.9 items 3-7

def irreflexiveF (V : EventsEnv) : VE.Formula :=
  .all V.day (.not (.binary V.before (.var 0) (.var 0)))
def transitiveF (V : EventsEnv) : VE.Formula :=
  .all V.day (.all V.day (.all V.day
    (.implies (.and (.binary V.before (.var 2) (.var 1)) (.binary V.before (.var 1) (.var 0)))
              (.binary V.before (.var 2) (.var 0)))))
def linearF (V : EventsEnv) : VE.Formula :=
  .all V.day (.all V.day (.or (.binary V.before (.var 1) (.var 0))
    (.or (.eq (.var 1) (.var 0)) (.binary V.before (.var 0) (.var 1)))))
def oneDayF (V : EventsEnv) (sort role : String) : VE.Formula :=     -- guarded form (A)
  .all sort (.all V.day (.implies (.binary role (.var 1) (.var 0))
    (.all V.day (.implies (.binary role (.var 2) (.var 0)) (.eq (.var 1) (.var 0))))))
def notBeforeBeginF (V : EventsEnv) (s : StateSort) : VE.Formula :=
  .all s.sort (.all V.day (.implies (.binary s.begins (.var 1) (.var 0))
    (.all V.day (.implies (.binary s.ends (.var 2) (.var 0)) (.not (.binary V.before (.var 0) (.var 1)))))))
def dateFacts (V : EventsEnv) : List VE.Formula
  -- for consecutive D, D' in V.dates: .binary V.before (.const (dateName D)) (.const (dateName D'))
def adjacentFacts (V : EventsEnv) : List VE.Formula
  -- for consecutive D, D' with D'.num = D.num + 1:
  -- .all V.day (.not (.and (.binary V.before (.const (dateName D)) (.var 0)) (.binary V.before (.var 0) (.const (dateName D')))))
def linkForwardF (V : EventsEnv) (l : Link) : VE.Formula      -- 2.3 link_forward: start role of the cause, bound role
                                                              -- of the effect (`on`, or `ends` for a state; D)
def linkWeakerF (V : EventsEnv) (n c : Link) : VE.Formula     -- 2.3 link_weaker

def orderPremises (V : EventsEnv) : List VE.Formula := [irreflexiveF V, transitiveF V, linearF V]
def conventionPremises (V : EventsEnv) : List VE.Formula
  -- one_day per event sort, one_begin/one_end/not_before_begin per state sort, link_forward per link,
  -- link_weaker per (necessary, contributed) pair on one sort pair, in declaration order
def eventsPremises (V : EventsEnv) : List VE.Formula :=
  orderPremises V ++ dateFacts V ++ adjacentFacts V ++ conventionPremises V

/-- A calendar reading of S: its days are numbered as civil days, `before` is `<`, named dates denote their days,
    and every civil day `0..dateMax` is a day of S (`onto`: the day domain is fixed, A). Without `onto` it is only an
    embedding, which is what a finite situation has. -/
structure CalendarReading (V : EventsEnv) (S : VE.Structure.{u}) where
  num    : S.Carrier → Nat
  inj    : ∀ x y, S.domain V.day x → S.domain V.day y → num x = num y → x = y
  range  : ∀ x, S.domain V.day x → num x ≤ dateMax
  onto   : ∀ n, n ≤ dateMax → ∃ x, S.domain V.day x ∧ num x = n
  order  : ∀ x y, S.domain V.day x → S.domain V.day y → (S.relation V.before [x, y] ↔ num x < num y)
  dates  : ∀ D ∈ V.dates, ∃ x, S.constant (dateName D) = some x ∧ S.domain V.day x ∧ num x = D.num

/-- 2.5, decidable on finite situations. -/
def embeddable {α} [DecidableEq α] (V : EventsEnv) (M : VE.FiniteModel α) : Bool

/-- The vocabulary the block does not touch: no day sort, no predicate or constant with the day sort in its
    signature (so no `before`, no role, no day-indexed author predicate, no named date), no link predicate. -/
def oldEnv (E : VE.Environment) (V : EventsEnv) : VE.Environment
```

### 3.2 Theorems (ET-3)

```lean
/-- Every generated premise is closed and typed over the regenerated environment. -/
theorem eventsPremises_wellFormed (E : VE.Environment) (V : EventsEnv) (h : WellFormedEvents E V = true) :
    ∀ p ∈ eventsPremises V, p.WellFormed (regenEnv E V) []

/-- The intended reading satisfies the order and date premises (on any structure admissible for the regenerated
    environment, so every `before` tuple is a pair of days). -/
theorem calendar_sat (E : VE.Environment) (V : EventsEnv) (h : WellFormedEvents E V = true)
    (S : VE.Structure.{u}) (hS : S.Admissible (regenEnv E V)) (c : CalendarReading V S) :
    Sat S (orderPremises V ++ dateFacts V ++ adjacentFacts V)

/-- Named dates are ordered exactly as the calendar orders them, in every structure of the premises. -/
theorem datesOrder_iff (E : VE.Environment) (V : EventsEnv) (h : WellFormedEvents E V = true)
    (S : VE.Structure.{u}) (hS : S.Admissible (regenEnv E V))
    (hp : Sat S (orderPremises V ++ dateFacts V)) (D D' : Civil) (hD : D ∈ V.dates) (hD' : D' ∈ V.dates) :
    (VE.Formula.binary V.before (.const (dateName D)) (.const (dateName D'))).denote S [] ↔ D.num < D'.num

/-- One owner of the calendar: the generated order agrees with W6a's chronological order. -/
theorem datesOrder_calendar (D D' : Civil) (hD : D.Proper) (hD' : D'.Proper) :
    D.num < D'.num ↔ D.Before D' :=
  (VE.Time.before_iff hD hD').symm

/-- The premises are satisfiable by a finite calendar situation (no vacuity from the pack alone). -/
theorem eventsPremises_satisfiable (E : VE.Environment) (V : EventsEnv) (h : WellFormedEvents E V = true) :
    ∃ M : VE.FiniteModel VE.Bridge.Entity, M.Valid (regenEnv E V) ∧ Sat M.asStructure (eventsPremises V) ∧
      embeddable V M = true

/-- A calendar-embeddable finite situation has a numbering into the calendar (an embedding, not onto); the calendar
    completion (events-time-causation.md 1.7) adds the missing days and is a calendar reading. -/
theorem embeddable_sound {α} [DecidableEq α] (E : VE.Environment) (V : EventsEnv) (h : WellFormedEvents E V = true)
    (M : VE.FiniteModel α) (valid : M.Valid (regenEnv E V)) (hp : Sat M.asStructure (eventsPremises V))
    (he : embeddable V M = true) :
    Embeds V M.asStructure (numbering V M)

-- The calendar completion keeps the value of every formula in the fragment (A, X2): stated in
-- events-time-causation.md 6.2 as `dayExtension_transfer`, `completion_extension` and `completion_reading`.

/-- Conservativity: for premises and a conclusion that mention no day, no role, no link and no named date, adding
    the block's premises changes no consequence. Proof by restriction (forget the new relations) one way, and by an
    expansion on the carrier `S.Carrier ⊕ ULift Nat` the other way, whose day domain is the named dates' days and day
    0, ordered by `<` (author day constants sent to day 0; role, link and day-indexed relations empty), with the lemma
    that a formula over `oldEnv E V` denotes the same in `S` and in the expansion. -/
theorem events_conservative (E : VE.Environment) (V : EventsEnv) (h : WellFormedEvents E V = true)
    (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, a.WellFormed (oldEnv E V) []) (hφ : φ.WellFormed (oldEnv E V) []) :
    (∀ S : VE.Structure.{u}, S.Admissible (regenEnv E V) → Sat S (eventsPremises V) → Sat S Γ → φ.denote S []) ↔
    (∀ S : VE.Structure.{u}, S.Admissible (oldEnv E V) → Sat S Γ → φ.denote S [])
```

### 3.3 Wire and the chain hook (ET-4)

`decodeEvents` decodes the block from the environment JSON, checks 2.9, regenerates the environment and `Ev_V`.
`eventsX` is the pack's contribution to `X`: PK-1's `events` pack (`decls` the named-date constants, `labelled`
`Ev_V` with labels `events:<name>`, `origins` each label and date's request path in the block), registered with PK-1
by one provider line, last in PK-1's order (X1). PK-1's assembler, owned by the RD-9 composition owner of
`lean/VE/NormDefaults/Layered.lean`, builds `X` from the packs; events has no assembly of its own. On
`rd-9/integrate` the names below exist: `VE.NormDefaults.EntailsX`, `VE.NormDefaults.acceptanceX`,
`VE.NormDefaults.modelCheckX`, `VE.NormDefaults.modelCheckX_sound`, `VE.NormDefaults.Wire.premisesX`,
`VE.NormDefaults.Wire.BaseAdmissibleX`, `VE.NormDefaults.FiniteFill`, `VE.NormDefaults.finFill`,
`VE.NormDefaults.withFill`.

```lean
namespace VE.Events
open VE.NormDefaults (UDoc fill WellFormedU EntailsX acceptanceX modelCheckX modelCheckX_sound FiniteFill)

def decodeEvents (environment : Lean.Json) : Except String (Option (EventsEnv × VE.Environment))
  -- none when the block is absent; otherwise the decoded block and the regenerated environment
def eventsX (V : EventsEnv) : List VE.Formula := eventsPremises V

/-- Absent block, no pack: the instance of PK-1's rule that an absent pack contributes nothing (X1), so the assembled
    X is the other packs' X. -/
theorem eventsX_absent (environment : Lean.Json) (h : (environment.getObjVal? "events").toOption = none) :
    decodeEvents environment = .ok none

/-- ET-4's certified entailment, on the layered route, at PK-1's assembled X (events last, so `X ++ eventsX V`): an
    accepted certificate with the pack's premises is an `EntailsX` with them; and it holds in every calendar
    reading. -/
theorem events_certificate_calendar (U : UDoc) (h : WellFormedU U = true) (V : EventsEnv) (X Γ : List VE.Formula)
    (φ : VE.Formula) (hX : ∀ a ∈ X ++ eventsX V, a.WellFormed (VE.Norms.envAt (fill U) 0) [])
    (cert : VE.Tableau.Certificate)
    (hv : VE.Tableau.checkCertificate (VE.Norms.envAt (fill U) (VE.Norms.size (fill U)))
            (VE.NormDefaults.Wire.premisesX U (X ++ eventsX V) Γ) φ cert = true) :
    EntailsX U (X ++ eventsX V) Γ φ

/-- A countermodel or witness is reported as a refutation only when it is calendar-embeddable and inside the
    completion fragment for every formula the check read (A, X2); then a calendar situation with every civil day
    satisfies the whole assembled X and the premises, and gives the conclusion the reported value. Stated in full in
    events-time-causation.md 6.3 (`events_model_calendar`, and its siblings for witnesses and statuses). -/
theorem events_countermodel_calendar (U : UDoc) (h : WellFormedU U = true) (V : EventsEnv) (X : List VE.Formula)
    (M : VE.FiniteModel VE.Bridge.Entity) (valid : M.Valid (VE.Norms.envAt U.D 0))
    (F : FiniteFill U VE.Bridge.Entity) (Γ : List VE.Formula) (φ : VE.Formula)
    (hm : (modelCheckX U (X ++ eventsX V) M F Γ φ).1 = true) (he : embeddable V (M.withFill F) = true)
    (hs : modelSafe U V X Γ φ (modelCheckX U (X ++ eventsX V) M F Γ φ).2 = true)
    (hE : EventsTyped (VE.Norms.envAt U.D 0) V = true) :
    ∃ (S : VE.Structure.{0}) (c : CalendarReading V S), VE.NormDefaults.Wire.BaseAdmissibleX U (X ++ eventsX V) S ∧
      (∀ a ∈ Γ, (VE.Norms.subst (fill U).T (VE.Norms.size (fill U)) a).denote S []) ∧
      ((VE.Norms.subst (fill U).T (VE.Norms.size (fill U)) φ).denote S [] ↔
        (modelCheckX U (X ++ eventsX V) M F Γ φ).2 = true)

/-- The wire: a replayed entailment on an events document decodes to exactly this block and holds with its premises. -/
theorem events_wire_acceptance (j : Lean.Json) (r : EventsEntailmentReplay) (h : replayEventsEntailment j = .ok r)
    (hv : r.valid = true) :
    decodeEvents (j.getObjValD "environment") = .ok (some (r.V, r.E)) ∧
    EntailsX r.U (r.X ++ eventsX r.V) r.premises r.conclusion
```

`events_certificate_calendar` is `acceptanceX` with `X ++ eventsX V`; with `calendar_sat` it gives the statement of
D7 (every calendar reading satisfying the conventions and `Γ` satisfies `φ`). The readings route uses the same `X`
per choice (RD-9's `choiceX`); `events_wire_acceptance` is instantiated per route that enables the profile, as nd's
wire theorems are.

### 3.4 `alternatives@0` with the completion (ET-7)

```lean
namespace VE.Alternatives
open VE.NormDefaults (UDoc fill WellFormedU ConflictFreeU BaseAdmissibleAltU backgroundBaseAltU
  allFollowableU followableFU followableU_sound FiniteFill)

structure AltSourceU where
  src    : Wire.AltSource
  unspec : List String           -- regulated predicates whose `default` is "unspecified"

def decodeAltSourceU (environment document : Lean.Json) : Except String AltSourceU
def notFollowableFU (A : AltDoc) (unspec : List String) : VE.Formula := .not (followableFU A unspec)

/-- No `unspecified` value and no `norm-defaults@0`: exactly today's decoder, with `unspec = []`. -/
theorem decodeAltSourceU_conservative (environment document : Lean.Json)
    (h : noUnspecified environment = true) :
    decodeAltSourceU environment document = (Wire.decodeAltSource environment document).map (fun s => ⟨s, []⟩)

/-- FOLLOWABLE on the wire, with the completion (`followableU_sound`, proved, applied to the replayed source). -/
theorem alternativesU_wire_followable_sound (j : Lean.Json) (res : FollowableUReplay)
    (h : replayFollowableU j = .ok res) (hv : res.followable = true) :
    decodeAltSourceU (j.getObjValD "environment") (j.getObjValD "document") = .ok res.src ∧
    WellFormedU ⟨inlineTree res.src.src.A, res.src.unspec⟩ = true ∧
    ConflictFreeU ⟨inlineTree res.src.src.A, res.src.unspec⟩ ∧
    ∀ B, BaseAdmissibleAltU res.src.src.A res.src.unspec B → VE.Norms.Sat B res.src.src.A.Γ →
      (allFollowableU res.src.src.A res.src.unspec).denote B []

/-- DILEMMA with the completion: a valid witness, a filling of its silences and a typed chooser at which
    ¬followable° holds refute the document-wide claim. -/
theorem alternativesU_dilemma_witness_sound {α} [DecidableEq α] (A : AltDoc) (unspec : List String)
    (h : WellFormedU ⟨inlineTree A, unspec⟩ = true) (M : VE.FiniteModel α)
    (F : FiniteFill ⟨inlineTree A, unspec⟩ α) (valid : M.Valid (VE.Norms.envAt (inlineTree A) 0))
    (hb : backgroundValidAlt A M = true) (hfill : fillValid ⟨inlineTree A, unspec⟩ M F = true)
    (hΓ : A.Γ.all (fun p => p.eval M []) = true) (r : α) (typed : M.inDomain A.alt.chooser r)
    (hd : (notFollowableFU A unspec).eval (M.withFill F) (tupleVal [r]) = true) :
    ¬ (∀ B, BaseAdmissibleAltU A unspec B → VE.Norms.Sat B A.Γ → (allFollowableU A unspec).denote B [])
```

`fillValid` is the Boolean filling check of `modelCheckU` (named as merged in `lean/VE/NormDefaults/Evidence.lean`);
`M.withFill F` is `VE.FiniteModel.withFill`. The scenario answer's values per alternative follow the evidence
contract (C, 2.10): clear or not clear from a definite Kleene value (`kleene_sound`) or enumeration of the cone, each
settled under every admissible filling; UNDECIDED only from two validated fillings with opposite values; UNKNOWN
otherwise, a Kleene "unknown" included. Nothing new is claimed for the untrusted diagnosis, which lists under
`UNSETTLED` only alternatives with UNDECIDED evidence. The statements (`SettledF`, `UndecidedF`, the scenario row with
its soundness fields) are in events-time-causation.md 6.4.

## 4. Fixtures

Definitions first, expectations after, so a reviewer derives each expectation before reading it (as alt 8).

### 4.1 Synthetic (`#guard` in Lean, the same cases through the service in Python)

| # | Definition | Expected |
|---|---|---|
| T1 | block with day sort `day`, `before`; no events; dates 2026-10-12, 2027-01-05 (dates from 1970 on, G) | 3 order premises, 1 date premise, 0 adjacency; `datesOrder_iff` true for (2026, 2027) and false for (2027, 2026) |
| T2 | dates 2026-10-12, 2026-10-13 | 1 date and 1 adjacency premise; "there is a day such that that day is after 12 October 2026 and that day is before 13 October 2026" refuted by certificate |
| T2b | no dates; the claim "for each day and each day, if neither day is before the other, the two days are the same day" (I) | certified, and the certificate needs `linear`: with `linearF` dropped (ET-3's seeded bug) it is not accepted |
| T3 | dates 2026-10-12, 2026-10-14; a model with three unnamed days strictly between them | `NotCalendar: 3 days between 2026-10-12 and 2026-10-14, at most 1` and UNKNOWN; with one unnamed day: accepted |
| T3b | dates 2026-10-12, 2026-10-14; a situation with exactly those two days and no day between them; the claim "there is a day such that that day is after 12 October 2026 and that day is before 14 October 2026" (A) | never refuted: UNKNOWN with `NotCalendar`; a situation with one day between them is a calendar situation in which the claim holds |
| T3c | date 2026-10-12; a situation whose last day is 12 October 2026; the claim "there is a day such that that day is after 12 October 2026" (A, edges) | never refuted: UNKNOWN with `NotCalendar` |
| T4 | event sort `act`, `committed_on`; a situation with one act on two days | `InvalidModel("events", "premise events:one_day:act fails")` |
| T5 | state sort `marriage`; a situation in which a marriage ends before it begins | `InvalidModel("events", "premise events:not_before_begin:marriage fails")` |
| T6 | link `contributed_to` (event → event), a situation in which the effect happens before the cause; link `contributed_to_state` (event → state), a cause after the state's last day, and a cause after the state began but before it ended (D) | `InvalidModel("events", "premise events:link_forward:contributed_to fails")`; the second fails `events:link_forward:contributed_to_state`; the third is accepted (a later event may contribute to a state in progress) |
| T7 | a document with no day vocabulary in any rule or premise, with and without the block | same statuses and verdicts; certificates differ only in their bound premise list (`events_conservative`) |
| T8 | identity: every existing fixture without the block | `environment_id` and every hash unchanged; with the block, `environment_id` changes |
| T9 | each wording of 2.7, a role wording "{0} is committed on {1}" and one without " on {1}" | one derivation each; the second role wording `EventsVerbalisation`; the twelve source words of 2.7 rejected in authored text with the advice of 2.7 |
| T10 | 65 named dates; a date 1969-12-31; a declared constant `date__x` | `ResourceLimit: events dates`; `DateRange: 1969-12-31`; `EventsReserved: date__x` |
| T11 | `until`, D9, permission: rule U1 "Every person may be presumed innocent on each day, if it is not the case that there is a conviction such that that conviction is of that person and that conviction happens no later than that day." with `presumed_innocent_permitted` unspecified; U2 adds "must not" for the days on which a conviction of that person happens no later than that day; situation: a conviction on 5 January 2027, days 4, 5 and 7 January 2027 (E's own day included, R2) | 4 January: both SETTLED yes; 5 and 7 January: U1 UNDECIDED (the text does not say), U2 SETTLED no; the situation is the reading set's distinguishing situation |
| T11b | `until`, obligation: "must file a report on each day ... until a closure", U2 adds "need not" from the closure's day; `x_permitted` unspecified with no rule | 7 January: U2 SETTLED not required, and filing is never SETTLED forbidden (the obligation stops; nothing is forbidden) |
| T11c | `until <date>`: "valid until 31 December 2026", four candidates (exclusive or inclusive, silent or ending) | the distinguishing situation has 31 December 2026 (exclusive against inclusive) and 1 January 2027 (silent against ending) |
| T12 | ET-7: nd fixture u10 (pull forbidden, push with no rule, `permitted` unspecified) | DILEMMA, diagnosis `UNSETTLED(push)` with two validated fillings for push; with "Every action may be performed, if that action is push." FOLLOWABLE |
| T12b | ET-7, the excluded-middle case (C): push's permission guarded by nd u12's guard ("if that agent may Y, or it is not the case that that agent may Y"), `y_permitted` unspecified | Kleene unknown; enumeration settles push clear; never UNDECIDED; with `MAX_UNSAID_ATOMS = 0` UNKNOWN naming the budget |
| T13 | strict precedence (E): events `confirmation`, `action`; "that confirmation happens before that action"; a confirmation on 12 October 2026 and an action on 13 October 2026, then both on 13 October 2026 | certified true, then its negation certified (the same day is not before); never UNDECIDED |

### 4.2 From the pilots (real units, run `20261012T1800Z`)

| # | Unit | VE text (sketch; the batch writes the final text) | Expected |
|---|---|---|---|
| P1 (ET-0) | U u042, 200 B | sorts `finding of guilt` (one finding that one person is guilty of a penal offence), `act` (one act or omission), `day`; regulated `finding_of_guilt_permitted(finding)` with act "{0} take place", `default: unspecified`; rule: "No finding of guilt may take place, if there is an act such that that finding of guilt is on account of that act and there is a day such that that act is committed on that day and it is not the case that that act constitutes a penal offence under national or international law on that day." The bearer stays as in u098 (unassigned) | loads and checks on today's chain; conflict-free with its part; the audit samples it FAITHFUL (bar) |
| P2 (ET-0) | U u043, 118 B | as P1 with an `imposition` sort and "a heavier penalty than the penalty that was applicable ... on that day": `heavier_than(penalty, penalty)` a named open comparison; "applicable to that offence on that day" needs a third place, so it is reified as an `applicability` state or the unit stays UNFORMALISED | recorded either way; claimed only if the audit accepts the reification |
| P3 (ET-1) | C u0172.s01 (119 B), u0172.s02 (213 B) | component on the alternatives route: chooser `decision` (one decision of one instance of Claude about one request), action `response`, harm `harm`; `inaction` declared; the ten hard constraints as prohibitions on responses with the pilot's open terms and the shared "knowingly or quite likely" condition; premises Γ: "For every decision there is a response such that that response is available to that decision and that response is inaction." and "No response that is inaction provides serious uplift to ... [each category]" (support: testimony, cites u0172.s02); legend: "This document holds only the hard constraints; 'may be given' means no hard constraint forbids it." | FOLLOWABLE, `conditional_on` both premises; without the first premise UNKNOWN (the existence fact is validated, not assumed: alt fixture u) |
| P4 (ET-1) | C u0171.s03, 276 B | in the same component: "Every response that clearly and substantially undermines Anthropic's ability to oversee and correct advanced AI models, if Claude knows or thinks it quite likely that it does, may not be given, even if there is a harm such that that response prevents that harm." as an entailed assertion; scenario: responses `undermine`, `refuse` (inaction), `answer`; harm `attack`; rows `refuse` and `answer` lead to `attack`, `undermine` does not | entailment certified; scenario: `undermine` prevents `attack` and is forbidden; "decision D has a clear action: refuse, answer" |
| P5 (ET-1) | C u0171.s01 (147 B), u0171.s02 (159 B), u0172.s03 (212 B) | the component's report: no obligation, so nothing requires prevention ("unmapped obligations: none"); u0172.s03's "refusal is not necessarily compatible with the other priorities" points outside the component | OPEN or LABELLED as the audit decides; claimed only then |
| P6 (ET-6) | U u041, 201 B | reading set {U1, U2} of T11 (D9, the permission case) over `presumed_innocent_permitted(person, day)`; the trial as an event with open conditions ("according to law", "public", "all the guarantees necessary for his defence") | READINGS with the T11 distinguishing situation |
| P7 (ET-6) | U u058, 91 B | state sort `marriage` with `begins`, `ends`; "on each day on which that marriage is in progress" and "on the day that marriage ends"; "equal rights" kept as in the rights translation | partly: the phases expressed; "equal rights" stays with `rights`/`quantities`; claimed only if the audit accepts the whole unit |
| P8 (ET-6) | U u042, u043 restated | P1 and P2 with `committed_on` as the `act` sort's `on` role (one day per act), its wording "{0} is committed on {1}" (R3) | same verdicts; fidelity: "the time when it was committed" is now one day |
| P9 (ET-9) | U u004, 127 B | events `disregard of human rights` (a state), `barbarous act` (event kind as a sort), `outrage of the conscience of mankind`; links "contributed to", decided by "the drafters"; "barbarous" open. Rechecked under D: the disregard (a state) does not begin after the day of an act it contributed to; an act does not start after the last day of the outrage when the outrage is a state that ends; no day is stated, so the conventions constrain nothing the unit asserts | OPEN; `causal_links` lists both links with support testimony |
| P10 (ET-6, probe) | C u0204.s03, 316 B | "Claude should ideally raise concerns before undertaking a task": events `raising of concerns`, `undertaking`; "happens before"; the "should ideally" force and the harm comparison stay with soft norms and `quantities` | probe only; claimed only with those features |
| P11 (ET-6, probe) | C u0022.s01, 67 B | anchor date; "there is a day such that that day is after the date of this document and this document changes on that day", hedged "likely" | the time part admitted; the unit is claimed only with `attitudes`' hedge |

### 4.3 Use-case regressions

| # | Case | Expected |
|---|---|---|
| R1 | eligibility rule R5's "throughout" in reg. 3(3) only, with no amounts (R1 edit), on the norms chain (`documents@1`, `events@0`, `norm-defaults@0`, `norms@0`, `relational-fol@0`; eligibility's own `order@0`/`time@0` environment is refused, D12): a `stay` state (`begins`, `ends`) and the claim "that stay is in progress on each day from 21 September 2026 through 27 September 2026" per case | which days each case's stay is in progress, matching the answer key: C26 (2026-06-29 to 2026-09-27) in progress throughout, certified; C25 (to 2026-09-26) and C27 (to 2026-09-20) not, each certified. A case with no end day is in progress throughout only with an explicit no-end premise (F), certified then; without it the claim is not entailed, with a calendar countermodel. R1 is inside the completion fragment (ET-2, A): its refutations are universal claims refuted at listed days; a countermodel to the claim's negation is outside it and gives UNKNOWN |
| R2 | asimov-laws with `permitted` switched to `unspecified` (ET-8) | the README's measured bound becomes the computed result: clear actions only where a rule permits; diagnoses `UNSETTLED(...)` only where two validated fillings show a silent permission is all that is left (C) |
| R3 | agent-policy "confirmed before the action" | **a trigger, not a regression** (ET-T4): agent-policy carries `data@0`, which D12 refuses, and its source needs order within a day. The day-level part is T-fixture T13 (strict precedence: a confirmation on the action's own day is not "before" it, E) |

## 5. Batches

Each batch is 2 to 6 hours. "Pilot" batches change pilot files under `manage-agents/pilots/` only. Every batch that
changes product code plants a seeded bug per behaviour claimed, in each language changed, and records the failing test
(CLAUDE.md). Generated files are regenerated with `uv run python tools/regen_generated.py --write`, never edited.

### ET-0. UDHR u042 with an event sort and a day sort (pilot, 2-3 h, no product code)

Smallest batch that moves a pilot number; an audited pilot with no promised byte gain. Rewrite u042 (P1) in its part
document; attempt u043 (P2); run the part's `ve document check`; record the unit in `units.json` with the new status.
Runs now. **Pre-registered bar**: u042 loads and checks,
its part stays conflict-free under every reading, and the next scheduled audit samples it FAITHFUL (or a targeted
audit of the changed unit does). **Stop**: if the audit rejects the reification, record why and claim nothing.
*Estimate*: 200 B (1.83% of UDHR); 318 B with u043. Shared files: none in the repository.

### ET-1. The constitution's hard-constraint argument as an alternatives component (pilot, 3 h, no product code)

Step 1: check that `ve document check` accepts a document on `alternatives@0`, `documents@1`, `norms@0`,
`relational-fol@0` (composition: route `alternatives` exists today); if not, run the component with the route's own
cases (`alt-followable`, `alt-certificate`, `alt-validate`) and record the units as OPEN only. Step 2: write the
component (P3 to P5) as a part document cited from the ledger, as the UDHR parts are. Step 3: FOLLOWABLE certificate,
the u0171.s03 entailment and scenario. **Bar**: FOLLOWABLE replayed with `conditional_on` the two premises; the
entailment certified; the targeted audit FAITHFUL on u0171.s03, u0172.s01, u0172.s02. *Estimate*: 755 B (0.41% of the
constitution); 1,126 B with P5, not a promised gain (an audited pilot). Runs now. The component is a separate part
document: it does not edit u0165.s01–s07, so it is outside the hard-constraint queue (X10). Shared files: none in
the repository.

### ET-2. Statement spec and stub elaboration (planner, 4-5 h)

[events-time-causation.md](events-time-causation.md) (item 1): sections 2 and 3 of this plan as reviewed statements,
diagnostics, wire, fixtures with expectations separated; every Lean block of 3 elaborated in an untracked stub against
`main` and `rd-9/integrate` (as RD-9 SC-0), names fixed (PK-1's provider registration, the layered decoder,
`fillValid`). It writes draft 2's contract: the fixed day domain and the calendar completion theorem over the whole
assembled `X` with its fragment, and where R1 falls (A, X2); the completeness report in place of D4's claim (B);
ET-7's evidence contract (C); the link conventions (D); strict precedence (E); persistence (F); dates from 1970 (G);
the gate as AR-10's row (H, X3); the linearity fixture (I); R1 narrowed, `data@0` decided, "until" per modality with
the end day and the inclusive date readings, and the per-role wordings (R1 to R3); the pack's `kind` with the
condition under which PK-1 may count it as a conservative step (X2). Pruning is an option only (6.5 of the spec).
Gate: the statement review the DRI assigns (two frontier reviewers), each reviewer deriving T1-T13 and P1-P11 before
reading the expectations; ET-7 may start once the review accepts the spec's ET-7 section, before the timeline
sections pass. Shared files: none. *Estimate*: 0 pilot bytes (specification).

### ET-3. Lean: block, premises, calendar, conservativity, completion (Lean, 5-6 h)

`lean/VE/Events/{Decl,Premises,Calendar,Completion,Conservative}.lean` and `lean/EVENTS.md`: 3.1 and 3.2 as the
spec states them (with the calendar completion theorem and its fragment), T1-T8, T10 and T13 as `#guard`. Lean-core
work that runs in parallel with the other plans' cores (X10). Seeded bugs: drop `linearF` from `orderPremises` (T2b's
certificate fails; T2 follows from the adjacency premise alone, I); generate all-pairs date facts in reverse order (T1
fails); skip the gap count in `embeddable` (T3 fails); let `before` serve as a guard in `hits` (T3b's refutation is
reported). Shared files (append-only): `lean/VE.lean`
(imports), `lean/VE/Audit.lean` (audit entries). Generated: `lean/declarations.txt`, `lean/statements.txt`,
`lean/predicates.txt`, `lean/axioms.txt` and anything `regen_generated.py --list` names for new Lean sources.
Conflicts: new directory only; the two shared files take one appended block each. *Estimate*: 0 pilot bytes
(infrastructure).

### ET-4. Lean: wire, the pack, report fields (Lean, 5-6 h; after PK-1, AR-10's table, and RD-9 SC-6 and SC-8 merge)

`lean/VE/Events/{Wire,Chain}.lean`: `decodeEvents`, `regenEnv` on the wire, `eventsX` as PK-1's `events` pack (its
provider registration line), `embeddable` and the completion fragment applied to every reported situation (UNKNOWN
with `NotCalendar` outside it, certificates kept), the report fields `named_dates`, `events_premises` (labels),
`causal_links` and the norms 7.1 `fragment` line after expansion (B); 3.3's theorems as the spec states them; the
`events@0` row of AR-10's profile-gate table with its composition proof (X3); the response shapes for the new fields
in `lean/ResponseShape/Schemas/` with encoder theorems in `lean/ResponseShape/Encoders/` (listed in
`lean/ResponseShape/Audit.lean`). Optionally, pruning of the order premises, only with its own preservation theorem
covering declarations as well as formulas (two declared dates and "all days are equal" are inconsistent with the full
pack, not without its order premises), under its own statement review; it is not a promised fallback (J). Seeded
bugs: append `eventsX` before soft's premises (binding fixture fails: a check of PK-1's order, X1); report a
non-embeddable countermodel (T3 through the service fails); report a countermodel outside the fragment (T3b through
the service fails). Shared files: PK-1's provider registration line (one line), the files RD-9 owns for the layered
dispatch only through that line, AR-10's table (one row), `lean/VE/Audit.lean`, `lean/ResponseShape/Audit.lean`.
In PK-1's integration order on `Layered.lean` (AT-2/AT-3a → WG-3 → ET-4 → QT-B2) it lands after WG-3 and before
QT-B2 (X1, X10). Generated: the service schemas (`ve/backends/lean_service_schema/*.json`,
`tools/response_schemas.py --write` through `regen_generated.py`), `lean/checkers.lock`. *Estimate*: 0 pilot bytes
(infrastructure).

### ET-5. Python and English: wordings, advice, relay, fuzz (Python, 4-5 h; after ET-E1)

The wordings of 2.7, as ET-E1 left them, and the source-word reading sets and authored-text refusals with rewrites, as
rows in english-lean's catalogue (rows only, X9); if that catalogue lives in `lean/VE/EnglishGrammar/*` when ET-5
runs, ET-5 joins the serialised English queue (`AT-5 → QT-A6 → ME-11 → QT-B3 → SC-7`) in landing order. W6's
date-literal class reused; block shape in `ve/environment.py` only if Python still checks environment shape there; no
`ve/profiles.py` row and no gate mirror: Python reads AR-10's generated data (X3); `ve/events.py` relays the report
fields and binds them to the request (every named date, label and link the answer names exists in the request; no
extra row); T9 and the binding fixtures; fuzz tests in `tests/test_events_answer.py` mutating genuine answers one and
two faults at a time (each member dropped, emptied, retyped, duplicated, reordered; an index out of range): every
mutant `CheckerUnavailable` or changing nothing shown. Seeded bug: accept a link wording equal to alternatives' `leads
to` (the disjointness test fails). Shared files: `ve/document.py` (profile acceptance; it joins the document-mode queue
after `lf-16g`, in landing order AT-3b, SC-1b, QT-A4, ET-5, WG-4, ME-10, X10), `ve/backends/service_schema.py` (only
if `MODES` changes, which D3 avoids), `tools/layer_policy.py` (layers of the new files). Generated:
`tools/gate-collection.json`, `tests/data/route-cases.jsonl` (via `tests/route_case_recorder.py`). *Estimate*: 0
pilot bytes (infrastructure); the use-case regression R1 (narrowed) becomes runnable; R3 stays the trigger ET-T4.

### ET-6. Pilot: dated events and states (pilot, 3-4 h; after ET-5)

UDHR P6, P7, P8 and the constitution probes P10, P11. Measure `ve document check` time per UDHR part before and after
the block. **Bar**: P6 READINGS with the T11 situation shown; u041 FAITHFUL in a targeted audit; ET-E1 rerun on the
wordings that changed since it last ran; check time per part at most 1.25 times the time without the block (lf-6's
target); otherwise record and stop adding the block to that part, and report it (the fallback stands; pruning is not
promised, J). *Estimate*: UDHR 201 to 548 B.

### ET-7. `alternatives@0` with the completion (Lean and Python, 5-6 h; independent of RD-9)

Starts once the statement review accepts the spec's ET-7 section (its evidence contract, C); Lean-core work that runs
in parallel with the other plans' cores (X10). `lean/VE/Alternatives/FillWire.lean`: 3.4 as the spec states it; the
alternatives runner dispatches lists with `norm-defaults@0` to it; the scenario's values under the evidence contract
(clear and not clear when settled, UNDECIDED from two validated fillings, UNKNOWN otherwise); `UNSETTLED` in the
untrusted diagnosis for alternatives with UNDECIDED evidence only. Delete the two refusals (2.11), the one in
`Dispatch.lean` serialised with AR-10's table (X3). Python: relay and display the values; the test asserting the
refusals rewritten. T12, T12b and nd fixture u11's alternatives part. Seeded bugs: report FOLLOWABLE from a
certificate over `backgroundBaseAlt` without `fillPremises` (T12 fails); render an UNDECIDED alternative as clear
(scenario test fails); report a Kleene-unknown alternative as UNDECIDED without two validated fillings (T12b fails).
Shared files: `lean/VE/Alternatives/Run.lean` (dispatch line), `lean/VE/Compose/Dispatch.lean` or AR-10's table row
(delete one refusal, with its proof, whichever has landed), `ve/profiles.py` (delete the mirror row only if it still
exists), `ve/alternatives.py` (relay), `lean/VE/Audit.lean`, the alternatives response shape and its encoder theorem.
Generated: `ve/backends/lean_service_schema/alternatives.json`, `tools/gate-collection.json`, `lean/checkers.lock`.
*Estimate*: 0 pilot bytes; it removes the Asimov case's modeling choice (ET-8).

### ET-8. Pilot: Asimov and the ET-1 component on the completion (pilot, 2-3 h; after ET-7)

R2; the ET-1 component switched from allow to `unspecified` for `may be given`, with the legend sentence removed (the
completion says "the text does not say" instead). **Bar**: Asimov's 13 rules still CHECKED and conflict-free, and the
count of models with a clear action reported. For the constitution component no outcome is pre-judged: refusal is
permitted by no rule, so the result is either FOLLOWABLE resting on a stated permission or DILEMMA
`UNSETTLED(refuse)`; the batch records which, with the targeted audit's view of whether u0172.s02 ("always compatible
with Claude's hard constraints") states a permission. *Estimate*: 0 new bytes; fidelity of the bytes ET-1 claimed.

### ET-9. Causal links (pilot and English, 4 h; after ET-5, on the link conventions ET-2's review settled, D)

P9; a sample of 20 constitution units of kinds (a), (d) and (e) (research 2.3) drawn with
`random.Random("ET-9").sample`, each written with links and the pilot's open terms where its hedges allow.
**Bar**: at least 5 of 20 become OPEN with the targeted audit FAITHFUL; otherwise links stay as designed but no
constitution bytes are claimed and the residual is recorded. *Estimate*: UDHR 127 B; constitution 600 to 1,500 B
extrapolated from the sample, of a 6,059 B upper bound.

### ET-D1. Design batch: alternatives beside `readings@1` (planner, 4 h; after ET-7)

The constitution's main document carries reading sets; C u0080.s03 (alt fixture f) needs a mapped obligation inside
it. Write the statements for `readings@1` × `alternatives@0` (per-choice inlining and slot premises as `X`), or record
why a component document is enough. No build without its own review. *Estimate*: 0 bytes now; C u0080.s03 (190 B)
if a build follows.

### ET-D2. Act-performance bridge (planner, design only, 4 h estimate; after ET-D1)

It specifies a predicate "x does A", relating an agent to an act (act-phrases' simple act, its act identity) through
events' event sorts and roles. Its statements must fit attitudes' contract, so that "intends to VP" and "wants Y to
VP" can be attitude conditions: content quantifier-free over the base vocabulary, at most one slot. It goes through its
own statement review; no build follows without a later batch. It needs ET-2, act-phrases' specification of act
identity (AP-1 to AP-3) and attitudes' AT-0. Until it passes, attitudes keeps intentional action residual; neither
act-phrases nor events landing changes that (X4). *Estimate*: 0 bytes.

### Experiments and triggers

- **ET-E1. Comprehension of the explicit wordings** (planner, 3 h; model calls with Sonnet 5.5 as the human proxy,
  DRI approval needed). Runs after ET-2 and before ET-5, in parallel with ET-3 and ET-4, which it does not block (R4).
  30 items: the wordings of 2.7, the "until" reading sets per modality (D9) and the T11 reading set. **Bar**: at least
  90% correct per wording, and the two "until" readings told apart in at least 90% of items; a wording below the bar
  is reworded before ET-5 writes it; ET-6 reruns it only on wordings that changed. Results from a model are early
  evidence, not proof about human readers.
- **ET-E2. Need for durations and deadlines** (planner, 3 h, model-free). Count, in both pilots and the use cases with
  answer keys, the sentences needing an offset over an event ("within 30 days after each request") or fulfilment by a
  deadline. **Bar**: 5 or more pilot units, or 2 or more answer-key use cases, start ET-T1; else record and stop.
- **ET-E3. Actual causation** (planner, 5-6 h, model-free). For 20 sampled causal units, write a structural model
  from what the source states only, and evaluate but-for and the three HP definitions by hand. **Bar**: at least 4 of 20
  gain a consequence beyond an open link that a blind audit judges faithful; else causal links stay open relations.
- **ET-T1. Integer days on the chain** (trigger: ET-E2's bar). A design batch for norms × integer days, after numbers2.
- **ET-T2. Multi-step choices** (trigger: a committed document that needs alternatives stage 2; asimov-extended's "which
  order came first" is the candidate). A design batch on causation-PLAN 1.6.
- **ET-T3. Dates before 1970.** Trigger: a pinned unit that needs a named date before 1970-01-01, such as UDHR's 1948
  date or math-evidence's 1887 observation sessions (H-10). It starts a design batch, under W6's own review, that
  extends `VE.Time.Calendar`'s valid range. There is no second calendar and no events-local date code. Until it
  fires, dates before 1970 are a stated limit (G, X8).
- **ET-T4. `events@0` beside `data@0`.** Trigger: a use case with an answer key that needs both, agent-policy's
  "confirmed before the action" (R3) being the candidate. It starts a design batch for AR-10's `events@0` row with
  `data@0` admitted and its composition proof; R3 also needs order within a day (`time-of-day`), so the batch says
  what part of R3 days can carry (R1, E).

### Order

The joint position of the review (round 3) and X10, in this order:

1. ET-0 and ET-1 now, as audited pilots with no promised byte gains.
2. ET-2 (this plan's draft 2 as the statement spec), under the statement review; its ET-7 section (C) may pass first.
   Then ET-7, then ET-8; ET-D1 after ET-7; ET-D2 after ET-D1.
3. ET-E1 after ET-2 and before ET-5, in parallel with ET-3 and ET-4; it does not block them.
4. ET-3 (Lean core, in parallel with the other plans' cores), then ET-4 (after PK-1, AR-10's table and RD-9 SC-6 and
   SC-8 merge; on `Layered.lean` after WG-3, before QT-B2), then ET-5 (in the English and document-mode queues of
   X9 and X10), then ET-6.
5. The causal-link conventions (D) are settled and reviewed in ET-2; ET-9 comes after ET-5.
6. ET-E2 and ET-E3 at any time.

Landing preference: ET lands after WG and before scope's SC-3…SC-7 (X10).

## 6. In-flight work, dependencies and merge conflicts

| In flight (branch) | What this plan needs from it | How a batch avoids conflicts |
|---|---|---|
| RD-9 (`rd-9/lean`, `rd-9/integrate`, `rd-9/py`) | the generic `X` on the layered route, its admission and certificate kinds (SC-6), `ve document` on layered documents (SC-8) | ET-4 waits for SC-6 and SC-8 on `main`; it registers PK-1's provider line and makes no other edit to RD-9's files |
| PK-1 (premise packs, owned by the RD-9 composition owner of `Layered.lean`; after `rd-9-int`) | the one assembler of `X` from packs, `reservedPrefixes`, label uniqueness, `transfers_append` | ET-4 waits for PK-1; on `Layered.lean` the providers land AT-2/AT-3a → WG-3 → ET-4 → QT-B2 (X1) |
| AR-10 (the profile-gate table, scope including `Dispatch.lean:417–474`) | one table row per profile, its generic lemma, generated data for Python | ET-4 adds the `events@0` row with its composition proof; ET-7's refusal deletion is serialised with the table, whichever lands second rebases (X3) |
| `weighing` (`design/weighing`, WG-3) | PK-1's assembler | WG-3 lands on `Layered.lean` before ET-4 (X1) |
| English-in-Lean (`english-lean` E2 and later) | the owner of wordings and advice rows | ET-5 adds rows to english-lean's catalogue only; if it lives in `lean/VE/EnglishGrammar/*` then, ET-5 joins the serialised English queue `AT-5 → QT-A6 → ME-11 → QT-B3 → SC-7` in landing order (X9) |
| Document mode (`ve/document.py`, after `lf-16g`) | profile acceptance | landing order AT-3b, SC-1b, QT-A4, ET-5, WG-4, ME-10 (X10) |
| Lean-first waves (`lf-12`, `lf-14a`..`d`, `lf-16*`) | none for the gate (AR-10's generated data replaces `lf-12`'s role here) | ET-5 adds no `ve/profiles.py` row; ET-7 deletes a mirror row only if it still exists; regenerate inventories after rebasing |
| test speed (`ts-B2`, `ts-B3`) | none | regenerate `tools/gate-collection.json` after rebasing; never hand-merge it (`regen_generated.py --resolve`) |
| pilots (`pilot.sh`, `pilot-udhr.sh`, 06:00 and 18:00 UTC) | ET-0, ET-1, ET-6, ET-8, ET-9 change pilot files | run between pilot windows, on the run directory the next pilot copies, and list `changed_units` for the audit |
| research-wave siblings | `attitudes` (hedges on causal claims, "knowingly"), `quantities` (durations, "heavier", comparisons of harm), `act-phrases` (event phrases), the phrase grammar (english-lean's engine and act-phrases) for quantifier scope inside a sentence ("every day before"); `scope` starts at a unit boundary (X7), `math-evidence` (support of causal claims) | this plan names each as a dependency and designs none of them (10); landing preference: ET after WG and before scope's SC-3…SC-7 (X10) |

No batch edits a generated file by hand; each lists its generated files above and regenerates them. New code lives in
new files: `lean/VE/Events/`, `lean/VE/Alternatives/FillWire.lean`, `ve/events.py`, `tests/test_events_*.py`.

## 7. The measure

Per pilot batch: units moved out of UNFORMALISED (by status), their bytes, the audit verdicts of the changed units,
and the check time per document; reported in the run's SUMMARY and `units.json` with `changed_units`. Per product
batch: the theorems of 3 audited under the unchanged allowlist, T1-T13 passing in Lean and through the service, the
seeded bugs recorded. Over the plan: UDHR and constitution bytes moved, against the estimates of research 5.1; the
NORTH-STAR rows 4 and 11 refreshed from the ledgers (their "semantics absent" and "Planned" cells are already out of
date, research 1.3).

## 8. Not claimed, risks, open questions

- **Not claimed**: the truth of any link or day; durations over events; deadline fulfilment; branching time;
  completeness of the premises for every calendar consequence (a consequence that needs counting the days between two
  named dates more than one apart is UNKNOWN); completeness of the checks on documents outside norms 7.1 (B: the
  `fragment` line says when); a refutation outside the calendar completion fragment (UNKNOWN, A); persistence of a
  state without a stated end (F); order within a day (E); any conservativity beyond `events_conservative`'s `oldEnv`
  (X2); dates before 1970 (ET-T3); any byte before its audit.
- **Risk: check time.** `linear` is a disjunction and `transitive` a three-variable premise; both enlarge tableau search
  and finite-model search. The UDHR whole document already fails to load in 815 s (pilot SUMMARY), so ET-6 measures
  per part and stops at its bar. Pruning the order premises is an optional optimisation with its own preservation
  theorem, not a promised fallback (J).
- **Risk: RD-9 slips.** ET-0, ET-1, ET-7, ET-8 and the experiments do not depend on it.
- **Risk: audits reject event reification.** ET-0 tests it on one unit before anything is built.
- **Open: ET-8's refusal question.** The constitution says refusal is "always compatible" with the hard constraints,
  not that it is permitted. With the completion, FOLLOWABLE needs a permission the component does not state; the plan
  records the outcome instead of choosing (D14).
- **Open: same-day order.** Two events on one day cannot be ordered (risk's `Q-clock`); a source that needs it
  ("immediately after", "confirmed before the action") is UNFORMALISED with reason `time-of-day`; same-day facts alone
  never make a point UNDECIDED (E).
- **Open: tagging.** Research 2.2 found inconsistent `missing_feature` tags ("promote" in three features); ET-9's
  sample uses the sentences, not the tags.

## 9. Review checklist (ET-2)

1. Is a day sort with a linear order the right base, given D1's rejection of integers on the chain?
2. Are D4's premises exactly the intended conventions, and is each one universal and function-free?
3. Is the calendar check (2.5, D6) with the completion theorem the right guard against non-calendar refutations: does
   the fragment cover every formula the evidence check reads (the whole assembled `X`, `Fill_T`, the expanded rules
   and definitions, the conclusion), and are T3b and T3c never refuted?
4. Does `events_conservative`'s expansion on `S.Carrier ⊕ ULift Nat` prove what 3.2 says, without Mathlib?
5. Is each wording of 2.7 one reading, and do T9's advice texts say what to write instead?
6. Is D9's "until" reading set complete enough per modality, with E's own day and the inclusive date readings, and
   are the T11 situations distinguishing?
7. Are the link forms (D10) and their two premises acceptable as the only causal content, stated as conventions, and
   are they disjoint from alternatives' and risk's wordings (D11)?
8. Is the D12 gate right as AR-10's row, in particular refusing `alternatives@0` and `data@0` beside `events@0` for
   now?
9. Do 3.4's statements match nd 282-301 and nd 2.5's evidence rule (C), and is deleting the refusal (D13) safe for
   every existing fixture?
10. Are ET-0's and ET-1's bars honest about what the audit must accept?

## 10. Shared pieces

Abstractions this plan thinks several of the seven research-wave topics could share. The cross-plan review may move any
of them.

| Shared piece | Who would use it | Proposal |
|---|---|---|
| **Premise packs on the layered route** | weighing, events-time-causation, attitudes, scales, soft, rights | **PK-1** (X1), owned by the RD-9 composition owner of `lean/VE/NormDefaults/Layered.lean`, after `rd-9-int`: one assembler of `X` from packs (`structure Pack` with `id`, `kind` (`.vocabulary` or `.constraint`), `decls`, `labelled`, `origins`), order `soft, rights, weighing, attitudes, scales, events`, one `reservedPrefixes` list, global freshness and unique labels; each provider proves typing and, on the readings route, `Transfers`; every reported witness satisfies the whole assembled `X`; no global conservativity claim. `events@0` is the `events` pack, last, of kind `.constraint`, counted as a conservative step only through `events_conservative` (over `oldEnv`) and only inside the calendar completion fragment (X2) |
| **Events and states as things with roles** (Davidsonian reification on the two-place chain) | act-phrases (an act phrase with arguments is an event with roles), attitudes (a belief or intention held by someone on a day), quantities (amounts and durations attached to events), scope | `events@0` owns the event and state sorts, their days and their order; other topics add roles to the same sorts rather than new reification schemes. act-phrases' AP-6 route (a) reifies a many-slot act as an event sort of `events@0` and adds its participant roles to that sort; it defines no case or role scheme of its own (X5) |
| **Act-performance predicate** | attitudes, act-phrases (Group A faithfulness), causation | events designs it (ET-D2); not built here (X4) |
| **One calendar and one date grammar** | quantities (W6 durations, ages), events, math-evidence (dated evidence) | `VE.Time.Calendar` and W6's date-literal class; no topic computes dates elsewhere. Dates before 1970 are a W6 trigger (ET-T3) that extends `VE.Time.Calendar`'s range, never a second calendar (X8) |
| **Named open relations with a decider and support** | events (causal links), attitudes (attitude holders), weighing (decisions), math-evidence (evidence support, VEX) | one schema: the W2 open term with `arguments`, `decided_by` and per-unit `support`, plus one residual line format |
| **Source words as reading sets with a distinguishing situation**, and the matching advice rows in authored text | every topic ("until", "should", "likely", "most", "every ... before") | one catalogue of source words, their candidate wordings and their advice texts, owned by english-lean's catalogue; events adds rows only, for "until", "by", "within", "during", "since", "while", "always", "eventually", "whenever", "resulted in", "led to", "caused" (X9) |
| **Exclusive choice: choosers and alternatives** | weighing's WG-E1 and WG-10 (collisions between different acts), act-phrases (act identity) | `alternatives@0` owns exclusivity (`available`, one chooser per action). Weighing's WG-10 consumes a reviewed composition of `alternatives@0` with soft norms and defines no exclusivity relation (X6) |
| **Intended-model checks on witnesses** (a refutation must be realisable by the intended reading: calendar days here) | quantities (integers within declared ranges), events | one pattern: a decidable `embeddable`-style check on every reported situation, plus a proved completion to the intended domain for a stated fragment, with UNKNOWN when either fails and certificates kept |
| **Hedged causal claims** ("can lead to", "could cause", "often") | attitudes and quantities own the hedge; events owns the link | the hedge wraps a link unit; neither topic copies the other's wording |
| **Indexical time** ("now", "currently", "at the moment", "in the future") | attitudes, discourse, events, quantities | the anchor ("the date of this document") is the one indexical day for every plan; other indexicals refer to it, and quantities' QT-0p "at the moment" refers to it once `events@0` lands (X9) |

## Change log

- Draft 1 (2026-10-12): first plan, from the research note of the same date.
- Draft 2 (2026-10-13): the converged Astra + Fable review (REVISE now, BUILD after ET-2's review) and the DRI's
  cross-plan synthesis edits X1 to X10. The day domain is fixed and witnesses need the calendar completion theorem
  over the whole assembled `X` (A, X2); D4's completeness claim replaced by the norms 7.1 report (B); ET-7's evidence
  contract (C); link conventions per effect kind (D); strict precedence (E); persistence never assumed (F); dates
  from 1970 and ET-T3 (G, X8); the gate as AR-10's row, no Python mirror (H, X3); the linearity fixture T2b (I); R1
  narrowed, `data@0` refused with R3 as ET-T4, "until" per modality with E's own day and the inclusive date readings,
  per-role wordings, ET-E1 before ET-5 (R1 to R4); pruning optional with its own theorem (J); X assembly by PK-1 (X1);
  ET-D2 (X4); AP-6 reuses event reification (X5); exclusive choice stays with alternatives (X6); scope inside a
  sentence is the grammar's (X7); source words in english-lean's catalogue and the anchor for every plan (X9); order
  and shared-file queues (X10). ET-2's spec is
  [events-time-causation.md](events-time-causation.md).
