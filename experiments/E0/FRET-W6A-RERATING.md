# FRET sample re-rated for W6a (2026-09-28)

PLAN-EXPAND2 W6 acceptance (2): "the 30 sampled items re-rated with
time-indexed relations over a user time sort; items needing integer time or
real values stay NO and are said to."

**Method.** The same 30 items as E0 (`survey_samples/fret.jsonl`, drawn with
`random.Random(20260921)`), the same a/b/c/d classes ([SURVEY.md](SURVEY.md)),
re-read against what W6a admits: a user sort `tick`, time-indexed unary and
binary relations over it, supplied `next`/`before` relations, ground scaled
decimals and dates, and user-sort counting up to the 8/7/7 caps. Integer
quantification, integer-time relations and real values are not W6a (numbers2
and W4 stage 2). **Exploratory, single rater:** like E0, one model reader (the
W6a worker, Claude Opus 5.5, in-session; no model API call) with no second
rater, so shares carry roughly ±15-18 points of sampling error. Per-item record:
[`survey_samples/fret-w6a.jsonl`](survey_samples/fret-w6a.jsonl); integrity and
the mechanical claim are tested in `tests/test_fret_w6a_rerating.py`.

| Rating | a | b | c | d |
|---|---|---|---|---|
| E0 (2026-09-21) | 0 | 8 (27%) | 18 (60%) | 4 (13%) |
| W6a (this re-rating) | 0 | 10 (33%) | 16 (53%) | 4 (13%) |

**What moved.** Items 20 and 26 ("within 16 ticks", "within 13 ticks") move
from c to b: over a user tick sort with a supplied one-tick successor, a
bounded response is a finite unrolling, 16 steps at formula depth 51 of the
64 budget. Lean's `ve_quantity` admits and evaluates the expansion (true when
the property holds at tick 0 or tick N, false at N+1). The unrolling is
faithful only if `next` is the functional successor on discrete ticks; that is
an assumption leaf, not something the checker establishes.

**What did not move, and why.** Sixteen items compare a numeric signal's value
at each tick with a constant or another signal (`kias >= 0.0`,
`vehAirPress < warningTrigForMinPress`). The constants are exactly
representable as W6a scaled decimals, but the signal's value at a tick is not a
ground quantity. Binding it (`∀t ∀v. kias(t, v) → 0 ≤ v`) needs an integer
binder, which is **gated on numbers2**. Real arithmetic (`absReal`, products,
`preReal`) and metric seconds ("for 200 secs") are not W6a either, and neither
is a persistence window of 100 ticks, which exceeds the depth budget when
unrolled (item 8). The four d items (trigonometric or pure arithmetic
equations) stay d. Items that need integer time or real values therefore stay
c/d, as the plan requires. The b items remain b: time-point reification over the
user sort is still a reification, not a direct fit.

| # | E0 | W6a | Requirement (shortened) | Reason |
|---|---|---|---|---|
| 1 | b | b | FSM_Autopilot shall always satisfy (state = ap_maneuver_state & standb… | always -> forall over a user tick sort; enum states as entities with equality; boolean signals as unary relations over tick |
| 2 | b | b | when emergency_button the liquid_mixer shall immediately satisfy ! val… | when/immediately -> tick sort with a supplied successor relation next(tick,tick); boolean signals unary over tick |
| 3 | c | c | Euler shall always satisfy c1xc1Transpose = 1.0 & c2xc2Transpose = 1.0… | real-valued matrix-product signals equal to 1.0; the compared value is a time-indexed numeric signal; W6a has ground scaled decimals only, so binding the signal's value at each tick needs the numbers2 integer binder (or real values); the constant itself is exactly representable |
| 4 | c | c | whenever (autopilot_engaged & !hdg) & preBool(false, roll_angle - roll… | real arithmetic (absReal, differences, preReal) over signals; the compared value is a time-indexed numeric signal; W6a has ground scaled decimals only, so binding the signal's value at each tick needs the numbers2 integer binder (or real values); the constant itself is exactly representable |
| 5 | b | b | when emergency_button the liquid_mixer shall immediately satisfy ! sti… | tick sort with successor; boolean signals |
| 6 | d | d | Euler shall always satisfy DCM321_21 = (- cos(phi) * sin(psi) + sin(ph… | trigonometric arithmetic equation over real signals; no W6a counterpart |
| 7 | c | c | SWIM shall always satisfy ((lowSpeedWarningAllowed = 1.0 & vehAirPress… | vehAirPress < warningTrigForMinPress compares two numeric signals at a tick; the compared value is a time-indexed numeric signal; W6a has ground scaled decimals only, so binding the signal's value at each tick needs the numbers2 integer binder (or real values); the constant itself is exactly representable |
| 8 | c | c | Regulator shall never satisfy persisted(100,hcvdt_cmd_fcs_fps2 > 32.0) | persisted(100, x > 32.0): 100-tick persistence could unroll over the successor relation, but 100 steps exceed the depth budget (64) and x > 32.0 is the compared value is a time-indexed numeric signal |
| 9 | b | b | FSM shall always satisfy (senstate = sen_nominal_state & !request) => … | tick sort; enum state equality; boolean signals |
| 10 | c | c | NN shall for 200 secs satisfy ( x = xt & y = yt => absReal(zt - z) <= … | 'for 200 secs' is metric time (seconds, not ticks) plus absReal; the compared value is a time-indexed numeric signal; W6a has ground scaled decimals only, so binding the signal's value at each tick needs the numbers2 integer binder (or real values); the constant itself is exactly representable |
| 11 | c | c | NN shall for 200 secs satisfy DeltaZDividedByYt <= 10.0 & DeltaZDivide… | 'for 200 secs' metric time plus numeric bounds on a signal; the compared value is a time-indexed numeric signal; W6a has ground scaled decimals only, so binding the signal's value at each tick needs the numbers2 integer binder (or real values); the constant itself is exactly representable |
| 12 | c | c | RollAutopilot shall always satisfy (TurnKnob >= 3.0 \| TurnKnob <= -3.0… | numeric comparisons of TurnKnob at each tick; the compared value is a time-indexed numeric signal; W6a has ground scaled decimals only, so binding the signal's value at each tick needs the numbers2 integer binder (or real values); the constant itself is exactly representable |
| 13 | c | c | Regulator shall always satisfy pitch_command_acceleration <= 50.0 | pitch_command_acceleration <= 50.0 at each tick; the compared value is a time-indexed numeric signal; W6a has ground scaled decimals only, so binding the signal's value at each tick needs the numbers2 integer binder (or real values); the constant itself is exactly representable |
| 14 | d | d | NLGuidance shall always satisfy Vv * yout > 0 | product of two real signals compared with 0: pure arithmetic |
| 15 | c | c | in roll_hold mode RollAutopilot shall immediately satisfy (-30.0 >= ro… | comparison and multiplication by sign_roll_angle; the compared value is a time-indexed numeric signal; W6a has ground scaled decimals only, so binding the signal's value at each tick needs the numbers2 integer binder (or real values); the constant itself is exactly representable |
| 16 | c | c | TriplexSignalMonitor shall always satisfy (single_fail_reported & (((!… | absReal differences against a threshold signal; the compared value is a time-indexed numeric signal; W6a has ground scaled decimals only, so binding the signal's value at each tick needs the numbers2 integer binder (or real values); the constant itself is exactly representable |
| 17 | b | b | The vehicle shall always satisfy rearprop xor hover_control_mode | always (p xor q): tick sort, unary signals |
| 18 | c | c | Euler shall always satisfy DCMxDCMTranspose_11 = 1.0 & DCMxDCMTranspos… | real equalities produced by matrix arithmetic; the compared value is a time-indexed numeric signal; W6a has ground scaled decimals only, so binding the signal's value at each tick needs the numbers2 integer binder (or real values); the constant itself is exactly representable |
| 19 | b | b | when timer_60sec_expire, the liquid_mixer shall until (timer_120sec_ex… | until: supplied order relation before(tick,tick) on the tick sort; boolean signals |
| 20 | c | b | The vehicle shall within 16 ticks satisfy lift_mode = thrust_borne | was c. 'within 16 ticks' unrolls to 16 nested steps over a supplied successor relation next(tick,tick) on the user tick sort (depth 51 of 64); Lean admits the expansion (tests/test_fret_w6a_rerating.py). Faithful only with next as the functional one-tick successor, an assumption leaf |
| 21 | c | c | The vehicle shall always satisfy kias >= 0.0 | kias >= 0.0 at each tick; the compared value is a time-indexed numeric signal; W6a has ground scaled decimals only, so binding the signal's value at each tick needs the numbers2 integer binder (or real values); the constant itself is exactly representable |
| 22 | c | c | Upon lift_mode = wing_borne & kias > 90.0 the vehicle shall until lift… | kias > 90.0 in trigger and stop conditions; the compared value is a time-indexed numeric signal; W6a has ground scaled decimals only, so binding the signal's value at each tick needs the numbers2 integer binder (or real values); the constant itself is exactly representable |
| 23 | d | d | Tustin_Integrator shall always satisfy normalv3 => yout = timeStep * 0… | arithmetic equation (Tustin integrator) |
| 24 | c | c | The vehicle shall always satisfy FTP \| absReal(preReal(0.0,wind_speed)… | absReal/preReal arithmetic; the compared value is a time-indexed numeric signal; W6a has ground scaled decimals only, so binding the signal's value at each tick needs the numbers2 integer binder (or real values); the constant itself is exactly representable |
| 25 | c | c | The vehicle shall always satisfy if preBool(false, fcs & kias >= 30.0)… | kias >= 30.0 inside preBool; the compared value is a time-indexed numeric signal; W6a has ground scaled decimals only, so binding the signal's value at each tick needs the numbers2 integer binder (or real values); the constant itself is exactly representable |
| 26 | c | b | The vehicle shall within 13 ticks satisfy lift_mode = thrust_borne | was c. 'within 13 ticks': the same successor unrolling as item 20, 13 steps (depth 42 of 64) |
| 27 | c | c | Upon lift_mode = semi_thrust_borne & kias <= 40.0 & (!hover_control_mo… | numeric comparisons on kias and kgs; the compared value is a time-indexed numeric signal; W6a has ground scaled decimals only, so binding the signal's value at each tick needs the numbers2 integer binder (or real values); the constant itself is exactly representable |
| 28 | b | b | The vehicle shall always satisfy kias = kgs | kias = kgs: equality of two signals' values at each tick, values as entities of a value sort (no order used) |
| 29 | d | d | Euler shall always satisfy DCM321_11 = cos(theta) * cos(psi) | trigonometric arithmetic equation |
| 30 | b | b | when emergency_button, the liquid_mixer shall immediately satisfy ! va… | tick sort with successor; boolean signals |
