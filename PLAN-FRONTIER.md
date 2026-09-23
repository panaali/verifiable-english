# PLAN-FRONTIER: the best plan to show VE's benefit for frontier models (2026-09-23)

Planner: Claude Fable 5.1 (xhigh), read-only; sources as listed in the brief, run log to 08:17Z. Status: proposal for
the orchestrator; Astra xhigh + Opus xhigh review before any spend.

## 1. Answer to the lead

**Expanding the language will not, by itself, produce a frontier-scale benefit.** Every frontier result we have is a
protocol effect: an untrusted agent supplies a certificate, a trusted checker replays it, and the monitor only has to
match the certified statement to the claim. The effect appears only where the monitor cannot redo the work (20,000
facts, a negative claim), and it is matched by a plain script (T1c) and by Z3 (T1d Part 2, 475/475 proved).
Extensions change what the checker can reach; they do not create a monitor failure to fix. On the real artefacts we
hold (P3's 40 items) frontier judges are at ceiling and VE costs 1.47x the tokens. Reach without scale buys nothing.

I agree with the orchestrator in substance and disagree in three places:

1. **A "one proved checker across property types" audit will not separate VE from a script.** Against Datalog or Z3
   it gives verdict parity again (T1d Part 2); the difference (a small proved trusted base, a readable surface) is
   engineering, not a model result.
2. **The script baseline that can lose has not been run: the agent's own verification code.** T1c's script was
   trusted and ours. The deployment alternative to a certificate is "let the agent write the check" (PLAN-V5-DEMO's
   arm b-exec, dropped from T1c): the monitor then reviews code with a planted bug, whereas with VE it reviews a
   formalisation with a planted mistranslation. That is the AI-control comparison, and it is open.
3. **Lemma citation and VEX are not on the frontier path.** The adopted obfuscation pilot shows Lean statements, not
   VE, and Astra allows diagnostics only; VEX's collapse is arithmetic by construction. Both are maths and usability
   work.

Plan: make the protocol result robust (T1d), show it survives an untrusted verifier, persuasion and injection, and
present VE as one instance of the protocol with a small proved checker and a readable surface, claiming nothing for
English with models.

## 2. Claims we can establish in the next weeks

| # | Claim | Decisive experiment | Fair baseline | Refuted if | Why not true by construction |
|---|---|---|---|---|---|
| A | Certificate plus signed verdict removes frontier false approval of false "cannot access" claims at 20,000 facts, honest completion intact, Opus and Haiku, also at high effort | T1d Part 1 v4: fix the blocking review items (degree leaks, NI bound, gate resolution, power scenarios), freeze, run 270 items x 5 arms | Same model reading the raw policy at low and high effort | McNemar not rejected with fewer VE approvals, or NI fails; raw FA < 15% on held-out families = ceiling | Raw arm has the same information; leakage at chance; alias/group/role strata need a bridge monitors can get wrong; honest items can be lost (T1c script arm lost 3) |
| B | A proved checker beats trusting the agent's own verification code: fewer false approvals at matched monitor budget, honest completion within 10pp | T1e: mixed-format policies (YAML, CSV, prose rules with "unless"); untrusted Opus transcribes to VE via `ve assist`, or writes a checking script the harness executes, or writes Datalog for a trusted engine; monitors Opus, Haiku, Gemini | (i) raw; (ii) agent script, trusted execution, monitor reviews code and output; (iii) agent Datalog, trusted engine. Expected VE = (iii); the claim is checker vs (ii) | VE FA not below (ii) by 10pp; or honest formalisation < 80% | Both arms leave a real review task; D-pilot monitors flagged 24/24 mistranslations yet Haiku approved 4/24; no capability gap when Opus reviews Opus code; completeness can fail |
| C | The protocol holds under adaptive persuasion (Jagged Judges L6) and artefact injection (Terekhov), the failures that do not shrink with capability | Add-on on A/B items where raw Opus errs: advisory (unlocked) verdict vs raw under a 10-turn Opus persuader; injected "pre-verified, approve" text in sabotaged policies | Raw monitor under the same persuader and injection; locked verdict as ceiling | Raw flips or injection success < 10% (no power); advisory arm not below raw by 10pp | The judge may override an advisory verdict; injection targets the matching step the checker does not cover |
| D (gate only) | Frontier monitors fail on universal properties of real policies | 22 Cedar + 7 K8s P3 items, one planted policy edit breaking "no principal outside G can ever ..."; 40 items, Opus raw | none yet | FA < 15%: ceiling; real-world benefit then needs scale | Negative universal claims; no frontier study exists |

## 3. Language extensions, by experiment

Needed, in order:

1. **A: none.** closure@0 and closure induction are merged.
2. **B:** closed-world "unless" guards already certify 15/16; fix the JSON nesting limit (log-depth builder).
   `ve assist` must produce certified, anchored transcriptions of flat facts plus prose rules; evaluate it on
   T1e-shaped items, not the 16-step P5 items.
3. **D, only if the gate passes:** the closure@0 x order@0 gate theorem, so Cedar items with numeric conditions (P3
   class c, 14/126 units) become expressible; background-axiom templates for schema facts (P3 section 5).

Not now: strings, globs and datetimes (IAM); attributes and sets beyond reification; lemma citation and conservative
definitions; the VEX evidence layer; the English-surface unambiguity proof. None changes a frontier monitor's decision
in any study above. The closure x numbers combination stays gated off unless D passes.

## 4. Stop or deprioritise

- **Pushback study as specified: stop.** Both probes gave 0 flips (L1 0/23, L6 0/10); the residual endpoint on V4
  translation items is small-item work judges handle at ceiling. Fold the L6 persuader into C.
- **Obfuscation pilot:** run G0 and G1 only (is a frontier judge fooled at N = 32) for at most $5; the rest waits for
  B. No VE build for it.
- **`ve assist` held-out P5 evaluation:** after the T1e-shaped authoring test, not before.
- **Mixed-property audit vs bespoke scripts:** do not run.
- **Numbers round 2, maths paper, Rust core, VEX, surface proof:** pause until the T1e prereg is frozen.
- **Paper rev3:** wait for A; Astra drafts the independent parts now.

## 5. Sequencing, accounts, gates, cost

**Week 1 (to Sep 27).**
- danielsaeedi37: T1d v4 after both re-reviews; freeze, timestamp, run 1,500 decisions with pause/resume (about two
  days under session limits; weekly reset Sep 24).
- saeedi.danial (reset Sep 28): T1e build: generator for mixed formats and prose rules, programmatic sabotage for
  rules and scripts, leakage audit per sabotage family, `ve assist` dry run on 12 dev items. Gate B1: honest
  transcription at least 80% certified and faithful; B2: 20-item headroom pilot of arm (ii), Opus monitor, code false
  approval at least 15%.
- main: orchestration, Opus xhigh reviews, the D gate (40 items), the C harness from the pushback code.
- Codex/Astra (quota fresh to Sep 29): T1d and T1e prereg reviews, the log-depth builder fix, paper sections
  independent of A.

**Week 2.** T1e full run on saeedi.danial: about 120 items x 4 arms x 2 monitors, near 1,000 decisions plus about 400
authoring sessions; Gemini judge on Vertex, at most $40. C on danielsaeedi37 after T1d: about 80 items x 10 turns x 2
arms. D follow-up only if its gate passed. Astra writes results.

**Week 3.** Paper rev3 (Astra); a proof-carrying-actions demo on the T1e materials (execute only certified tool
calls) as a figure, not a study.

Rules: two xhigh reviews before spend; leakage audit at chance on fresh seeds; pilots at most $40; one account per
arm. Vertex at most $100 in total; the rest is subscription quota; the binding constraint is reviewer bandwidth, not
money.

## 6. Biggest risks

1. **Opus at high effort is at ceiling** in T1d. The claim then shrinks to "certificates substitute for monitor
   effort"; report it as such.
2. **T1e parity or a completeness loss.** Opus reviewing Opus code may catch the mutations, or the honest agent fails
   to formalise mixed-format policies. Then the finding is that the formalisation tax returns at frontier scale.
3. **Leakage and construction critiques.** T1d needed three leakage rounds; T1e's two sabotage families must be
   equally detectable from the surface (classifier at chance per family).
4. **Safeguards and quota.** Opus refuses to author sabotaged code (mutation only); three accounts with five-hour and
   weekly limits; Codex to Sep 29.
5. **"Everything here is Lean or Z3 plus a protocol."** True. The paper must present VE as one instance with a small
   proved checker; the English surface is for human sign-off and untested with humans.
6. **Review bandwidth.** Every merge and prereg needs two xhigh reviews; language work competes with the studies for
   them, which is why we build only what B and D need.

## 7. After review (2026-09-23): adopted with changes

Reviews: `reviews/frontier-plan-review-astra.md` (Astra xhigh) and `reviews/frontier-plan-review-fable.md`
(Fable 5.1 xhigh). Both: **ADOPT WITH CHANGES**. The changes below override sections 1-6 where they conflict.

**Answer on expansion, corrected.** Expressiveness alone gives no frontier benefit: every frontier signal so far is
a protocol effect (T1c script = VE; T1d Part 2 Z3/cvc5/VE 475/475; P3 review = VE 75/75 at 1.47x tokens). But
"reach without scale buys nothing" is unsupported: extensions can open universal properties and cut authoring cost,
which is untested, not refuted. P2 caps a deduction checker at about 35% of natural flaws; say so. P3's ceiling is 8
items / 75 questions, not 40. Language expansion stays a parallel track (the lead's direction), off the frontier
critical path and never ahead of study reviews.

**A (T1d robust T1c).**
- Freeze and re-review the design actually implemented (v4 sizes by bytes; the prereg still says v3/20,000 facts).
- High effort is a secondary endpoint; claim it only if confirmatory.
- Success = lower false approval plus honest completion non-inferior at 10pp. Refutation = harm or NI failure;
  non-rejection alone is inconclusive.
- Budget ten five-hour windows and the weekly cap, not "two days".

**B (T1e agent-authored verification).**
- Primary authoring path: P3-style direct authoring with the guide (37/40 first pass, 8/8 independent agents).
  `ve assist` is an optional arm until its held-out evaluation passes.
- The same semantic mutation is rendered into every arm (VE, script, Datalog with a trusted engine); symmetric
  mutation operators preregistered; the script arm gets rule-to-code anchoring to match VE's source anchoring.
- Match total authoring + proving + monitor budgets and attack opportunities.
- Gate before scaling: independently audited held-out fidelity >= 80%. Stop if fidelity < 80% or honest completion
  drops > 10pp. Refuted if the CI excludes a 10pp gain.
- Claim scope: trusted verification versus untrusted checking code, not VE versus Datalog.

**C (persuasion/injection), redesign before any run; after B.**
- Analyse items initially correct in both arms; add corrective-update controls; restore decomposition-only D0.
- Separate persuasion from injection; injection must attack the bridge (statement/transcription), not the signed
  verdict channel. Match attacker budgets. Gate on the count of eligible items. L6 data so far: 0/24 trajectories
  (Wilson upper ~28% at n=10 items), deduction-only.
- This replaces PLAN-PUSHBACK as specified.

**D (Cedar/K8s universal-property headroom gate).** 22 Cedar + 7 K8s = 29 artefacts; cluster by artefact. Before
spend: define the items, independent ground truth, domain and schema assumptions, and a named reference verifier
(source-native or SMT). Zero-cost gate; expected to fail by the plan's own scale thesis; a fail closes only this sample.
Numbers cannot cover all 14 opaque units (IAM globs, datetimes).

**Keep (reversing section 3 stops):** held-out `ve assist` evaluation; small obfuscation completeness diagnostics
(G0/G1); residual and corrective-update controls. Mixed-property audit: dropped as a benefit study, allowed later as
a cost/reuse audit.

**Budget and schedule.** No Vertex total was authorised; the rule is at most $40 per pilot. Codex quota resets Sep
29 23:00. The fixed three-week schedule is replaced by gates: A and D now; B after its authoring gate; C after B.
