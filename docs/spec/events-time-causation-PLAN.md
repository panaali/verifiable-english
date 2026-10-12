# Events, time, durations and causation (`events@0`, and `alternatives@0` on documents): buildable plan

> Status: plan draft 1 (2026-10-12), branch `design/events-time-causation` from `main` at `49de179e`. Research wave
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
   checked consequence. *Estimates*: UDHR 200 to 318 B, constitution 755 to 1,126 B.
2. **A timeline profile, `events@0`** (ET-2 to ET-6): a day sort counted in whole days; `before` with three generated
   premises; event sorts whose elements happen on at most one day; state sorts that begin and end; named dates whose
   order Lean computes from the proved W6a calendar; an optional "date of this document"; causal links (item 4). All
   premises are universal and function-free and ride the layered route's extra premises `X` (RD-9), so no checker
   changes. Witnesses and countermodels are reported only when a calendar can realise them; otherwise UNKNOWN.
   Plain wordings; "until", "during", "by", "within" in sources become reading sets, and in authored text are
   rejected with explicit rewrites. *Estimate*: UDHR 201 to 548 B on its own.
3. **`alternatives@0` with the completion** (ET-7, ET-8): wire the branch whose semantics `followableU_sound` already
   proves (nd 282-301), so a silent permission is UNDECIDED instead of allowed by a modeling choice (Asimov, and the
   ET-1 component).
4. **Causal links between events as named open relations** (ET-9): "<event> contributed to <event>", "<event> was
   necessary for <event>", each with a decider and support, never decided by the checker; two universal premises
   (an effect never happens before its cause; a necessary condition contributes). *Estimate*: UDHR 127 B; constitution
   600 to 1,500 B of a 6,059 B upper bound, measured by ET-9's bar.

Integer durations over variables, deadline obligations, multi-step choices and actual causation are **experiments and
triggers** (ET-E1 to ET-E3, ET-T1, ET-T2), each with a pre-registered bar.

**The first batch that moves a pilot number** is ET-0 (UDHR u042, 2 to 3 h, no product code); ET-1 (constitution,
3 h, no product code) is independent and may run beside it.

## 1. Decisions

| # | Decision | Why | Rejected |
|---|---|---|---|
| D1 | Time on the chain is a **day sort** of whole civil days with a declared `before`, not integers | the chain is first-order with two-place atoms and no arithmetic (research 1.4); W6a already counts civil days and excludes clock time (W6 6.2); days are what the pilot sentences need | integer days on the chain (candidate B, research 4.2): a norms × order checker for a need measured at about zero; dense time, clock time |
| D2 | **Events and states are things** with two-place roles: an event sort's `on` predicate ("{0} happens on {1}"), a state sort's `begins` and `ends` ("{0} begins on {1}", "{0} ends on {1}"); names are the author's, argument orders and verbalisations fixed by the block (as alt 1.1) | Davidson and Parsons (research 3.1); fits the two-place chain; it is what the UDHR translators already do without days (research 1.4) | a time argument on every predicate (three places: `nary@0`, which the chain lacks) |
| D3 | The profile is a **premise pack**: its block regenerates closed base premises `Ev_V` that are appended to the layered route's extra premises `X` (`VE.NormDefaults.Wire.premisesX`, `EntailsX`, `acceptanceX`, `modelCheckX_sound`). No new checker, no new route, no new service mode | RD-9 proves the checkers sound for any typed `X`; the same hook carries soft's and weighing's premises | a new route `ve_events_route` (a copy of the layered dispatch); inlining defined words into guards (unneeded: every wording elaborates to base formulas over the roles) |
| D4 | The premises are **universal and function-free**: `before` is irreflexive, transitive and linear; each event on at most one day; a state never ends before it begins; consecutive named dates ordered, and no day between two named dates one day apart; links forward in time; necessary implies contributed | the documents stay in the fragment where the existing checks are complete; finite models exist for every premise set (`eventsPremises_satisfiable`) | "every day has a next day" (forces infinite models); existence of an event's day as a premise (validated on situations instead, as alt 4.2 E1-E3) |
| D5 | **Named dates** are constants of the day sort generated from the block's ISO list (`date__YYYY_MM_DD`, reserved prefix), rendered in W6's long form ("10 December 1948"); Lean orders them with `VE.Time.Calendar` (`Civil.num`, `before_iff`). At most 64 per document | one calendar, one date grammar (W6), no Python computation of dates; 64 keeps the generated premises under `MAX_NODES` | a second calendar; Python date order; all-pairs order facts (quadratic; transitivity derives them) |
| D6 | A witness or countermodel is reported only when it is **calendar-embeddable** (its days can be numbered as civil days, keeping the order and the named dates); otherwise the answer is UNKNOWN with `NotCalendar` | the premises admit structures no calendar realises (a day squeezed between two consecutive dates); a refutation there would be about no real situation | dropping the check (wrong refutations); adding counting premises for every gap (expensive; the adjacency premise covers the one-day gap) |
| D7 | Certificates are sound for every structure satisfying the premises, hence for every **calendar reading** (`events_certificate_calendar`) | the intended reading is the calendar; it satisfies the premises (`calendar_sat`) | — |
| D8 | **Reader-facing English has no temporal operators**: no "until", "always", "eventually", "while", "by" (deadline), "within" (window), "since" in VE text. Quantification over days is written out ("on each day", "there is a day such that", "no later than that day"). In a **source**, each of those words becomes a reading set with a distinguishing situation; in **authored** text it is rejected with the explicit rewrites | one reading per sentence; readers misread LTL (research 3.3); "until" alone has at least two readings (silent after the end, or ending), and "by 10 December" two (before, or no later than) | fixed FRET-style meanings for "until" and "within" |
| D9 | "until E" reads as a reading set {R1: on every day before E happens (and the text is silent after); R2: R1 and on no day from the day E happens}. Under `norm-defaults@0`, R1's silence is UNDECIDED, so the distinguishing situation is "E happens on day 5; day 7": R1 UNDECIDED, R2 SETTLED no | the completion already gives "the text does not say"; no new machinery | a single cessation reading |
| D10 | **Causal links** are base predicates between event or state sorts, declared in the block with a form (`contributed`: "{0} contributed to {1}"; `necessary`: "{0} was necessary for {1}") and a decider; they are open: the checker never decides a link, lists every stated link in the residual with its support and decider, and adds only `link_forward` and `link_weaker` | VISION converged rule 8 (no unsupported causal assumptions certified); Lewis: dependence suffices for causation; no backward causation for ordinary events | deciding causation (structural models are research, ET-E3); reusing `leads to` outside a declared decision model |
| D11 | The link wordings are disjoint from `alternatives@0`'s and `risk@0`'s fixed wordings (`leads to`, `allows ... to happen`, `prevents`, `causes`, `might lead to`, `cannot lead to`); "resulted in", "led to", "caused", "brought about" in a source become a reading set over the two link forms (and `leads to` where a decision model is declared) | one owner per wording; alternatives already rejects "results in" and "brings about" with a rewrite to `leads to` (alt 2.2), which stays | a third causal vocabulary |
| D12 | `events@0` requires `relational-fol@0`, `norms@0` and `norm-defaults@0` (the layered route that carries `X`; a predicate may still take the `deny` or `allow` default), with or without `soft-norms@0`, `rights@0` and `readings@1`; it is refused with `order@0`, `time@0`, `closure@0`, `nary@0`, `alternatives@0`, `risk@0`, `reports@0`, `speech-acts@0` (`UnsupportedProfile: events@0 with <p>`). Documents without norms are out of the first build | the hook is RD-9's layered `X`; each refused pair is a later design batch with its own trigger | a frozen-route Background slot now |
| D13 | **Alternatives with the completion** (ET-7) wires the branch `fill (inlineTree A)` that `followableU_sound` already proves, in a new file beside the alternatives wire; the refusal `alternatives@0 with norm-defaults@0 is not implemented` is deleted, not kept as a fallback | nd 282-301 specified it; `lean/NORMDEFAULTS.md` lists it as still open; the Asimov case waits for it | a Python-side classification of silent permissions |
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
(2.3) and appends it to `X` on whichever branch of the layered route checks the list. Everything the route answers
(elaborate, conflict, status, report, certificate, admission, readings verdicts) is unchanged in kind; certificates
bind `Ev_V` by meaning id like every other regenerated premise.

### 2.2 The block (wire form, identity-bound like `regulated`)

```json
"events": {
  "day": "day", "before": "before",
  "events": [{"sort": "act", "on": "committed_on"}, {"sort": "conviction", "on": "convicted_on"}],
  "states": [{"sort": "marriage", "begins": "marriage_begins", "ends": "marriage_ends"}],
  "dates": ["1948-12-10"],
  "anchor": "2026-10-12",
  "links": [{"predicate": "contributed_to", "form": "contributed", "decided_by": "the drafters"}]
}
```

The values are an example (the anchor is the date the document gives for itself). Unknown fields are rejected.
`dates` are ISO strings parsed by `VE.Time.parseIso` and admitted only when `Civil.Valid`
(1970-01-01 to 9999-12-31, W6 6.1; earlier dates are `DateRange`, as in W6). `anchor`, when present, is a valid ISO
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
one_day:<E>        ∀x t u. on_E(x, t) ∧ on_E(x, u) → t = u                     each event sort E
one_begin:<S>      ∀x t u. begins_S(x, t) ∧ begins_S(x, u) → t = u             each state sort S
one_end:<S>        ∀x t u. ends_S(x, t) ∧ ends_S(x, u) → t = u                 each state sort S
not_before_begin:<S> ∀x t u. begins_S(x, t) ∧ ends_S(x, u) → ¬ before(u, t)   each state sort S
date:<D>:<D'>      before(c_D, c_D')                                            consecutive named dates, D.num < D'.num
adjacent:<D>:<D'>  ∀t. ¬ (before(c_D, t) ∧ before(t, c_D'))                     consecutive named dates with D'.num = D.num + 1
link_forward:<L>   ∀x y t u. L(x, y) ∧ start(x, t) ∧ start(y, u) → ¬ before(u, t)   each link; start = on (event) or begins (state)
link_weaker:<N>:<C> ∀x y. N(x, y) → C(x, y)                                     a `necessary` link N and a `contributed` link C on the same sort pair
```

All are closed, universal and function-free. Existence facts are **validated on situations, never assumed** (as alt
4.2): a situation in which a stated event has no day, or a state no beginning, is accepted, and the report says the
fact is missing where a wording needed it.

### 2.4 Named dates and the anchor

The decoder sorts the named dates by `Civil.num`, removes none silently (`DuplicateDeclaration: date <iso>`), and
generates one constant `date__YYYY_MM_DD` of the day sort per date with the verbalisation of W6's long form. Only
consecutive pairs get a `date` premise; transitivity entails every other pair (`datesOrder_iff`). No declared name
may start with `date__` (`EventsReserved: <name>`). The anchor is a named date; "in the future" in a source is
"on some day after the date of this document".

### 2.5 The calendar check (`embeddable`)

On every finite situation the route would report (a CONFLICT witness, a countermodel, a NONE or SOME model of
readings, a scenario), Lean checks, after the existing checks:

1. `before` restricted to the day domain is a strict linear order;
2. each named date denotes a day, in increasing `Civil.num` order;
3. sorting the days by `before`, the number of unnamed days strictly between two consecutive named dates `D < D'`
   is at most `D'.num - D.num - 1`; before the first named date at most `D.num`; after the last at most
   `dateMax - D.num`; with no named date, at most `dateMax + 1` days.

If the check fails, the result is UNKNOWN with `NotCalendar: <first failing condition>`, never a refutation.
`embeddable_sound` (3.2) gives the numbering.

### 2.6 Causal links

A link is a base predicate between two event or state sorts, declared in the block with a form and a decider, and
listed as a W2 open term (document.md) with the same decider. The route never decides a link: a link atom is true in
a situation only if the situation says so, and certificates use links only as the author states them. The report
gains `causal_links`: each link predicate with its decider, and each unit that states or denies a link with its
support. The two premises `link_forward` and `link_weaker` are the only causal content the checker adds.

### 2.7 English (one reading each; rejected as today when `events@0` is off)

Role and derived wordings (registered with `profiles=("events@0",)` in the catalogue that owns wordings when the
batch runs, 6):

| Wording | The one reading (the IDE's paraphrase) | Formal effect |
|---|---|---|
| `<event> happens on <day>` | the day the event happens | `on_E(x, t)` |
| `<state> begins on <day>` / `<state> ends on <day>` | its first day / its last day (the state is still in progress on it) | `begins_S`, `ends_S` |
| `<day> is before <day>` | strictly earlier | `before(t, u)` |
| `<day> is after <day>` | strictly later | `before(u, t)` |
| `<day> is no later than <day>` | earlier or the same day | `before(t, u) ∨ t = u` |
| `<day> is on or after <day>` | the same day or later | `before(u, t) ∨ t = u` |
| `<event> happens before <day>` / `... no later than <day>` / `... after <day>` / `... on or after <day>` | the event happens, on a day so placed | `∃u. on_E(x, u) ∧ …` |
| `<event> happens before <event>` / `... no later than ...` / `... after ...` / `... on the same day as ...` | both happen, on days so placed | `∃t u. on_E(x, t) ∧ on_F(y, u) ∧ …` |
| `<state> is in progress on <day>` | from the day it begins through the day it ends, both included; with no end day, every day from its beginning | `∃b. begins_S(x, b) ∧ ¬before(t, b) ∧ ¬∃e. ends_S(x, e) ∧ before(e, t)` |
| `<cause> contributed to <effect>` | an open causal link, decided by its decider | `L(x, y)` (form `contributed`) |
| `<cause> was necessary for <effect>` | an open but-for link: without the cause the effect would not have happened, decided by its decider | `N(x, y)` (form `necessary`) |
| named dates: `10 December 1948`, `1948-12-10`, `the date of this document` | the named day | `c_D` |

Days are quantified with the existing forms ("each day", "there is a day such that", "that day"), so no new binder is
added. A regulated predicate may take a day argument ("{0} be presumed innocent on {1}"), which keeps it two-place.
The legend generated from the block says, in plain English: "Times are counted in whole days: two things on the same
day happen on the same day, and neither is before the other." and "A state is in progress from the day it begins
through the day it ends." "Ends on" is inclusive because that is the common English reading ("the offer ends on
Friday") and the one the eligibility answer key needs (4.3, R1); a source whose end day is exclusive becomes a reading
set.

Rejected in authored text, each with its rewrites (advice rows in the catalogue's advice table, as the
`alternatives-*` families):

| Pattern | Advice |
|---|---|
| `until <...>` | "Write the rule for each day with the guard 'if it is not the case that <event> happens no later than that day'; the text then says nothing about later days. If it means the rule stops, add a second rule for the days on which <event> happens no later than that day." |
| `by <day or event>` (as a deadline) | "Write 'before <day>' or 'no later than <day>'." |
| `within <n> days` | "Durations over events are not available here; name the dates, or use the quantity wordings in a quantity document." |
| `during <state>` | "Write the rule for each day with the guard '<state> is in progress on that day'." |
| `since <...>`, `while <...>`, `always`, `eventually`, `whenever` | "Write the days explicitly: 'on each day, if ...', 'there is a day such that ...'." |
| `resulted in`, `led to`, `caused` between events | "Write '<cause> contributed to <effect>' or '<cause> was necessary for <effect>'; in a decision model write 'leads to'." |

In translation, each of these source words opens a reading set whose candidates are the explicit wordings, with the
distinguishing situation shown (D9).

### 2.8 Identity and binding

The block is in the canonical environment bytes (`environment_id` changes only for environments that carry it). The
regenerated date constants are part of the regenerated environment, as `unsaid__p` declarations are (nd, NORMDEFAULTS
"`E‴_base` on the wire"); Python builds the same bytes for certificate bindings by relaying Lean's
`baseEnvironmentJson`, never by computing them. `Ev_V` enters `premisesX` after the other packs' premises in a fixed
order (10, "premise packs"), so every certificate binds it by meaning id. A replay against a changed block, a changed
date list or a changed link decider is stale.

### 2.9 Well-formedness, in order (`WellFormedEvents`)

1. The profile list satisfies D12 (`UnsupportedProfile: events@0 with <p>`; `UnsupportedProfile: events@0 requires
   norm-defaults@0`).
2. The block decodes with no unknown field (`InvalidInput: events.<field>`).
3. The day sort is declared; `before` is a base predicate `(day, day)` with verbalisation `{0} is before {1}`
   (`EventsSort: before`, `EventsVerbalisation: before`), not regulated, not defined (`EventsRegulated: <p>`).
4. Each event sort is declared, is not the day sort, appears once among event and state sorts
   (`DuplicateDeclaration: event sort <s>`); its role predicate has sorts `(s, day)` and the fixed verbalisation.
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
witness situation and a filling; scenario evaluation in which each alternative is clear, not clear, or "undecided:
the text does not say whether it may be performed"; the untrusted diagnosis gains `UNSETTLED(<alternatives>)` before
NONE-PERMITTED (nd 286-290). A document without `unspecified` decodes exactly as today
(`decodeAltSourceU_conservative`). `risk@0` with the completion is not in this plan (nd 293-298; its own batch).

### 2.11 One owner, and what is deleted or not duplicated

- **Calendar**: `VE.Time.Calendar` only (`parseIso`, `Civil.Valid`, `Civil.num`, `before_iff`). The events decoder
  calls it; nothing in Python or Rust computes a date order or a day number for this profile.
- **Date literals in English**: W6's literal grammar (ISO and long form), wherever the catalogue holds it; the events
  surface reuses that class.
- **Outcome tables and the four alternatives words**: `VE.Alternatives` only. `events@0` adds no causal word that
  overlaps (D11); the catalogue's disjointness check covers the link wordings.
- **The W2 `causal` kind**: unchanged (`ve/admission.py` `RELATIONS`, `lean/VE/Route/Admission.lean`); links are
  content, the kind stays a label for causal text that is not formalised.
- **The profile gate**: `lean/VE/Compose/Dispatch.lean` owns it. `ve/profiles.py` still mirrors the gate on `main`;
  ET-5 adds the same rows there only if the Lean-first wave that removes the mirror (`lf-12`, "environments/models/
  profile gate") has not landed, and the batch records the duplicate in its report. Never a third copy.
- **X assembly**: one function shared with soft and weighing (10); `events@0` adds one line to it, not a copy of the
  layered dispatch.
- **Deleted by ET-7**: the refusal `alternatives@0 with norm-defaults@0 is not implemented` (Lean
  `VE.Compose.Dispatch`, Python mirror if present) and the alternatives route's `UnsupportedProfile: Unsupported
  profile norm-defaults@0`; the test that asserts both refusals is rewritten to assert the branch.
- **Pilot workarounds** (no product code): one-occurrence sorts with no day, and days baked into predicate names, are
  retired for every unit ET-6 restates.

### 2.12 What stays open (the residual, never certified)

The truth of every link and of every day an event is said to happen on (with their support); the completeness of
stated events and alternatives; whether "periodic", "constantly", "progressive", "of full age" and the like are met
(open terms); clock time within a day (two things on the same day are on the same day; risk's `Q-clock`);
durations over events; deadline fulfilment; branching futures.

## 3. Lean statements

Files (new): `lean/VE/Events/{Decl,Premises,Calendar,Conservative,Wire,Chain}.lean`, `lean/EVENTS.md`; ET-7:
`lean/VE/Alternatives/FillWire.lean`. Names have prefix `VE.Events.` (ET-7: `VE.Alternatives.`); no theorem name
contains a prime, and no name or comment contains a word `lean/audit.py` rejects. Without Mathlib
(`lean/lakefile.toml` has no `require`), order lemmas are proved locally.

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
def oneDayF (V : EventsEnv) (sort role : String) : VE.Formula :=
  .all sort (.all V.day (.all V.day
    (.implies (.and (.binary role (.var 2) (.var 1)) (.binary role (.var 2) (.var 0))) (.eq (.var 1) (.var 0)))))
def notBeforeBeginF (V : EventsEnv) (s : StateSort) : VE.Formula :=
  .all s.sort (.all V.day (.all V.day
    (.implies (.and (.binary s.begins (.var 2) (.var 1)) (.binary s.ends (.var 2) (.var 0)))
              (.not (.binary V.before (.var 0) (.var 1))))))
def dateFacts (V : EventsEnv) : List VE.Formula
  -- for consecutive D, D' in V.dates: .binary V.before (.const (dateName D)) (.const (dateName D'))
def adjacentFacts (V : EventsEnv) : List VE.Formula
  -- for consecutive D, D' with D'.num = D.num + 1:
  -- .all V.day (.not (.and (.binary V.before (.const (dateName D)) (.var 0)) (.binary V.before (.var 0) (.const (dateName D')))))
def linkForwardF (V : EventsEnv) (l : Link) : VE.Formula      -- 2.3 link_forward, start roles from the link's sorts
def linkWeakerF (V : EventsEnv) (n c : Link) : VE.Formula     -- 2.3 link_weaker

def orderPremises (V : EventsEnv) : List VE.Formula := [irreflexiveF V, transitiveF V, linearF V]
def conventionPremises (V : EventsEnv) : List VE.Formula
  -- one_day per event sort, one_begin/one_end/not_before_begin per state sort, link_forward per link,
  -- link_weaker per (necessary, contributed) pair on one sort pair, in declaration order
def eventsPremises (V : EventsEnv) : List VE.Formula :=
  orderPremises V ++ dateFacts V ++ adjacentFacts V ++ conventionPremises V

/-- A calendar reading of S: its days are numbered as civil days, `before` is `<`, named dates denote their days. -/
structure CalendarReading (V : EventsEnv) (S : VE.Structure.{u}) where
  num    : S.Carrier → Nat
  inj    : ∀ x y, S.domain V.day x → S.domain V.day y → num x = num y → x = y
  range  : ∀ x, S.domain V.day x → num x ≤ dateMax
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

/-- A calendar-embeddable finite situation has a calendar reading. -/
theorem embeddable_sound {α} [DecidableEq α] (E : VE.Environment) (V : EventsEnv) (h : WellFormedEvents E V = true)
    (M : VE.FiniteModel α) (valid : M.Valid (regenEnv E V)) (hp : Sat M.asStructure (eventsPremises V))
    (he : embeddable V M = true) :
    Nonempty (CalendarReading V M.asStructure)

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
`eventsX` is the pack's contribution to `X`. The layered decoder of RD-9 (the function that builds `U` and `X` for a
case, named as merged) calls the shared X assembly (10, "premise packs"), which appends `eventsX` when the block is
present. On `rd-9/integrate` the names below exist: `VE.NormDefaults.EntailsX`, `VE.NormDefaults.acceptanceX`,
`VE.NormDefaults.modelCheckX`, `VE.NormDefaults.modelCheckX_sound`, `VE.NormDefaults.Wire.premisesX`,
`VE.NormDefaults.Wire.BaseAdmissibleX`, `VE.NormDefaults.FiniteFill`, `VE.NormDefaults.finFill`,
`VE.NormDefaults.withFill`.

```lean
namespace VE.Events
open VE.NormDefaults (UDoc fill WellFormedU EntailsX acceptanceX modelCheckX modelCheckX_sound FiniteFill)

def decodeEvents (environment : Lean.Json) : Except String (Option (EventsEnv × VE.Environment))
  -- none when the block is absent; otherwise the decoded block and the regenerated environment
def eventsX (V : EventsEnv) : List VE.Formula := eventsPremises V

/-- Absent block, nothing changes: the assembled X is the other packs' X. -/
theorem eventsX_absent (environment : Lean.Json) (h : decodeEvents environment = .ok none) (X : List VE.Formula) :
    assembleX environment X = X                 -- `assembleX`: the shared assembly of 10, named as built

/-- ET-4's certified entailment, on the layered route: an accepted certificate with the pack's premises is an
    `EntailsX` with them; and it holds in every calendar reading. -/
theorem events_certificate_calendar (U : UDoc) (h : WellFormedU U = true) (V : EventsEnv) (X Γ : List VE.Formula)
    (φ : VE.Formula) (hX : ∀ a ∈ X ++ eventsX V, a.WellFormed (VE.Norms.envAt (fill U) 0) [])
    (cert : VE.Tableau.Certificate)
    (hv : VE.Tableau.checkCertificate (VE.Norms.envAt (fill U) (VE.Norms.size (fill U)))
            (VE.NormDefaults.Wire.premisesX U (X ++ eventsX V) Γ) φ cert = true) :
    EntailsX U (X ++ eventsX V) Γ φ

/-- A countermodel or witness is reported as a refutation only when it is calendar-embeddable; then it is a
    calendar situation. (`modelCheckX_sound` gives the rest.) -/
theorem events_countermodel_calendar (U : UDoc) (h : WellFormedU U = true) (V : EventsEnv) (X : List VE.Formula)
    (M : VE.FiniteModel VE.Bridge.Entity) (valid : M.Valid (VE.Norms.envAt U.D 0))
    (F : FiniteFill U VE.Bridge.Entity) (Γ : List VE.Formula) (φ : VE.Formula)
    (hm : (modelCheckX U (X ++ eventsX V) M F Γ φ).1 = true) (he : embeddable V M = true)
    (hE : WellFormedEvents (VE.Norms.envAt U.D 0) V = true) :
    Nonempty (CalendarReading V M.asStructure)

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
`M.withFill F` is `VE.FiniteModel.withFill`. The scenario answer's three values per alternative come from
norm-defaults' Kleene evaluation (`kleene_sound`) on the filled tree; nothing new is claimed for the diagnosis.

## 4. Fixtures

Definitions first, expectations after, so a reviewer derives each expectation before reading it (as alt 8).

### 4.1 Synthetic (`#guard` in Lean, the same cases through the service in Python)

| # | Definition | Expected |
|---|---|---|
| T1 | block with day sort `day`, `before`; no events; dates 1948-12-10, 2026-10-12 | 3 order premises, 1 date premise, 0 adjacency; `datesOrder_iff` true for (1948, 2026) and false for (2026, 1948) |
| T2 | dates 2026-10-12, 2026-10-13 | 1 date and 1 adjacency premise; "there is a day such that that day is after 12 October 2026 and that day is before 13 October 2026" refuted by certificate |
| T3 | dates 2026-10-12, 2026-10-14; a model with three unnamed days strictly between them | `NotCalendar: 3 days between 2026-10-12 and 2026-10-14, at most 1` and UNKNOWN; with one unnamed day: accepted |
| T4 | event sort `act`, `committed_on`; a situation with one act on two days | `InvalidModel("events", "premise events:one_day:act fails")` |
| T5 | state sort `marriage`; a situation in which a marriage ends before it begins | `InvalidModel("events", "premise events:not_before_begin:marriage fails")` |
| T6 | link `contributed_to` (event → event), a situation in which the effect happens before the cause | `InvalidModel("events", "premise events:link_forward:contributed_to fails")` |
| T7 | a document with no day vocabulary in any rule or premise, with and without the block | same statuses and verdicts; certificates differ only in their bound premise list (`events_conservative`) |
| T8 | identity: every existing fixture without the block | `environment_id` and every hash unchanged; with the block, `environment_id` changes |
| T9 | each wording of 2.7 | one derivation each; "until", "by", "within", "during", "since", "resulted in" rejected with the advice of 2.7 |
| T10 | 65 named dates; a date 1969-12-31; a declared constant `date__x` | `ResourceLimit: events dates`; `DateRange: 1969-12-31`; `EventsReserved: date__x` |
| T11 | `until`, D9: rule R1 "Every person may be presumed innocent on each day, if it is not the case that there is a conviction such that that conviction is of that person and that conviction happens no later than that day." with `presumed_innocent_permitted` unspecified; R2 adds the prohibition for days on or after a conviction; situation: a conviction on 5 January 2027, day 7 January 2027 | R1: UNDECIDED (the text does not say); R2: SETTLED no; the pair is the reading set's distinguishing situation |
| T12 | ET-7: nd fixture u10 (pull forbidden, push with no rule, `permitted` unspecified) | DILEMMA, diagnosis `UNSETTLED(push)`; with "Every action may be performed, if that action is push." FOLLOWABLE |

### 4.2 From the pilots (real units, run `20261012T1800Z`)

| # | Unit | VE text (sketch; the batch writes the final text) | Expected |
|---|---|---|---|
| P1 (ET-0) | U u042, 200 B | sorts `finding of guilt` (one finding that one person is guilty of a penal offence), `act` (one act or omission), `day`; regulated `finding_of_guilt_permitted(finding)` with act "{0} take place", `default: unspecified`; rule: "No finding of guilt may take place, if there is an act such that that finding of guilt is on account of that act and there is a day such that that act is committed on that day and it is not the case that that act constitutes a penal offence under national or international law on that day." The bearer stays as in u098 (unassigned) | loads and checks on today's chain; conflict-free with its part; the audit samples it FAITHFUL (bar) |
| P2 (ET-0) | U u043, 118 B | as P1 with an `imposition` sort and "a heavier penalty than the penalty that was applicable ... on that day": `heavier_than(penalty, penalty)` a named open comparison; "applicable to that offence on that day" needs a third place, so it is reified as an `applicability` state or the unit stays UNFORMALISED | recorded either way; claimed only if the audit accepts the reification |
| P3 (ET-1) | C u0172.s01 (119 B), u0172.s02 (213 B) | component on the alternatives route: chooser `decision` (one decision of one instance of Claude about one request), action `response`, harm `harm`; `inaction` declared; the ten hard constraints as prohibitions on responses with the pilot's open terms and the shared "knowingly or quite likely" condition; premises Γ: "For every decision there is a response such that that response is available to that decision and that response is inaction." and "No response that is inaction provides serious uplift to ... [each category]" (support: testimony, cites u0172.s02); legend: "This document holds only the hard constraints; 'may be given' means no hard constraint forbids it." | FOLLOWABLE, `conditional_on` both premises; without the first premise UNKNOWN (the existence fact is validated, not assumed: alt fixture u) |
| P4 (ET-1) | C u0171.s03, 276 B | in the same component: "Every response that clearly and substantially undermines Anthropic's ability to oversee and correct advanced AI models, if Claude knows or thinks it quite likely that it does, may not be given, even if there is a harm such that that response prevents that harm." as an entailed assertion; scenario: responses `undermine`, `refuse` (inaction), `answer`; harm `attack`; rows `refuse` and `answer` lead to `attack`, `undermine` does not | entailment certified; scenario: `undermine` prevents `attack` and is forbidden; "decision D has a clear action: refuse, answer" |
| P5 (ET-1) | C u0171.s01 (147 B), u0171.s02 (159 B), u0172.s03 (212 B) | the component's report: no obligation, so nothing requires prevention ("unmapped obligations: none"); u0172.s03's "refusal is not necessarily compatible with the other priorities" points outside the component | OPEN or LABELLED as the audit decides; claimed only then |
| P6 (ET-6) | U u041, 201 B | reading set {R1, R2} of T11 over `presumed_innocent_permitted(person, day)`; the trial as an event with open conditions ("according to law", "public", "all the guarantees necessary for his defence") | READINGS with the T11 distinguishing situation |
| P7 (ET-6) | U u058, 91 B | state sort `marriage` with `begins`, `ends`; "on each day on which that marriage is in progress" and "on the day that marriage ends"; "equal rights" kept as in the rights translation | partly: the phases expressed; "equal rights" stays with `rights`/`quantities`; claimed only if the audit accepts the whole unit |
| P8 (ET-6) | U u042, u043 restated | P1 and P2 with `committed_on` as the `act` sort's `on` role (one day per act) | same verdicts; fidelity: "the time when it was committed" is now one day |
| P9 (ET-9) | U u004, 127 B | events `disregard of human rights` (a state), `barbarous act` (event kind as a sort), `outrage of the conscience of mankind`; links "contributed to", decided by "the drafters"; "barbarous" open | OPEN; `causal_links` lists both links with support testimony |
| P10 (ET-6, probe) | C u0204.s03, 316 B | "Claude should ideally raise concerns before undertaking a task": events `raising of concerns`, `undertaking`; "happens before"; the "should ideally" force and the harm comparison stay with soft norms and `quantities` | probe only; claimed only with those features |
| P11 (ET-6, probe) | C u0022.s01, 67 B | anchor date; "there is a day such that that day is after the date of this document and this document changes on that day", hedged "likely" | the time part admitted; the unit is claimed only with `attitudes`' hedge |

### 4.3 Use-case regressions

| # | Case | Expected |
|---|---|---|
| R1 | eligibility rule R5 ("throughout the qualifying week") restated with a `stay` state (`begins`, `ends`) and "on each day from 21 September 2026 through 27 September 2026 that stay is in progress" | C25 and C27 give £200, C26 £100, as the answer key; a stay with no end date is in progress on every later day |
| R2 | asimov-laws with `permitted` switched to `unspecified` (ET-8) | the README's measured bound becomes the computed result: clear actions only where a rule permits; diagnoses `UNSETTLED(...)` where a silent permission is all that is left |
| R3 | agent-policy "confirmed before the action": events `confirmation`, `action`; "that confirmation happens no later than that action" | expressible; the policy unit moves from OPEN-with-gap to the rule (claimed by that use case's own run) |

## 5. Batches

Each batch is 2 to 6 hours. "Pilot" batches change pilot files under `manage-agents/pilots/` only. Every batch that
changes product code plants a seeded bug per behaviour claimed, in each language changed, and records the failing test
(CLAUDE.md). Generated files are regenerated with `uv run python tools/regen_generated.py --write`, never edited.

### ET-0. UDHR u042 with an event sort and a day sort (pilot, 2-3 h, no product code)

Smallest batch that moves a pilot number. Rewrite u042 (P1) in its part document; attempt u043 (P2); run the part's
`ve document check`; record the unit in `units.json` with the new status. **Pre-registered bar**: u042 loads and checks,
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
constitution); 1,126 B with P5. Shared files: none in the repository.

### ET-2. Statement spec and stub elaboration (planner, 4-5 h)

`docs/spec/events.md` (item 1): sections 2 and 3 of this plan as reviewed statements, diagnostics, wire, fixtures with
expectations separated; every Lean block of 3 elaborated in an untracked stub against `main` and `rd-9/integrate` (as
RD-9 SC-0), names fixed (`assembleX`, the layered decoder, `fillValid`). Gate: the statement review the DRI
assigns (two frontier reviewers), each reviewer deriving T1-T12 and P1-P11 before reading the expectations. Shared
files: none. *Estimate*: 0 pilot bytes (specification).

### ET-3. Lean: block, premises, calendar, conservativity (Lean, 5-6 h)

`lean/VE/Events/{Decl,Premises,Calendar,Conservative}.lean` and `lean/EVENTS.md`: 3.1 and 3.2, T1-T8 and T10 as
`#guard`. Seeded bugs: drop `linearF` from `orderPremises` (T2's certificate fails); generate all-pairs date facts in
reverse order (T1 fails); skip the gap count in `embeddable` (T3 fails). Shared files (append-only): `lean/VE.lean`
(imports), `lean/VE/Audit.lean` (audit entries). Generated: `lean/declarations.txt`, `lean/statements.txt`,
`lean/predicates.txt`, `lean/axioms.txt` and anything `regen_generated.py --list` names for new Lean sources.
Conflicts: new directory only; the two shared files take one appended block each. *Estimate*: 0 pilot bytes
(infrastructure).

### ET-4. Lean: wire, the chain hook, report fields (Lean, 5-6 h; after RD-9 SC-6 and SC-8 merge)

`lean/VE/Events/{Wire,Chain}.lean`: `decodeEvents`, `regenEnv` on the wire, `eventsX`, the line in the shared X
assembly (10), `embeddable` applied to every reported situation, the report fields `named_dates`, `events_premises`
(labels) and `causal_links`; 3.3's theorems; the response shapes for the new fields in
`lean/ResponseShape/Schemas/` with encoder theorems in `lean/ResponseShape/Encoders/` (listed in
`lean/ResponseShape/Audit.lean`). Seeded bugs: append `eventsX` before soft's premises (binding fixture fails); report
a non-embeddable countermodel (T3 through the service fails). Shared files: the X assembly file (one line), the files
RD-9 owns for the layered dispatch only through that line, `lean/VE/Compose/Dispatch.lean` (the D12 gate rows,
appended with their proofs), `lean/VE/Audit.lean`, `lean/ResponseShape/Audit.lean`. Generated: the service schemas
(`ve/backends/lean_service_schema/*.json`, `tools/response_schemas.py --write` through `regen_generated.py`),
`lean/checkers.lock`. *Estimate*: 0 pilot bytes (infrastructure).

### ET-5. Python and English: wordings, advice, relay, fuzz (Python, 4-5 h)

The wordings and advice rows of 2.7 in the catalogue that owns them when the batch runs (English-in-Lean's tables if
moved; otherwise the surface registry with `profiles=("events@0",)`); W6's date-literal class reused; block shape in
`ve/environment.py` only if Python still checks environment shape there; the profile row in `ve/profiles.py`
(`REGISTRY`, and the gate mirror only as 2.11 says); `ve/events.py` relays the report fields and binds them to the
request (every named date, label and link the answer names exists in the request; no extra row); T9 and the binding
fixtures; fuzz tests in `tests/test_events_answer.py` mutating genuine answers one and two faults at a time (each
member dropped, emptied, retyped, duplicated, reordered; an index out of range): every mutant `CheckerUnavailable` or
changing nothing shown. Seeded bug: accept a link wording equal to alternatives' `leads to` (the disjointness test
fails). Shared files: `ve/profiles.py`, `ve/document.py` (profile acceptance), `ve/backends/service_schema.py` (only if
`MODES` changes, which D3 avoids), `tools/layer_policy.py` (layers of the new files). Generated:
`tools/gate-collection.json`, `tests/data/route-cases.jsonl` (via `tests/route_case_recorder.py`). *Estimate*: 0
pilot bytes (infrastructure); the use-case regressions R1 and R3 become runnable.

### ET-6. Pilot: dated events and states (pilot, 3-4 h; after ET-5)

UDHR P6, P7, P8 and the constitution probes P10, P11. Measure `ve document check` time per UDHR part before and after
the block. **Bar**: P6 READINGS with the T11 situation shown; u041 FAITHFUL in a targeted audit; check time per part at
most 1.25 times the time without the block (lf-6's target); otherwise record and stop adding the block to that part.
*Estimate*: UDHR 201 to 548 B.

### ET-7. `alternatives@0` with the completion (Lean and Python, 5-6 h; independent of RD-9)

`lean/VE/Alternatives/FillWire.lean`: 3.4; the alternatives runner dispatches lists with `norm-defaults@0` to it; the
scenario's third value; `UNSETTLED` in the untrusted diagnosis. Delete the two refusals (2.11). Python: relay and
display the third value; the test asserting the refusals rewritten. T12 and nd fixture u11's alternatives part.
Seeded bugs: report FOLLOWABLE from a certificate over `backgroundBaseAlt` without `fillPremises` (T12 fails); render
an UNDECIDED alternative as clear (scenario test fails). Shared files: `lean/VE/Alternatives/Run.lean` (dispatch line),
`lean/VE/Compose/Dispatch.lean` (delete one refusal, with its proof), `ve/profiles.py` (delete the mirror row),
`ve/alternatives.py` (relay), `lean/VE/Audit.lean`, the alternatives response shape and its encoder theorem.
Generated: `ve/backends/lean_service_schema/alternatives.json`, `tools/gate-collection.json`, `lean/checkers.lock`.
*Estimate*: 0 pilot bytes; it removes the Asimov case's modeling choice (ET-8).

### ET-8. Pilot: Asimov and the ET-1 component on the completion (pilot, 2-3 h; after ET-7)

R2; the ET-1 component switched from allow to `unspecified` for `may be given`, with the legend sentence removed (the
completion says "the text does not say" instead). **Bar**: Asimov's 13 rules still CHECKED and conflict-free, and the
count of models with a clear action reported. For the constitution component no outcome is pre-judged: refusal is
permitted by no rule, so the result is either FOLLOWABLE resting on a stated permission or DILEMMA
`UNSETTLED(refuse)`; the batch records which, with the targeted audit's view of whether u0172.s02 ("always compatible
with Claude's hard constraints") states a permission. *Estimate*: 0 new bytes; fidelity of the bytes ET-1 claimed.

### ET-9. Causal links (pilot and English, 4 h; after ET-5)

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

### Experiments and triggers

- **ET-E1. Comprehension of the explicit wordings** (planner, 3 h; model calls with Sonnet 5.5 as the human proxy,
  DRI approval needed). 30 items: the wordings of 2.7 and the T11 reading set. **Bar**: at least 90% correct per
  wording, and the two "until" readings told apart in at least 90% of items; a wording below the bar is reworded
  before ET-6 claims it.
- **ET-E2. Need for durations and deadlines** (planner, 3 h, model-free). Count, in both pilots and the use cases with
  answer keys, the sentences needing an offset over an event ("within 30 days after each request") or fulfilment by a
  deadline. **Bar**: 5 or more pilot units, or 2 or more answer-key use cases, start ET-T1; else record and stop.
- **ET-E3. Actual causation** (planner, 5-6 h, model-free). For 20 sampled causal units, write a structural model
  from what the source states only, and evaluate but-for and the three HP definitions by hand. **Bar**: at least 4 of 20
  gain a consequence beyond an open link that a blind audit judges faithful; else causal links stay open relations.
- **ET-T1. Integer days on the chain** (trigger: ET-E2's bar). A design batch for norms × integer days, after numbers2.
- **ET-T2. Multi-step choices** (trigger: a committed document that needs alternatives stage 2; asimov-extended's "which
  order came first" is the candidate). A design batch on causation-PLAN 1.6.

## 6. In-flight work, dependencies and merge conflicts

| In flight (branch) | What this plan needs from it | How a batch avoids conflicts |
|---|---|---|
| RD-9 (`rd-9/lean`, `rd-9/integrate`, `rd-9/py`) | the generic `X` on the layered route, its admission and certificate kinds (SC-6), `ve document` on layered documents (SC-8) | ET-4 waits for SC-6 and SC-8 on `main`; it adds one line to the X assembly and no other edit to RD-9's files |
| `weighing` (`design/weighing`, WG-3) | the same X assembly | whichever lands first creates the assembly (10); the other appends one line |
| English-in-Lean (`english-lean` E2 and later) | the owner of wordings and advice rows | ET-5 writes rows where the catalogue is on the day it starts; never in both places |
| Lean-first waves (`lf-12`, `lf-14a`..`d`, `lf-16*`) | `lf-12` may move the profile gate's Python mirror to a relay | ET-5 and ET-7 edit `ve/profiles.py` only if the mirror still exists; append-only otherwise; regenerate inventories after rebasing |
| test speed (`ts-B2`, `ts-B3`) | none | regenerate `tools/gate-collection.json` after rebasing; never hand-merge it (`regen_generated.py --resolve`) |
| pilots (`pilot.sh`, `pilot-udhr.sh`, 06:00 and 18:00 UTC) | ET-0, ET-1, ET-6, ET-8, ET-9 change pilot files | run between pilot windows, on the run directory the next pilot copies, and list `changed_units` for the audit |
| research-wave siblings | `attitudes` (hedges on causal claims, "knowingly"), `quantities` (durations, "heavier", comparisons of harm), `act-phrases` (event phrases), `scope` (quantifier scope of "every day before"), `math-evidence` (support of causal claims) | this plan names each as a dependency and designs none of them (10) |

No batch edits a generated file by hand; each lists its generated files above and regenerates them. New code lives in
new files: `lean/VE/Events/`, `lean/VE/Alternatives/FillWire.lean`, `ve/events.py`, `tests/test_events_*.py`.

## 7. The measure

Per pilot batch: units moved out of UNFORMALISED (by status), their bytes, the audit verdicts of the changed units,
and the check time per document; reported in the run's SUMMARY and `units.json` with `changed_units`. Per product
batch: the theorems of 3 audited under the unchanged allowlist, T1-T12 passing in Lean and through the service, the
seeded bugs recorded. Over the plan: UDHR and constitution bytes moved, against the estimates of research 5.1; the
NORTH-STAR rows 4 and 11 refreshed from the ledgers (their "semantics absent" and "Planned" cells are already out of
date, research 1.3).

## 8. Not claimed, risks, open questions

- **Not claimed**: the truth of any link or day; durations over events; deadline fulfilment; branching time;
  completeness of the premises for every calendar consequence (a consequence that needs counting the days between two
  named dates more than one apart is UNKNOWN); any byte before its audit.
- **Risk: check time.** `linear` is a disjunction and `transitive` a three-variable premise; both enlarge tableau search
  and finite-model search. The UDHR whole document already fails to load in 815 s (pilot SUMMARY), so ET-6 measures
  per part and stops at its bar.
- **Risk: RD-9 slips.** ET-0, ET-1, ET-7, ET-8 and the experiments do not depend on it.
- **Risk: audits reject event reification.** ET-0 tests it on one unit before anything is built.
- **Open: ET-8's refusal question.** The constitution says refusal is "always compatible" with the hard constraints,
  not that it is permitted. With the completion, FOLLOWABLE needs a permission the component does not state; the plan
  records the outcome instead of choosing (D14).
- **Open: same-day order.** Two events on one day cannot be ordered (risk's `Q-clock`); a source that needs it
  ("immediately after") is UNFORMALISED with reason `time-of-day`.
- **Open: tagging.** Research 2.2 found inconsistent `missing_feature` tags ("promote" in three features); ET-9's
  sample uses the sentences, not the tags.

## 9. Review checklist (ET-2)

1. Is a day sort with a linear order the right base, given D1's rejection of integers on the chain?
2. Are D4's premises exactly the intended conventions, and is each one universal and function-free?
3. Is the calendar check (2.5, D6) the right guard against non-calendar refutations, and is `embeddable_sound` the
   statement it needs?
4. Does `events_conservative`'s expansion on `S.Carrier ⊕ ULift Nat` prove what 3.2 says, without Mathlib?
5. Is each wording of 2.7 one reading, and do T9's advice texts say what to write instead?
6. Is D9's "until" reading set complete enough, and is the T11 situation distinguishing?
7. Are the link forms (D10) and their two premises acceptable as the only causal content, and are they disjoint from
   alternatives' and risk's wordings (D11)?
8. Is the D12 gate right, in particular refusing `alternatives@0` beside `events@0` for now?
9. Do 3.4's statements match nd 282-301, and is deleting the refusal (D13) safe for every existing fixture?
10. Are ET-0's and ET-1's bars honest about what the audit must accept?

## 10. Shared pieces

Abstractions this plan thinks several of the seven research-wave topics could share. The cross-plan review may move any
of them.

| Shared piece | Who would use it | Proposal |
|---|---|---|
| **Premise packs on the layered route**: one assembly of the extra premises `X` from each enabled pack (soft's labelled premises, `weighing@0`, `events@0`, later `alternatives@0`'s slot premises), in a fixed order, each pack proving typing and its own conservativity | weighing, events-time-causation, attitudes (if attitude axioms become premises), quantities (if comparison axioms do) | one Lean function (`assembleX`, in the file that owns RD-9's layered decoder) and one generic theorem: a concatenation of typed packs is typed, and a pack whose premises mention only its own new symbols is conservative (each pack instantiates it) |
| **Events and states as things with roles** (Davidsonian reification on the two-place chain) | act-phrases (an act phrase with arguments is an event with roles), attitudes (a belief or intention held by someone on a day), quantities (amounts and durations attached to events), scope | `events@0` owns the event and state sorts, their days and their order; other topics add roles to the same sorts rather than new reification schemes |
| **One calendar and one date grammar** | quantities (W6 durations, ages), events, math-evidence (dated evidence) | `VE.Time.Calendar` and W6's date-literal class; no topic computes dates elsewhere |
| **Named open relations with a decider and support** | events (causal links), attitudes (attitude holders), weighing (decisions), math-evidence (evidence support, VEX) | one schema: the W2 open term with `arguments`, `decided_by` and per-unit `support`, plus one residual line format |
| **Source words as reading sets with a distinguishing situation**, and the matching advice rows in authored text | every topic ("until", "should", "likely", "most", "every ... before") | one catalogue of source words, their candidate wordings and their advice texts, owned by the English catalogue |
| **Exclusive choice: choosers and alternatives** | weighing's WG-E1 and WG-10 (collisions between different acts), act-phrases (act identity) | `alternatives@0` owns exclusivity (`available`, one chooser per action); weighing reuses it rather than defining exclusive acts again |
| **Intended-model checks on witnesses** (a refutation must be realisable by the intended reading: calendar days here) | quantities (integers within declared ranges), events | one pattern: a decidable `embeddable`-style check on every reported situation, with UNKNOWN when it fails |
| **Hedged causal claims** ("can lead to", "could cause", "often") | attitudes and quantities own the hedge; events owns the link | the hedge wraps a link unit; neither topic copies the other's wording |
| **Indexical time** ("now", "currently", "at the moment", "in the future") | attitudes, discourse, events | the anchor ("the date of this document") is the one indexical day; other indexicals refer to it |

## Change log

- Draft 1 (2026-10-12): first plan, from the research note of the same date.
