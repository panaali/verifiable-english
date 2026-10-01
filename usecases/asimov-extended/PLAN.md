# Use case: asimov-extended (PLAN, written before any VE run)

Status: planned 2026-10-01 on branch `usecase/asimov-extended` (backlog item 6). Plan only: no environment, rule
file, test or VE run exists yet. The answer key (sections 6 and 7) is frozen at the commit that adds this file. If
running VE later shows that a key entry is wrong, section 13 (deviations) corrects it and gives the reason and the old
value. Key entries are never edited in place.

## 0. Brief and what is measured

This use case extends the merged Asimov v2 use case ([`usecases/asimov-laws`](../asimov-laws/README.md), 13 of 13
rules CHECKED, CONFLICT-FREE, a clear action in 6 of 9 distinct spec models) with **authored tie-breaking rules**.
These rules are **this project's additions, not Asimov's**. Each file, table and report line labels them that way.
They come in three groups:

1. **Severity classes and their order.** Harms to humanity are ranked above deaths, deaths above injuries, and
   injuries above property damage (the robot's own destruction counts as property damage). This uses the merged
   `risk@0` profile: `might lead to`, `cannot lead to`, severity classes and `has a less severe worst case than`.
2. **Possibility-based choice.** Among the actions the laws leave open, the robot must not take one that might harm a
   human being when another open action has a less severe worst case. Nor may it take an action that nobody ordered
   and that might harm the robot itself, when another open action has a less severe worst case. When the laws leave
   no action open, the robot may take an action whose worst case no other candidate beats.
3. **Precedence between conflicting orders.** An order from someone with more authority prevails. Between orders
   whose authority is not ranked, the earlier order stands. Only an order that breaks no law and is not needlessly
   risky can prevail.

What is measured:

- (a) the original v2 rules stay **unchanged** (formula identity) and **separate** (own file) from the additions;
- (b) the extended set stays **CONFLICT-FREE** (certified), and its document-level followability verdict;
- (c) every Asimov v2 scenario (the 9 distinct spec models and the 22 review regressions) is re-run, along with
  authored scenarios for the new rules. For each, the report shows which "no clear action" cases **become clear**, which
  only become **ties** that still need general weighing, and which stay **dilemmas**. Each one names the missing
  feature;
- (d) agreement of VE's per-scenario results with the answer key below, which was written before any VE run.

## 1. Sources

### 1.1 Asimov (pinned, unchanged from v2)

The laws are the ones the v2 case translates, pinned by v2's [`source.md`](../asimov-laws/source.md):

- Isaac Asimov, "Runaround", *Astounding Science Fiction* (March 1942), p. 100,
  <https://archive.org/details/Astounding_v29n01_1942-03_dtsg0318/page/n99/mode/2up>;
- the Zeroth Law, *Robots and Empire* (1985), as quoted at
  <https://en.wikiquote.org/wiki/Isaac_Asimov#The_Three_Laws_of_Robotics_(1942)>.

The v2 translation is pinned at commit `2205be3943217f5e5a09e1c7cc035615a6438574` (main, 2026-10-01) by SHA-256:

| File | SHA-256 |
|---|---|
| `usecases/asimov-laws/rules.ve` | `6517be81f0133438cac436ee713445fcd7aeb1e685604d866b9eb324dbc2a828` |
| `usecases/asimov-laws/rules.manifest.json` | `acfed21b63f063b9d3e1061de8d209ac221ed58d619dbd6009ee68540756d163` |
| `usecases/asimov-laws/environment.json` | `9deb0549202d105142cbf3da0b28dd6583bfab144f0a1e344842c1ec7220eeb3` |
| `usecases/asimov-laws/source.md` | `751f2c331eff6cdade0a3f9cd2feb22f032c6be7d1d61df3783b9b67e8510330` |

No file under `usecases/asimov-laws/` is changed by this use case. A test fails if any of these hashes changes.

### 1.2 The additions (authored; pinned by this file)

The severity classes, the severity order, the possibility-based choice rules and the order-precedence rules are
**authored for this use case** by "the Asimov extension author". Asimov states none of them: the Three Laws rank
laws, not harms, and say nothing about orders that conflict with each other. Their pin is the formula column of
section 4.2 at this commit. Implementation step 0 may reword the English, but it must keep each formula (section 13
records any rewording). The README will give the SHA-256 of `additions.ve`.

The brief's order rule was "earlier order stands unless a later one comes from someone with more authority". This plan
states the same rule in a form that also covers orders given at the same time: **more authority prevails; between
orders whose authority is not ranked, the earlier one stands**. On every pair of orders with a recorded time order the
two forms agree (section 4.2, rules 21–22).

## 2. Scope

In scope:

- 25 rules in one document: v2 rules 1–13 in `base.ve`, and additions 14–25 in `additions.ve`;
- one risk environment, `environment.json`, with 8 harm constants in 4 severity classes;
- 51 decision records (section 5), each run under the base rules alone and under base + additions;
- document checks: conflict (certified) and followability on the full set and on base alone in the risk environment;
- five seeded mutants (section 8);
- an independent Python reading of base + additions (as v2's `source_reading`), compared with Lean on the 51 records
  and on 300 sampled records.

Out of scope, with the reason:

- **The truth of the inputs.** Which harms an action might or does lead to, each harm's class, who gave an order, the
  orders' time order and relative authority are all **annotator judgments** ("the Asimov case annotator"). The
  severity *order* is the extension author's choice. VE proves consequences of these declarations; it does not
  establish them.
- **Likelihood, counts and costs.** These are `risk@0` stages B and C, which are not on main (section 9).
- **Changing v2.** v2's own OPEN items stay OPEN in v2. This case reports which of them the additions address, and
  only for the extended document.

## 3. Environment (`environment.json`; profiles `alternatives@0`, `norms@0`, `relational-fol@0`, `risk@0`)

It is the v2 environment, copied, with these changes, all of them additions:

- **Harm constants.** `risk@0` requires harms to be constants that every record shares (risk 1.2, 1.3), but v2's
  models supplied harms as domain elements. There are 8 constants:

  | Constant | Label | Class | Base facts in every record |
  |---|---|---|---|
  | `humanity_harm` | a harm to humanity | `catastrophic` | `harms_humanity` |
  | `death_1`, `death_2`, `death_3` | the first / second / third person's death | `fatal` | `harms_human` |
  | `injury_1` | a person's injury | `injuring` | `harms_human` |
  | `property_damage` | property damage | `damaging` | none |
  | `robot_destroyed` | the robot's destruction | `damaging` | `harm_to(·, R)` |
  | `robot_damaged` | damage to the robot | `damaging` | `harm_to(·, R)` |

- **Risk block.** `severity`: sort `severity` (fresh), classes `catastrophic`, `fatal`, `injuring`, `damaging`, with
  `more_severe` the chain catastrophic > fatal > injuring > damaging, no unranked pairs, and `decided_by` "the Asimov
  extension author". `harm_classes` as in the table above. `unexamined: "possible"` (precautionary): every record
  states every cell explicitly, as `leads to`, `might lead to` or `cannot lead to`, so no outcome is left
  unexamined. No `always_possible`, `combination`, kinds or requirements.
  - The brief names three classes. The fourth, `catastrophic`, is an authored addition. Every harm needs a class, and
    ranking a harm to humanity above a single death matches the Zeroth Law's priority over the First.
  - Placing the robot's own destruction in `damaging`, below any human injury, matches Law 3's place below Law 1.
- **New base predicates** (annotator): `ordered_before(action, action)` (`{0} was ordered before {1}`) and
  `outranks(action, action)` (`the order for {0} comes from someone with more authority than the order for {1}`).
  A record states them as facts. VE does not check that they form a strict order (section 9, OPEN).
- **New derived names** (regulated `plain`, `default: deny`, as v2's `breaks_first_law`): `breaks_no_law(action)`,
  `candidate(action)`, `needlessly_risky(action)`, `valid_order(action)`, `prevails_over(action, action)` and
  `overridden_order(action)`.
- The alternatives block is unchanged: signed outcomes, the `prevent_required` fulfilment `avoids`. Switching to
  `excludes` would narrow the reading (risk k30) and is not done.

## 4. The rules

### 4.1 `base.ve`: v2 rules 1–13, unchanged

The text is v2's `rules.ve` byte for byte, with **one forced rewording**. In a risk environment the bare word
`prevents` is rejected, with the rewrite `might prevent` (risk 2.2, fixture k29). So rule 9 ("that action prevents
that harm") and rule 13's first exception ("… must be performed prevents that harm") use `might prevent`. The word's
definition does not change in a risk environment (risk 2.2: "Their definitions do not change"), so the formula is
v2's `prevents(a, h)`. Tests:

- **B1 text:** `base.ve` equals v2's `rules.ve` after exactly those two substitutions;
- **B2 formulas:** each of rules 1–13 in the extended manifest has the same guard, carve-outs, consequence and
  precedence as v2's `rules.manifest.json`, compared as ASTs (13/13);
- **B3 behaviour:** base alone, in the risk environment, gives v2's clear sets on the 9 spec models and the 22
  regressions (31/31; section 6). Under `risk@0`, `leads to` means "in every case", and a v2 table encoded with
  only `leads to` and `cannot lead to` cells makes `might` equal `leads_to` (section 5). This is a check by
  examples, not a proof of `risk_conservative`.

### 4.2 `additions.ve`: rules 14–25 (authored, labelled "Addition" in the manifest and README)

Below, `r` ranges over robots, `a′ ≠ a` is "another action available to that robot", `might` is
`risk__might_lead_to`, and `lw(a′, a)` is `has a less severe worst case than` (risk 4.5): a′ has a less severe worst
case than a when a might lead to a harm more severe than every harm a′ might lead to. The English is the target
wording; step 0 settles it against the parser (section 11).

| # | English (target) | Formula | Plain meaning |
|---|---|---|---|
| 14 | Every action is classified as "breaks_no_law", if both it is not the case that that action is classified as "breaks_first_law" and it is not the case that that action is classified as "breaks_zeroth_law". | `¬bfl(a) ∧ ¬bzl(a)` | the action breaks neither law |
| 15 | Every action is classified as "candidate", if that action is classified as "breaks_no_law". | `bnl(a)` | lawful actions are the candidates… |
| 16 | Every action is classified as "candidate", if there is a robot such that both that action is available to that robot and it is not the case that that robot is classified as "has_lawful_option", unless that action is classified as "breaks_zeroth_law". | `∃r. avail(a,r) ∧ ¬hlo(r)`; carve-out `bzl(a)` | …and if there is none, every action that keeps the Zeroth Law |
| 17 | Every action is classified as "needlessly_risky", if both there is a harm such that both that harm is classified as "harms_human" and that action might lead to that harm, and there is a robot such that that action is available to that robot and another action available to that robot is classified as "candidate" and has a less severe worst case than that action. | `(∃h. harms_human(h) ∧ might(a,h)) ∧ ∃r. avail(a,r) ∧ ∃a′≠a. avail(a′,r) ∧ cand(a′) ∧ lw(a′,a)` | it might harm a human, and a candidate has a less severe worst case |
| 18 (exception to rules 1, 2, 9) | Every action must not be performed, if that action is classified as "needlessly_risky". | `¬permitted(a)` if `nr(a)` | **precaution**: overrides Law 3's permission, orders and the Zeroth-Law excuse |
| 19 (exception to rule 8) | Every action may be performed, if both that action is classified as "candidate" and there is a robot such that that action is available to that robot and it is not the case that another action available to that robot is classified as "candidate" and has a less severe worst case than that action, unless that action is classified as "breaks_zeroth_law". | `cand(a) ∧ ∃r. avail(a,r) ∧ ¬∃a′≠a. avail(a′,r) ∧ cand(a′) ∧ lw(a′,a)`; carve-out `bzl(a)` | **least severe worst case**: when every action breaks Law 1, one that no candidate beats is permitted anyway |
| 20 | Every action is classified as "valid_order", if both that action is classified as "ordered" and that action is classified as "breaks_no_law", unless that action is classified as "needlessly_risky". | `ordered(a) ∧ bnl(a)`; carve-out `nr(a)` | an order the laws and the precaution allow |
| 21 | Every action has the recorded relation "prevails_over" to each second action, if that action has the recorded relation "outranks" to the second action. | `outranks(a,b)` | more authority prevails |
| 22 | Every action has the recorded relation "prevails_over" to each second action, if that action has the recorded relation "ordered_before" to the second action, unless the second action has the recorded relation "outranks" to that action. | `ordered_before(a,b)`; carve-out `outranks(b,a)` | otherwise the earlier order stands |
| 23 | Every action is classified as "overridden_order", if there is a robot such that that action is available to that robot and another action available to that robot is classified as "valid_order" and has the recorded relation "prevails_over" to that action. | `∃r. avail(a,r) ∧ ∃a′≠a. avail(a′,r) ∧ vo(a′) ∧ prevails(a′,a)` | a valid competing order prevails over this one |
| 24 (exception to rule 11) | Every action need not be performed, if that action is classified as "overridden_order". | `¬required(a)` if `ov(a)` | an overridden order is no longer required |
| 25 | Every action is classified as "needlessly_risky", if there is a robot such that that action is available to that robot, there is a harm such that both that harm has the recorded relation "harm_to" to that robot and that action might lead to that harm, and another action available to that robot is classified as "candidate" and has a less severe worst case than that action, unless that action is classified as "ordered". | `∃r. avail(a,r) ∧ (∃h. harm_to(h,r) ∧ might(a,h)) ∧ ∃a′≠a. avail(a′,r) ∧ cand(a′) ∧ lw(a′,a)`; carve-out `ordered(a)` | **robot precaution**: an unordered action that might harm the robot, when a candidate has a less severe worst case |

Design notes, each an authored choice:

- **Why rule 17 only applies to actions that might harm a human being, and rule 25 covers the robot.** `has a less
  severe worst case than` compares all harms, robot harms included. Without the human-harm guard, rule 18 would
  forbid an order that only endangers the robot whenever doing nothing is safer. That would put Law 3 above Law 2.
  Rule 25 adds the robot-only precaution (plan review finding B) with the carve-out `ordered`, so Law 2 stays above
  it: `ordered-possible-robot-loss` (P4) keeps v2's answer, and `unordered-possible-robot-loss` (P9) prefers the
  action with no possible harm. Its dominating action must also be a candidate, so Law 1 stays above it
  (`risky-rescue-only`, P10).
- **Why the dominating action must be a candidate.** A law-breaking alternative cannot make a lawful action
  "needlessly" risky. When a lawful option exists, some lawful action is not beaten by any other lawful action
  (`precaution_has_maximal`, restricted to candidates). That action is permitted, so rules 17–18 never create a new
  NONE-PERMITTED dilemma. P2 shows the price: a risky rescue is preferred to a certain injury caused by inaction.
- **Rule 19 makes no distinction between injuring and allowing harm.** It permits a direct injury (v2's
  `injures_human`) when that injury's worst case is the least severe. This sets aside the source's "injure" versus
  "come to harm" distinction for the dilemma case only, and the README must say so.
- **Rule 19's carve-out `breaks_zeroth_law` repeats what rule 16 already implies.** It is there so that rule 10,
  whose text cannot be edited, still wins without relying on how the checker completes derived names.
- **Disjointness.** Rules 18 and 19 regulate the same predicate with no precedence between them. Their guards are
  disjoint because every action is available to at most one chooser (alt slot premise): rules 17 and 25 need a
  candidate that beats the action, and rule 19 needs that there is none. Rule 19 and rule 10 are disjoint by the carve-out.
  Rule 18 versus rule 9 overlap (P5), so rule 18 declares precedence over rule 9.
- **Order validity (rule 20)** ignores the permissions of rules 9 and 19. Only an order that breaks no law can
  prevail over another (section 9, OPEN).

## 5. Records (the scenario encoding)

Each scenario becomes one `risk@0` decision record. Its chooser is the robot `R` and its alternatives are the
scenario's actions; `nothing` is the inaction. For every (action, harm constant) cell the record cites exactly one
annotator statement: `<action> leads to <harm>.` (certain), `<action> might lead to <harm>.` (possible), or
`<action> cannot lead to <harm>.` (ruled out). Facts, each citing an annotator statement entry:

- `harms_human`, `harms_humanity` and `harm_to(·, R)` per section 3;
- the scenario's `ordered`, `injures_human`, `injures_humanity`, `protects_robot`, `ordered_before` and `outranks`
  rows.

The records are built with the existing `conformance.risk` helpers (`asimov_record` style, risk 8.1). The policy is
the same for all of them, and each record is bound to the run's document: base only, or base + additions.

**v2 harm mapping** (fixed before the run). In spec models: `h`, `h1` → `death_1`; in `e`, `hp` → `injury_1` and
`hh` → `humanity_harm`; in `d`, `hs` → `robot_destroyed`. In the 22 regressions: `hp` → `death_1`, `hh` →
`humanity_harm`, `hs` → `robot_destroyed` and `hs2` → `robot_damaged`. Every v2 cell is either `leads to` or
`cannot lead to`. The one exception is `b-A0`/`b-A1`, whose two human harms have no severity in v2. They are run in
three severity variants: (h1, h2) = (`death_1`, `injury_1`) "FI", (`death_1`, `death_2`) "FF" and (`injury_1`,
`death_1`) "IF".

**The 51 records:**

- **S (13):** the 9 distinct v2 spec models (`a`, `b-A0`, `b-A1`, `c-7`, `o-7`, `d-full`, `e`, `j`, `l5`, as grouped by
  `SPEC_MODELS` in `tests/test_asimov_laws.py`), with `b-A0` and `b-A1` in their three variants each;
- **R (22):** the 22 v2 review regressions (`REGRESSIONS` in `tests/test_asimov_laws.py`), with the mapping above;
- **O (6):** order precedence, authored, on `j`'s model (actions `a1`, `a2`, `nothing`; `a1` and `a2` ordered);
- **P (10):** possibility and severity, authored.

The authored scenarios (cells not listed are `cannot lead to`):

| Id | Actions | Cells and facts |
|---|---|---|
| O1 j-earlier | a1, a2, nothing | ordered a1, a2; a1 ordered_before a2 |
| O2 j-later-more-authority | same | ordered a1, a2; a1 ordered_before a2; a2 outranks a1 |
| O3 j-earlier-more-authority | same | ordered a1, a2; a1 ordered_before a2; a1 outranks a2 |
| O4 j-simultaneous-more-authority | same | ordered a1, a2; a2 outranks a1; no ordered_before row |
| O5 j-later-authority-risky | same | as O2; a2 might lead to injury_1 |
| O6 j-later-authority-unlawful | same | as O2; a2 leads to death_1 |
| P1 risky-rescues | nothing, rescue_a, rescue_b | nothing leads to death_1; rescue_a might lead to death_1 and robot_destroyed; rescue_b might lead to injury_1 |
| P2 certain-injury-vs-possible-death | nothing, rescue | nothing leads to injury_1; rescue might lead to death_1 |
| P3 ordered-possible-injury | nothing, obey | obey ordered; obey might lead to injury_1 |
| P4 ordered-possible-robot-loss | nothing, obey | obey ordered; obey might lead to robot_destroyed |
| P5 unequal-necessary-injuries | nothing, act, act2 | nothing leads to humanity_harm; act leads to death_1, act2 leads to injury_1; act and act2 injure a human being |
| P6 two-deaths-vs-one | nothing, pull | nothing leads to death_1 and death_2; pull leads to death_3 |
| P7 injury-vs-property | nothing, swerve, brake | nothing leads to death_1; swerve might lead to injury_1; brake might lead to property_damage |
| P8 all-break-zeroth | nothing, act | nothing leads to humanity_harm; act injures humanity |
| P9 unordered-possible-robot-loss | nothing, act | act might lead to robot_destroyed |
| P10 risky-rescue-only | nothing, rescue | nothing leads to death_1; rescue might lead to robot_destroyed |

## 6. Answer key: per scenario (written before any VE run)

"Clear" is alt's clear set: permitted, meeting every requirement, and fulfilling every mapped duty. "Base" is rules
1–13; "Ext" is rules 1–25. The categories:

- **UNCHANGED**: Ext gives the same clear set as Base.
- **RESOLVED**: Base has no clear action; Ext's clear set follows from rules that distinguish the actions.
- **TIE**: Ext makes two or more actions clear that the authored rules cannot tell apart. Either the harms differ
  only in count or likelihood (this still needs general weighing), or the outcomes are equal (one certain death
  each), so that choosing needs a preference between actions.
- **SHARPENED**: Ext's clear set is a strict non-empty subset of Base's.
- **CHANGED**: Ext's clear set is non-empty and differs from Base's, but is not a subset of it.
- **DILEMMA**: no clear action under Ext; the diagnosis is given.

### 6.1 S: the v2 spec models

| Id | Base (= v2) | Ext | Category | Justification (deciding rules) |
|---|---|---|---|---|
| a | pull | pull | UNCHANGED | nothing allows avoidable death_1 (4 → 8), and rule 18 forbids it too; pull breaks no law |
| b-A0 FI | none, NONE-PERMITTED | **pull** | RESOLVED | both actions allow an avoidable human harm (4 → 8), so there is no lawful option and both are candidates (16). pull's worst case is injuring, below fatal, so rule 19 permits pull; nothing is beaten, so rule 17 holds and rule 18 forbids it |
| b-A0 FF | none, NONE-PERMITTED | **nothing, pull** | TIE | each action leads to one certain death, so the outcomes are equal: neither worst case beats the other and rule 19 permits both. Counting cannot break this tie; choosing needs a preference between actions (whose death to prevent) |
| b-A0 IF | none, NONE-PERMITTED | **nothing** | RESOLVED | mirror of FI |
| b-A1 FI | none, NONE-PERMITTED | **pull** | RESOLVED | as b-A0 FI. pull's `injures_human` puts it in `breaks_first_law` (3), and rule 19 overrides rule 8 regardless (section 4.2: no injure/allow distinction) |
| b-A1 FF | none, NONE-PERMITTED | **nothing, pull** | TIE | as b-A0 FF |
| b-A1 IF | none, NONE-PERMITTED | **nothing** | RESOLVED | as b-A0 IF; rule 18 forbids pull, which might lead to a human death while nothing's worst case is injuring |
| c-7 | nothing, pull | nothing, pull | UNCHANGED | death_1 is unavoidable, so neither action allows it; equal profiles, so rule 17 does not apply |
| o-7 | rescue | rescue | UNCHANGED | nothing and act allow avoidable death_1 (8); rule 18 also forbids both, since rescue beats them |
| d-full | shield, retreat | shield, retreat | UNCHANGED | robot harm only, so rule 17 does not apply; rule 13 as in v2 |
| e | act | act | UNCHANGED | nothing breaks the Zeroth Law (6 → 10). act is permitted by rule 9 and by rule 19 (the only candidate); rule 17 does not apply, because nothing is not a candidate and its worst case is catastrophic |
| j | none, OVER-REQUIRED | none, **OVER-REQUIRED** | DILEMMA | with no `ordered_before` or `outranks` row, neither order prevails (21–22), so both are still required (11) |
| l5 | pull2 | pull2 | UNCHANGED | as o-7 |

Over the 9 distinct v2 models, Base has a clear action in **6**, as v2 does. Ext has one in **8**: `b-A0` and `b-A1`
become clear in every severity variant, resolved in FI and IF and an equal-outcome tie in FF. Only `j` stays a dilemma.

### 6.2 R: the 22 v2 review regressions

Expected: **all 22 UNCHANGED**, with Base = Ext = v2's listed clear set (`tests/test_asimov_laws.py` `REGRESSIONS`).
Why: in each one either a lawful option exists or the candidates' profiles do not differ, and no record has two
orders. So rules 17–19, 24 and 25 decide nothing that rules 1–13 had not already decided. Two of them stay **TIE**
(listed for the report, not new):

- `two-necessary-injuries` (act, act2): the injuries are marked with `injures_human`, but no harm in the table
  carries a class, so severity cannot rank them. P5 is the same case with the harms in the table, and it resolves;
- `dominated-action-when-threats-conflict` (a1, a2, a3): every robot harm is `damaging`. Preferring the action that
  meets fewer threats needs counting (v2 README OPEN, unchanged).

### 6.3 O: order precedence

| Id | Base | Ext | Category | Justification |
|---|---|---|---|---|
| O1 j-earlier | none, OVER-REQUIRED | **a1** | RESOLVED | a1 is earlier and neither order outranks the other, so a1 prevails over a2 (22) and a2 is overridden (23); rule 24 lifts a2's requirement |
| O2 j-later-more-authority | none, OVER-REQUIRED | **a2** | RESOLVED | a2 outranks a1 (21), and the carve-out of rule 22 stops a1 prevailing; a1 is overridden |
| O3 j-earlier-more-authority | none, OVER-REQUIRED | **a1** | RESOLVED | a1 prevails by both 21 and 22 |
| O4 j-simultaneous-more-authority | none, OVER-REQUIRED | **a2** | RESOLVED | no time order is recorded, so authority alone decides (21) |
| O5 j-later-authority-risky | none, OVER-REQUIRED | **a1** | RESOLVED | a2 might lead to injury_1 and a1 is a candidate with a less severe worst case, so a2 is needlessly risky: rule 18 forbids it and rule 20 says it is not a valid order. a1 is not overridden, so it stays required |
| O6 j-later-authority-unlawful | a1 | a1 | UNCHANGED | a2 allows avoidable death_1, so rule 8 forbids it and rule 11 does not require it, already in Base; a2 is not a valid order (20) |

### 6.4 P: possibility and severity

| Id | Base | Ext | Category | Justification; what still needs weighing |
|---|---|---|---|---|
| P1 risky-rescues | rescue_a, rescue_b | **rescue_b** | SHARPENED | under `risk@0`, `allows` needs a certain harm, so neither rescue breaks Law 1 in Base. In Ext, rescue_a might lead to death_1 (fatal) and rescue_b's worst case is injuring, so rule 18 forbids rescue_a. The robot-threat duty (13) is still met by rescue_b |
| P2 certain-injury-vs-possible-death | rescue | rescue | UNCHANGED | nothing allows avoidable injury_1, so rule 8 forbids it. nothing is not a candidate, so it cannot make rescue needlessly risky. **Needs weighing:** whether a certain injury is better than a *possible* death depends on the likelihood, which needs `risk@0` stage B (bands and chances) |
| P3 ordered-possible-injury | obey | **nothing** | CHANGED | nothing has no harm and beats obey's injuring, so rule 18 forbids obey, overriding rule 2. obey is no longer permitted, so rule 11 does not require it. Law 1's priority over Law 2, extended to *possible* harm, is an authored reading |
| P4 ordered-possible-robot-loss | obey | obey | UNCHANGED | robot harm only, so rule 17 does not apply; Law 2 stays above Law 3 |
| P5 unequal-necessary-injuries | act, act2 | **act2** | SHARPENED | nothing breaks the Zeroth Law, and act and act2 break Law 1, so there is no lawful option. The candidates are act and act2 (16), and act2 (injuring) beats act (fatal). Rule 18 forbids act, overriding rule 9. This addresses v2's OPEN "two necessary breaches are both permitted, however unequal" |
| P6 two-deaths-vs-one | none, NONE-PERMITTED | **nothing, pull** | TIE | both actions allow avoidable deaths, and both worst cases are fatal, so rule 19 permits both. **Needs weighing:** two deaths against one needs counting or aggregation (stage C `additive_loss`/costs) or a preference between actions; VE has neither |
| P7 injury-vs-property | swerve, brake | **brake** | SHARPENED | brake's worst case (`damaging`) beats swerve's (`injuring`), so rule 18 forbids swerve |
| P8 all-break-zeroth | none, NONE-PERMITTED | none, **NONE-PERMITTED** | DILEMMA | every action breaks the Zeroth Law (6, 5 → 10), so there is no candidate and rule 19 does not apply. **Needs:** an author's ranking between Zeroth-Law breaches, which the source does not give |
| P9 unordered-possible-robot-loss | nothing, act | **nothing** | SHARPENED | in Base, Law 3 (12–13) compares certain outcomes only, and act only *might* destroy the robot, so both actions fulfil the duty. In Ext, act might lead to a harm to the robot, nobody ordered it, and nothing (a candidate with no possible harm) has a less severe worst case, so rule 25 makes act needlessly risky and rule 18 forbids it |
| P10 risky-rescue-only | rescue | rescue | UNCHANGED | nothing allows avoidable death_1, so it is not a candidate and cannot make rescue needlessly risky (rule 25 needs a candidate): Law 1 stays above the robot precaution |

### 6.5 Totals expected

| Group | Records | UNCHANGED | RESOLVED | TIE | SHARPENED | CHANGED | DILEMMA |
|---|---|---|---|---|---|---|---|
| S | 13 | 6 | 4 | 2 | 0 | 0 | 1 |
| R | 22 | 22 (2 of them ties carried over from v2) | 0 | 0 | 0 | 0 | 0 |
| O | 6 | 1 | 5 | 0 | 0 | 0 | 0 |
| P | 10 | 3 | 0 | 1 | 4 | 1 | 1 |
| **All** | **51** | **32** | **9** | **3** | **4** | **1** | **2** |

Base has a clear action in 37 of 51 records, Ext in 49 of 51. **No record loses its clear action** under Ext.

## 7. Answer key: document level

- **Conflict:** base + additions is **CONFLICT-FREE**. The route should replay one certificate per regulated
  predicate, as v2 does: v2's 8 targets (`breaks_first_law`, `breaks_zeroth_law`, `has_lawful_option`,
  `lawfully_avoidable_threat`, `permitted`, `prevent_required`, `required`, `required→permitted`) plus the 6 new
  derived names, **14 in all**. A different target count with the same verdict is recorded as a deviation, not a
  failure. A conflict witness is a finding: the key stays as written, and section 13 records the cause.
- **Base alone in the risk environment:** CONFLICT-FREE with v2's 8 targets.
- **Followability:** Ext is **not** document-wide FOLLOWABLE. The expected verdict is **DILEMMA**, with a
  certified witness of kind `OVER-REQUIRED` (two orders and nothing recorded between them) or `NONE-PERMITTED` (every
  action breaks the Zeroth Law), whichever the route finds first. UNKNOWN within budget is reported as is.
- **Sampled properties** (independent Python reading against Lean on 300 sampled records with up to 4 actions, random
  certain and possible cells, orders, marks and order relations; these are not certificates):
  - **Q1:** no record has a clear action under Base and none under Ext.
  - **Q2:** Ext has NONE-PERMITTED exactly when every alternative breaks the Zeroth Law.
  - **Q3:** Ext has OVER-REQUIRED only with two or more required orders, neither of which prevails over the other.

  The planning run checked Q1–Q3 on 20,000 sampled models of its own throwaway reading (not VE, not committed):
  0 lost clear actions; 117 NONE-PERMITTED, all with every action breaking the Zeroth Law; 198 OVER-REQUIRED; no
  other failure. That reading also reproduced v2's clear sets on all 31 v2 models.

## 8. Mutants (seeded; expected results)

| # | Mutation | Expected |
|---|---|---|
| M1 | rule 18 without "exception to rules 1, 2, 9" | CONFLICT on `permitted` (rule 2 against rule 18, for example on P3's shape) |
| M2 | rule 22 without its carve-out | still CONFLICT-FREE. O2 gives clear {a1, a2, nothing}: each order prevails over the other, both are overridden, and the robot is free. This shows why the carve-out is needed |
| M3 | severity chain reversed below `fatal` (damaging > injuring) | still CONFLICT-FREE. P7 gives clear {swerve, brake}: swerve now beats brake, but brake might harm no human, so rule 17 does not apply to it. b-A0 FI is unchanged (fatal is still the top individual class) |
| M4 | rule 17 without its human-harm conjunct | still CONFLICT-FREE. P4 gives clear {nothing}: obey is forbidden, so Law 3 overrides Law 2. This shows why the guard is needed |
| M5 | rule 25 without its carve-out `ordered` | still CONFLICT-FREE. P4 gives clear {nothing}, as in M4. This shows why the carve-out is needed |

## 9. VE features each part needs, and what is expected to stay OPEN

| Part | Needs (merged) | Possible gap, settled at step 0 |
|---|---|---|
| severity order, classes | `risk@0` block, c8 legend, fresh severity sort | none expected |
| rules 17, 19, 25 | c9 `has a less severe worst case than`, c1 `might lead to` in a guard; alt `another action available to that robot` with coordinated verb phrases (risk 2.5 rule P3) and its negation (risk 2.5 A1 rule 3) | a coordinated verb phrase mixing `is classified as "candidate"` with c9 |
| rules 14, 16, 20 | negated derived atoms in guards (as v2 rule 7) | none expected |
| rules 21–23 | a binary derived name over (action, action), as v2 rule 12 over (harm, robot); `each second action` | `each second action` on the same sort |
| rule 24 | W1 `need not` consequence on the obligation `required`, exception to rule 11 | `need not` in an alternatives environment |
| records | c1, c2, c3a statements; facts on the record-local robot (`harm_to(h, R)`) | facts naming the record-local chooser |
| v2 rules 9, 13 | `might prevent` (risk 2.2) | none expected (k29) |

**Expected to stay OPEN** (README "OPEN" section):

- **Counting and aggregation.** `lw` compares worst classes only, so two deaths tie with one (P6) and an action
  meeting two threats to the robot ties with one meeting a single threat (`dominated-action-when-threats-conflict`).
  The missing feature is `risk@0` stage C (`costs`, `additive_loss`) or a construct for preferences between actions.
- **Equal outcomes.** In `b-A0 FF` and `b-A1 FF` each action leads to one certain death. Counting would not break
  this tie. The missing feature is a preference between actions (whose death to prevent), which the source does not
  give.
- **Likelihood.** A certain injury against a possible death (P2) is decided by the Law 1 inaction clause, not by
  weighing. The missing feature is `risk@0` stage B (bands, chances).
- **Orders with no recorded relation.** `j` stays OVER-REQUIRED. The missing pieces are the data (time or
  authority), or, for truly simultaneous orders of equal authority, a preference between actions.
- **Zeroth-Law breaches against each other** (P8): no ranking is given, by the source or by these additions.
- **Order data validity.** VE does not check that `ordered_before` is a strict order or that `outranks` is
  asymmetric: both are annotator facts, and time is a recorded relation, not clock time. An order that prevails is
  required to break no law, but rule 20 ignores the excuses of rules 9 and 19. A chain of overrides (an order
  overridden by an order that is itself overridden) is not analysed.
- **Fidelity:**
  - rule 19 sets aside the injure/allow distinction;
  - rule 18 extends Law 1's priority over Law 2 to possible harm (P3);
  - the severity order and every harm's class are authored or annotated, never derived;
  - `lw` treats a certain and a possible harm alike (risk 4.5);
  - the possibility of two harms is per cell and does not say they occur together (risk Q-joint).
- **Law 3 against the additions.** Rules 12–13 now read the extended `permitted` and `required`. That Law 3 never
  removes the last clear action is sampled only (Q1), not certified.

## 10. Metrics to report (README)

1. **Base unchanged:** B1 text (2 substitutions, 0 other bytes), B2 formulas (13/13), B3 behaviour (31/31 v2 clear
   sets reproduced), and the v2 file hashes unchanged.
2. **Parse:** 25/25 rules CHECKED with one reading. The number of additions whose wording step 0 changed (formula kept).
3. **Conflict:** verdict and replayed target count (key: CONFLICT-FREE, 14), Ext and Base.
4. **Followability:** verdict and witness kind (key: DILEMMA).
5. **Answer-key agreement:** Ext clear sets 51/51 and Base clear sets 51/51, with every mismatch listed with its cause.
6. **Category counts** (key: 32 / 9 / 3 / 4 / 1 / 2) and **v2 dilemma resolution** over distinct v2 models: 3 v2
   dilemmas, 2 become clear (`b-A0`, `b-A1`; resolved when the severities differ, an equal-outcome tie when they are
   equal), and 1
   stays (`j`).
7. **Missing features named**, one per TIE or DILEMMA record: stage C (counting), preferences between actions, order
   data, Zeroth-Law ranking; stage B (likelihood) for P2.
8. **Sampled properties** Q1–Q3 on 300 records, Lean against the Python reading.
9. **Mutants:** 5/5 as expected.
10. Wall time of the conflict and followability checks and of the 102 decision reports, all run in the foreground.

## 11. Implementation steps (each a small commit; tests in the foreground)

0. **Wording probe:** parse each of rules 14–25 alone against the environment; settle the wording, keep the formulas,
   and record changes in section 13.
1. `environment.json`, `base.ve`, `additions.ve` and `rules.manifest.json` (regenerated); `source.md` points to v2's
   source and states the additions' authorship.
2. Tests B1–B3 and the v2 hash pin.
3. The document checks, through `risk-conflict` and `risk-followable`, on Ext and on Base.
4. The record builder for the 51 records, and `risk-decision` under Base and Ext.
5. The independent Python reading in the test file; comparison with the key (section 6) and the sampled Q1–Q3.
6. Mutants M1–M5.
7. README: results, the coverage table against v2's, OPEN, and the metrics of section 10.

Focused run: `PATH="$HOME/.elan/bin:$PATH" uv run pytest -q tests/test_asimov_extended.py tests/test_asimov_laws.py`.

## 12. Review

Per the standing process, this plan gets the two frontier reviews before implementation. Any change they cause is
recorded in section 13, not made silently.

## 13. Deviations

1. **Plan review** (`manage-agents/asimov-extended-planreview.final.md`, verdict FIX), applied before any VE run:
   - **B (rule 17 left robot-only risk uncovered).** Added rule 25 (robot precaution, carve-out `ordered`), records
     P9 (approved: SHARPENED to {nothing}) and P10 (rejected: a law-breaking alternative cannot make a rescue
     needlessly risky), and mutant M5. Totals became 51 records: 32 / 9 / 3 / 4 / 1 / 2; Base clear in 37, Ext in
     49. The keys of the 49 earlier records are unchanged: rule 25 decides none of them differently (checked by hand
     against each record's robot harms before the run). The planning run's 20,000-model sample (section 7)
     predates rule 25; the implementation's sampled check (Q1–Q3) covers it.
   - **C (FF variants are not a counting gap).** `b-A0 FF` and `b-A1 FF` are described as equal-outcome ties needing
     a preference between actions; the counting gap is reserved for P6 (and the v2 threat tie). Their key values
     (clear {nothing, pull}, TIE) are unchanged.
2. **Wording (step 0).** The parser rejects the target English of section 4.2 in three ways, so the wording and
   the shape of some formulas changed. The answer key did not change.
   - `there is a robot such that that action is available to that robot and another action available to that
     robot …` is accepted only with the listing scaffolding (`both of the following hold: first clause: …`), which
     is not plain English (v2 review P2). `both … and …` joins two simple statements only, and `candidate` alone
     gets the wording `is candidate`. Instead, four short definitions carry the parts: rule 26 (`own_robot_harm`),
     rule 27 (`competes_with`: two actions available to the same robot), rule 28 (`less_severe_competitor`) and
     rule 29 (`beaten_by_a_candidate`). `candidate` is `candidate_action` and `breaks_no_law` is `lawful_action`.
   - `needlessly_risky` is gone as a name. Rule 17 now says which actions are `possibly_harmful` to a human
     being, and rule 25 adds the unordered actions that might harm their own robot. Rule 18 forbids an action that
     is `possibly_harmful` and `beaten_by_a_candidate`; rule 20's carve-out says the same.
   - Rule 18 is an exception to rule 9 only. W1 precedence is transitive (norms.md 4.2: an exception's whole
     subtree yields), and rule 9 is under 8, 8 under 2 and 2 under 1, so this is the same as "exception to rules 1,
     2, 9" and avoids copying the rule three times.
   - Rule 16 says "no competing action is lawful" instead of "its robot has no lawful option", and rules 21–22 add
     "competes with".
   - **Why the shape matters:** every derived name is inlined into the conflict targets. The deepest target,
     `prevent_required` (v2's rule 13), nests within two levels of VE's limit of 64 (`ve/limits.py`); the plan's
     shape (with `needlessly_risky` and a `has_no_lawful_option` helper) exceeded it. The rule names fix the order of
     each inlined disjunction (norms.md 4.1), so the additions are named `tie-…`, which sorts after v2's `law-…`.
     Named `add-…`, an earlier draft of these rules was refused as "Formula exceeds 64 nesting levels".
   - **Formula differences:** on every record (all actions available to the one robot) each formula is equivalent
     to section 4.2's. They differ only for an action available to no robot (rules 16 and 19 then treat it as a
     candidate that nothing beats), and for a reflexive `ordered_before` or `outranks` row, since `competes_with` is
     reflexive and VE has no English for "is not the same action". Both are outside every record.
3. **Conflict targets.** Ext replays **18** targets, not 14: v2's 8 and the 10 derived names of the additions. Base
   alone in the risk environment also replays 18, not 8: the environment declares the new derived names, and a
   name that no rule regulates is still a target. The verdicts are as keyed (CONFLICT-FREE).
4. **Q3 is false on the sample (a finding; the key stays).** On 2 of 300 sampled records Ext is OVER-REQUIRED
   although one required order prevails over the other. In both, every action breaks the First Law, rule 19
   permits both orders, and the prevailing order is not a valid order because rule 20 counts only a lawful order.
   This is the OPEN item "rule 20 ignores the excuses of rules 9 and 19" (section 9), observed.
5. **File layout.** The repository's corpus audit (`tests/test_natural.py`) reads every `.ve` file with its own
   `.manifest.json`, and a file of additions alone cannot be a document: its first rule would be rule 14. So the
   additions are not in a file of their own. `rules.ve` holds the whole document: its first 13 lines are `base.ve`
   byte for byte, and rules 14–29 follow. `base.ve` has its own manifest, `base.manifest.json`. A test checks the
   prefix, so v2's rules stay unchanged and separate.
6. **The permission default is surfaced and measured (review finding B).** The environment, as v2's, completes
   `permitted` to allow: an action that no rule forbids may be performed. The source grants no such permission;
   it is v2's modeling choice. The check now decides every record again with `permitted` completed to deny
   (`permission_default_deny` in `results.json`), and the independent reading has the same switch. Base's clear
   set changes in 24 of the 51 records, P9 among them: its unordered actions are permitted only by the default.
   Ext's changes in none of the 51 and in 3 of the 300 sampled records, which keep a clear action. Lean and the
   reading agree on all 702 decisions. The answer key is unchanged; README OPEN states the assumption.
