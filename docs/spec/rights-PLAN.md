# Rights and claim-rights in VE: plan (`rights@0`)

> Status: planning draft 1 (2026-09-27), North Star rank 2. Inputs: the pinned UDHR
> (`manage-agents/pilots/udhr/source/udhr.md`, SHA-256 `d6495201…d3a`, cited "Art. n") and its pilot `run-20260927T1800Z`
> (116 units; 70 unformalised units blocked by norms/rights; 14 open terms; 5 unelaborated reading inventories; zero
> substantive checked bytes); [norms.md](norms.md) (W1, merged); [soft-norms.md](soft-norms.md) (item-1 spec, unmerged);
> [document.md](document.md) (W2); [VISION.md](../../VISION.md). Nothing here changes a frozen contract, a `norms@0` or
> `soft-norms@0` hash, a W1 theorem or a checker function. Theorems and fixtures below are obligations, not results.

## 0. Problem and stance

W1 writes duties from the bearer's side and rejects "is entitled to" (norms.md 2). The Declaration writes from the
holder's side: "Everyone has the right to X", "No one shall be subjected to X", with the duty-bearer unnamed, the duty's
polarity (do not interfere, or provide) unstated and the deciding standard ("arbitrary", "fair", "degrading") open. The
pilot audit warns against both cheap fixes: an entitlement reduced to a permission, and every "shall" read as a strict
duty on an invented bearer.

Stance: **a right is the holder-side view of duties and permissions; it adds no deontic primitive.** A right block names
a holder and lists Hohfeldian *incident lines*, each an ordinary W1 rule or soft default rule: a **claim** is a duty on a
bearer with the holder in an object slot; a **liberty** is a permission with the holder as subject; an **immunity** is a
prohibition on a bearer's act that would alter the holder's status; a **power** is a liberty over a constitutive act
plus a claim that bearers recognise its result (the static shadow of power/liability; an act changing which norms hold
is stage-3 material). Correlativity is by construction: the holder's claim and the bearer's duty are one rule read from
two ends, so "who owes what to whom here" is a projection of W1's outcome tables. `rights@0` elaborates by `correlate`
into `norms@0` or `soft-norms@0` over the author's vocabulary plus fresh open *limitation* predicates and adds no
background premise, so W1's and the soft route's theorems are **reused unchanged**; only shape checks and projections
are new. The ambiguity the source leaves (bearer, polarity, incident) lives in W2 reading sets, **shared
document-wide** so per-choice checking stays inside W2's 64-choice budget. Legal standards are open terms with the W2
schema, never predicates the checker decides.

## 1. Semantics

### 1.1 A rights document

```text
environment `rights` block (identity-bound like `regulated` and `soft`):
  holder sorts H, bearer sorts B ⊆ sorts(E)   "person"; "state", "person", "group"; "community" (Art. 29(1))
  protected ⊆ base predicates                the Art. 2 list (race, colour, sex, language, religion, opinion, …)
  alters : act ↦ status predicate            acts that change a holder's status (marry, deprive of nationality)
right R       := stable name; holder sort h ∈ H; holder guard H_R(h) (Art. 11(1)); incident lines; number = document order
incident line := kind ∈ {claim, liberty, immunity, power}; one W1/soft rule N whose shape matches the kind;
                 holder slot := the unique object slot of sort h (HolderSlotAmbiguous otherwise)
limitation L  := stable name; scope ⊆ rights or `all`; per act a in scope a fresh open base predicate lim_{L,a} with a's
                 sorts (name rights__lim__<L>__<act key>, soft-norms.md 1.3 discipline); one shared W2 open-term schema
bar           := an Art. 30 unit: a hard prohibition line with an open classification guard, or a non-entailment query
```

Shapes: a **claim** line's subject has a bearer sort, its holder slot is an object, its predicate is an obligation
(`must`, `+`) or a permission of sign `−` (`must not`). A **liberty** line's subject is the holder, its predicate a
permission of sign `+`. An **immunity** is a claim of sign `−` on an `alters` act (Art. 15(2), 17(2)). A **power** is a
liberty on an `alters` act plus one claim that every bearer recognise the result (Art. 15(1), 16(1), 23(4)).
`IncidentShape` rejects a mismatch; labels carry no semantics beyond the rules they type. "Anyone" as bearer fans out
into one rule per declared bearer sort (distinct acts by W1's act identity).

### 1.2 Elaboration `correlate(D) = T″` and the direct semantics

`T″` is every line's rule unchanged, except that each line of a right `R` receives one packed carve-out `lim_{L,a}(x̄)`
per limitation with `R` in scope; a power contributes two rules, "anyone" its fan-out, the bar its rule under the rule
reading. No derived precedence, rank or premise; `E″ = E + {lim_{L,a}}`, regenerated at every site. With no limitation,
power, fan-out or bar, `T″` is the lines byte for byte (`correlate_identity`). `ValueRight` is W1's `Value` (soft:
`ValueSoft`) on the lines with `live_N := G_N ∧ ¬⋁U_N ∧ ¬⋁_{L∋R} lim_{L,a}(x̄)`, so `Norms.Value T″ = ValueRight D` by
unfolding (`correlate_faithful`, the soft-norms 5.1 pattern). Right-level answers are projections of the completed
outcomes in the unique expansion `S`:

```text
owes(b, h, a)(S) := O_{a_required}(b, …, h, …)  (claim on an obligation) | ¬O_{a_permitted}(b, …, h, …)  (must not)
free(h, a)(S)    := O_{a_permitted}(h, …)                                                        (liberty)
rightsOf(h, S)   := {(R, kind, b, a) : owes(b,h,a) ∨ free(h,a)}      dutiesOf(b, S) := {(R, h, a) : owes(b,h,a)}
```

`projections_agree`: `(R, claim, b, a) ∈ rightsOf(h)` iff `(R, h, a) ∈ dutiesOf(b)`. Correlativity is a theorem only
because a claim and its duty are one rule. The checker never *infers* a positive duty from a negative one, a bearer from
a holder, or a claim from a liberty; those are readings.

### 1.3 Readings (translation mode)

Three axes stay open where the source leaves them (VISION.md 3): **bearer** (every state; the state of jurisdiction or
nationality; every person; every party; the community), **polarity** (negative: do not deprive or interfere; positive:
secure, provide, protect against third parties; both) and **incident** (claim; liberty; liberty plus protective claim;
power). A candidate is a complete right block with elaborated lines and a distinguishing checked situation; a candidate
without lines is an inventory and counts nothing (North Star). Enumeration fits W2's 64 complete choices through two
**shared** sets that article units cite: `rs_bearer` (Preamble "every individual and every organ of society … Member
States have pledged": {states only, states and every person}) and `rs_polarity` ({negative only, negative and
positive}). A per-unit set exists only where the text opens an axis the shared sets do not settle; a cited narrowing
closes an axis the text fixes ("protection by society and the State", Art. 16(3): bearer and positive; "No one shall be
subjected to", Art. 5, 9: negative; "by the competent national tribunals", Art. 8: positive, the state). A conclusion
depending on more than 64 combinations is UNKNOWN, with the units named. Worked example, Art. 3:

```text
Right 3. Every person has the right to life.
  Claim of right 3 (rs_bearer). Every state must not deprive each person of life.
  Claim of right 3 (rs_polarity: positive). Every state must protect each person within its jurisdiction against
    deprivation of life.                                    ("within its jurisdiction" open; separating situation: a state
                                                             that fails to protect but does not deprive)
Art. 5: Claim of right 5. Every state must not subject each person to treatment that is torture or is cruel, inhuman or
  degrading.    (fan-out to `person` under rs_bearer; `degrading`, `cruel`, `inhuman` open; decider unstated)
Art. 25: Claim of right 25 (default). Every state should secure for each person a standard of living that is adequate …
  The exception to this line takes account of the resources of that state.   (`adequate` open; soft line)
```

### 1.4 Limitations, the bar and non-discrimination (Art. 29, 30, 2)

**Art. 29(2)** is one limitation `L29`, scope `all`: `lim_{L29,a}` is open, decider unstated (a narrowing may cite
Art. 8's tribunals), `necessary` "determined by law" (a base predicate, hence a premise), factors "the rights and
freedoms of others", "the just requirements of morality", "public order", "the general welfare in a democratic
society", with `just` and `democratic society` open terms. English: `Limitation 29 (on every right). A right in this
document is limited in a situation only where that limitation is determined by law and is solely for a permitted
purpose.` The word **"only"** is the executable check `limitationScope`: every carve-out on, and every exception rule
over, a right-derived rule in scope is (a) the `lim_{L29,·}` carve-out, (b) a source-cited exception (Art. 14(2), 29(3))
or (c) a rule whose guard is certified to entail `lim_{L29,a}` over `Background_base`; anything else is
`UnlicensedLimitation: rule <n> on right <R>`. The check bites when an adopter's norms document (a state's law, a
policy) is composed with the Declaration: it answers "does this policy narrow a right the Declaration does not
license?" structurally and leaves lawfulness to the decider. **Art. 14(2)** is the pilot's `rs_u052`: {carve-out on
every line of right 14 ("right inapplicable"), on the claim line only ("invocation barred")}, `genuine` open.
**Art. 29(3)** is a second limitation on liberty lines, `contrary_to_un_purposes`, reading set {liberty lines, all
lines} (`rs_u112`). **Art. 29(1)** is a claim of holder sort `community` against every person with an open act.
**Art. 30** is a reading set {a hard line on every bearer sort, `must not perform each act aimed at the destruction of
a right`, `aimed_at_destruction` open, `hard: true`; a checked **non-entailment query** "no liberty for a destructive
act is derivable"} (`rs_u114`). **Art. 2 and 7** ("without distinction of any kind") are the executable check
`noDistinction`: no protected predicate in the dependency cone of any right-derived rule; soft-norms
`cone_independent` then gives `no_distinction_sound`: every `owes` and `free` outcome is invariant under the protected
predicates. Substantive equality stays the pilot's open term `equal_before_law`.

### 1.5 Shared with soft norms; the same-act limit; other limits

Positive social rights (Art. 22, 25(1), 26(1) "generally available") are default lines; "in accordance with the
organization and resources of each State" (Art. 22) is a `necessary` condition or factor of the exception, never a
silent strict duty. The Declaration ranks nothing, so every collision of two rights on one act is a WEIGHING POINT with
an unstated decider; Art. 29(2)'s "rights and freedoms of others" names those points. Collisions are same-act
(soft-norms.md 4.5): Art. 19's liberty to impart and Art. 12's claim against attacks on honour collide only if both
regulate one declared act; the status text says "among rules on the same act". Powers and immunities are static: the
checker knows marrying is permitted and must be recognised, not what duties follow (stage-3 trigger: a recorded
inference that needs the change, converged rule item 3). No fulfilment or time: `violation := required ∧ ¬done` is W3
above the norms. "Peoples" and "the family" need declared sorts or stay open. Preamble "have pledged" is W2 attribution.
Whether a right is respected in the world is never certified.

## 2. English wordings (one reading each; rejected as today when `rights@0` is off)

| Wording | The one reading (the IDE's paraphrase); formal effect |
|---|---|
| `Right n. Every <holder>[ that C] has the right to <phrase>.` | Names the holder and the right; requires or permits nothing by itself: the right means exactly its lines (`RightWithoutIncident` if none). Right `R`, `H_R`. |
| `Claim of right n. Every <bearer> must <act> each <holder> …` / `must not …` `[, if C][, unless U]` | The bearer owes this to the holder in every situation of the kind. `should`, `(default)`, `(users may turn off)` as soft-norms.md 2.1. A W1/soft rule of kind `claim`. |
| `Liberty of right n. Every <holder> may <act> …` / `generally may` | The holder is permitted; no duty follows from this line. Permission `+`, kind `liberty`. |
| `Immunity of right n. Every <bearer> must not <alter-act> each <holder> …` | The bearer cannot lawfully change the holder's status this way. Kind `immunity`. |
| `Power of right n.` + one liberty sentence + one `… must recognise …` claim | The holder may perform the act and every bearer must recognise its result; later effects are not modelled. Two rules. |
| `Right n includes:` + lines | Adds lines to the named right ("this right includes", Art. 18, 19). |
| `Limitation m (on every right \| on rights a and b). A right in this document is limited in a situation only where <open term>.` | Every line in scope gives way where the limitation holds; no other exception narrows a right unless written here or entailing the limitation. `L`, `lim_{L,a}`, `limitationScope`. |
| `No <holder> shall be <passive act>.` (input only) | Not a line: the bearer is missing. The IDE offers a `Claim of right n` per bearer sort; translation records the set. |

Input synonyms: `is entitled to` → `has the right to`; `freedom of <noun>` becomes a liberty only through a declared act
phrase. `shall` is not a norm word: in translation a "shall" unit is a READINGS set {strict claim, default claim}
(soft-norms.md 2.2). The reader's checklist adds, per right: the holder; each bearer and what it owes in the example
situation ("Texas owes Ann: not to deprive her of life; nobody owes Ann protection under this reading"); each applicable
limitation and its decider; for a reading set, the separating situation.

## 3. What the checker certifies and what stays open

**Certified** (certificate or theorem bound to `environment_id` and the rights document hash; W1 and soft contracts
apply to `T″` verbatim): (1) `correlate_wellFormed`, `correlate_identity`, `correlate_faithful`; (2) `projections_agree`;
(3) conflict-freedom of the duties or a witness situation by the unchanged W1/soft machinery on `T″` (conditional on
`Coh_T` where default lines exist), and the colliding rights on shared acts; (4) `limitation_scope_sound`: a passing
scope check means every narrowing of a right in scope is the limitation carve-out, a cited exception or a certified
lawful limitation; (5) `no_distinction_sound`; (6) the Art. 30 non-entailment query or a derivation exhibiting the
liberty; (7) wire theorems in the norms.md 11.4 shape, certificates stale under any change to a line, scope, limitation
schema, protected list or reading choice.

**Open, never certified:** every legal standard (`arbitrary`, `fair`, `degrading`, `adequate`, `genuine`, `effective
remedy`, `independent and impartial`, `determined by law`, `aimed at destruction`); who bears the duty and whether it is
positive, where the source is silent; the weighing between rights; whether a limitation is lawful in fact; the dynamic
effect of a power; whether any duty is fulfilled.

## 4. Lean obligations (`lean/VE/Rights/*`; frozen `Norms/*`, `Route/*` untouched; soft names as in soft-norms.md 9)

```lean
namespace VE.Rights   -- RightsDoc = SoftDoc + holders, bearers, protected, alters, rights (lines), limits, bar
def WellFormedRights (D : RightsDoc) : Bool         -- shapes, holder slots, scopes, protected/alters typing, fan-out
def correlate (D : RightsDoc) : SoftNorms.SoftDoc  -- lines + lim carve-outs + power/fan-out/bar rules; E″ = E + lims
def ValueRight (D) (r : Regulated) (S : VE.Structure) (vs : List S.Carrier) : Option Bool
def limitationScope (D) (certs : List (Option Certificate)) : Bool      def noDistinction (D) : Bool

theorem correlate_wellFormed (D) (h : WellFormedRights D = true) : SoftNorms.WellFormedSoft (correlate D) = true
theorem correlate_identity (D) (h) (hn : D.limits = [] ∧ noPowers D ∧ noFanOut D ∧ D.bar = none) :
  (correlate D).T.nodes = (linesOf D).map (·.rule)
theorem correlate_faithful (D) (h) (r) (hr) (S) (vs) : SoftNorms.ValueSoft (correlate D) r S vs = ValueRight D r S vs
theorem projections_agree (D) (h) (S) (b h' a) :
  (∃ R, (R, .claim, some b, a) ∈ rightsOf D S h') ↔ (∃ R, (R, h', a) ∈ dutiesOf D S b)
theorem limitation_scope_sound (D) (h) (certs) (hc : limitationScope D certs = true) (L) (N) (hN : Narrows D L N) :
  isLimCarveOut L N ∨ cited D N ∨ ∀ B, BaseAdmissible (correlate D) B → GuardEntailsLim B L N
theorem no_distinction_sound (D) (h) (hd : noDistinction D = true) (p) (hp : rightDerived D p) (B R)
  (hR : ∀ q vs, q ∉ D.protected → (R q vs ↔ B.relation q vs)) (vs) :
  (outcomeBase (correlate D) p).denote {B with relation := R} (tupleVal vs) ↔ (outcomeBase (correlate D) p).denote B (tupleVal vs)
-- rights_wire_acceptance, rights_wire_conflict_sound: norms.md 11.4 shape from raw JSON through `ve_rights_route`,
-- every checker call delegated to unchanged W1/soft functions on the regenerated E″, T″.
```

`correlate_faithful` is by unfolding (the carve-out is ordinary); `no_distinction_sound` is `cone_independent` with
`Q := protected`; `limitation_scope_sound` composes the syntactic check with `norms_route_acceptance` for case (c). No
route theorem is restated: `correlate D` is a soft document and inherits `soft_route_acceptance` and
`soft_route_countermodel` (W1's when no line is default). Audit: existing allowlist, no `sorry`; `lean/RIGHTS.md`.

## 5. Coverage accounting

Statuses stay CHECKED / LABELLED / OPEN / READINGS / UNFORMALISED. A right whose active lines are strict rules over
declared vocabulary with no open term is CHECKED; one with an open standard in a guard, act or limitation is OPEN
(`{"open": ["arbitrary", "rights__lim__l29__arrest_permitted"]}`); one whose bearer, polarity or incident is unsettled
is READINGS only when every candidate has elaborated lines and a distinguishing situation; headers and Preamble
"Whereas" units stay LABELLED or attribution. New residual lines: `bearer_readings`, `polarity_readings` (shared sets
counted once), `incident_readings`, `limitation_terms` (with decider and `necessary` count), `power_shadows`,
`unlicensed_limitations`, `distinction_hits`, `narrowings` (with citations). Open standards count once per term;
deciders are `unstated` unless a source unit names one, so the pilot's `applicable_court` and
`human_rights_interpreter` become cited narrowings or `unstated`. No gain is counted without the soft-norms plan's three
gates: end-to-end `ve document check` admission of right units, a split-only baseline under `norms@0` alone, and blind
whole-span fidelity review auditing every bearer and polarity choice. North Star's 0–8,800 B is an upper bound on
tagged spans, not a forecast; this plan predicts no number.

## 6. Work items

| # | Item | Owner, effort |
|---|---|---|
| 0 | Prerequisites: soft-norms items 0 (document-level norm admission), 2 and 4 merged (rights reuse `SoftDoc`, `ValueSoft`, `cone_independent`, the soft route); W1 fixtures green | soft-norms owners |
| 1 | `docs/spec/rights.md`: 1.1–1.5 as definitions; exact grammar for section 2; diagnostics (`IncidentShape`, `HolderSlotAmbiguous`, `RightWithoutIncident`, `UnlicensedLimitation`, `UnknownRight`, `ProtectedInGuard` warning); fixtures; Astra + Fable statement review before 2–4 (PLAN-EXPAND2 rule 10) | spec, 3 days |
| 2 | Profile `rights@0` requiring `norms@0` (soft optional): `rights` block; W2 unit kind `right` with `lines`, `includes`, `limitation`, `bar`; `correlate` in `ve/rights.py`; shared reading sets (`shared_by`) in W2; `ve document check` through the norms/soft route; `norms@0` and `soft-norms@0` fixtures and hashes unchanged | Python, 5 days |
| 3 | Surface registrations (`Right n.`, `Claim/Liberty/Immunity/Power of right`, `includes:`, `Limitation m`, `has the right to`, `is entitled to`, passive rewrite; `Rule ` and `Right ` distinct keywords); W7 harness; `tests/test_english_unambiguity.py` | `ve/surface/rights.py`, 3 days |
| 4 | Lean `lean/VE/Rights/{Tree,Correlate,Semantics,Scope,Wire,Admission,Run}.lean`, section 4 theorems, executable `ve_rights_route`; `lean/RIGHTS.md`; frozen files untouched | Lean, 5 to 7 days |
| 5 | Coverage residual lines; shared-set enumeration accounting; `conditional_on` inherited (metrics schema addition only) | Python, 2 days |
| 6 | W8: `add_right`, `add_line`, `add_limitation`; "who owes what to whom" paraphrase; translation rule for `has the right to` and `shall` (never collapse; propose the bearer set); fidelity gate | `ve/assist/*` |
| 7 | UDHR rerun: Art. 2–3, 5, 8–10, 12, 14, 16, 18–19, 22, 25–26, 29–30 with shared sets and cited narrowings; split-only baseline; blind fidelity review; measured deltas only. Spot checks: 14th-s1 clauses 2–4 as claims of persons against states (L); two rights claims of the birthright debate (B) | pilot, 3 days |

Fixtures for item 1 (deterministic; Python and Lean where a case kind exists): (α) Art. 3 negative claim: `owes(Texas,
Ann, deprive)` false where Texas deprives nobody; `rightsOf`/`dutiesOf` agree. (β) Art. 5 fan-out to `state` and
`person`: two acts, one header. (γ) Limitation 29 on Art. 9: arrest permitted where `lim` holds, forbidden where not;
dropping `determined_by_law` from `necessary` breaks the certificate for "arrest without law is forbidden"; an adopter
rule "Every state may arrest each person, if that person is a journalist" is `UnlicensedLimitation`, and passes once
guarded by `lim_{L29,arrest}`. (δ) A claim guarded by `religion(h, r)`: `ProtectedInGuard`; the invariance witness.
(ε) Art. 16 power: liberty plus recognition claim; a refusing state breaches; nothing post-marriage is derivable.
(ζ) Art. 3 under `rs_polarity`: both candidates elaborated; "Texas owes Ann protection" holds under SOME with the
choice named. (η) Art. 30 both readings; the rule reading blocks a default liberty via `hard_over_soft`. (θ) `correlate_identity`;
every norms.md 10.1 row wrapped as a one-line right gives identical statuses. (ι) Budget: 40 units citing two shared
sets plus three per-unit sets enumerate 32 choices; a fourth per-unit set makes a document-wide conclusion UNKNOWN with
the units named. (κ) Art. 25 default line: OPEN, one `excepted` term; completion pair conflict as in soft-norms
fixture (γ) when `secure_permitted` is deny-by-default.

Review questions: is the static power shadow acceptable, or should powers stay UNFORMALISED until stage 3? Is Art.
29(2)'s "only" rightly a scope check plus open term rather than a rule? Should the shared bearer set be document-level
by default, or should every article carry its own set with the shared one as a narrowing?

## 7. Risks

1. **Entitlement read as permission.** A header with only a liberty line says less than the source. The IDE shows
   "nobody owes the holder anything under this reading"; translation sets always include a claim candidate where the
   source is passive; item 7 audits per unit.
2. **Invented bearers.** "Every state" is a choice the Declaration never makes; the bearer is a shared reading set with
   the Preamble citation, never a checker default.
3. **Reading explosion.** Per-unit sets over 55 units exceed 64 choices; shared sets and named-unit UNKNOWN (fixture ι).
4. **Hohfeld labels overclaim.** Labels are shape-checked types; powers and immunities are static, and the report says
   "recognition required; later effects not modelled".
5. **Rule budget and same-act blindness.** Fan-out and positive candidates can approach W1's 256 rules (only the active
   choice is elaborated; measured in item 7); most inter-right conflicts are practical, not same-act, and stay invisible.
6. **Open standards read as decided; no measurable gain.** Standards are the residual headline, grouped by decider. The
   70 blocked units are labels, most with open standards and some with attribution, causation, time or metaphor
   co-blockers; the pilot number is reported as measured, including zero.

## Summary

Rights enter VE as the holder-side view of W1 and soft-norm rules: a right block names a holder and lists Hohfeldian
incident lines (claim, liberty, immunity, power), each an ordinary rule whose shape the checker types, so correlativity
is a theorem by construction and "who owes what to whom" is a projection of outcome tables. `correlate` adds only
limitation carve-outs, power recognition claims and bearer fan-out, so W1 and soft-route theorems are reused
unchanged. Article 29 becomes an open limitation term plus an executable "only such limitations" scope check, Article 2
a non-discrimination check via cone independence, Article 30 a hard rule or a non-entailment query. Bearer, polarity
and incident stay reading sets, shared document-wide to fit W2's 64-choice budget; legal standards stay open terms
with deciders. Coverage counts a unit only after end-to-end admission, a split-only baseline and blind fidelity
review; no number is predicted.

## Change log

| Date | Revision | Changes |
|---|---|---|
| 2026-09-27 | Draft 1 | Initial plan: rights as holder-side view of W1/soft rules; incident shapes; `correlate`, `ValueRight`; shared reading sets; Art. 29/30/2 as limitation term, scope check, bar and non-discrimination check; Lean statements; coverage lines; work items; fixtures; risks. Plan only. |
