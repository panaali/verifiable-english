# Verifiable English (VE): roadmap

The single entry point for status, queue, future phases and paused work.
Updated 2026-09-22 late (UTC). Study specs are linked; this file does not repeat them.
Live state between updates: `~/code/manage-agents/ve-run-log.md`.

## 1. Vision and core claim

- VE is a controlled subset of ordinary English with one exact meaning per sentence and a small, Lean-proved checker.
- Long term: anything someone is held to (policies, contracts, scientific claims, agent actions) is written in VE,
  drafted by an assistant and approved by its author through an unambiguous paraphrase.
- Agents state what they intend to do and prove it complies before they act (proof-carrying actions).
- Open-textured words ("harmful", "reasonable") stay judgement calls; VE makes the logic around them exact
  and isolates them as named, counted residuals ([vision note](design/vision-and-open-texture.md)).
- The checker grows with the language, but must stay small and proved.

**Current core claim.** The English surface is for human sign-off; we do not claim it helps models.
The benefit sought for model oversight comes from verifiability plus protocol:

- **Trusted verification of untrusted work:** a weak trusted checker certifies what a strong untrusted agent claims.
- **Universal and negative claims** ("u cannot access x", "no principal can ever ..."): a certificate is cheap to
  check but the work is expensive to redo ([crypto note](design/crypto-inspired-oversight.md)).
- **Resistance to pressure:** a signed checker verdict cannot be argued away ([failure modes](design/frontier-failure-modes-and-ve.md)).
- **Mandatory proof against obfuscation:** if nothing is accepted without a checked derivation from reviewed
  foundations, a Barnes-Christiano chain with a false leaf fails to certify. Limits: true claims without an
  affordable proof stay "unresolved"; foundations, formalisation faithfulness and cost remain open; statistical and
  heuristic leaves need mandatory evidence ([VEX note](design/vex-mandatory-evidence.md)).

## 2. Status snapshot (2026-09-22 late)

**Built and merged on `ve-integration`:** language core (Python, Rust, Lean reference semantics and
certificate checker); `closure@0` plus Lean-proved closure induction; `order@0` Lean stage (gated off) with
the executable countermodel check and the general profile-gate theorem; writable plain-English surface; `ve propose`
with the OEWN lexicon (72,780 entries); `ve assist` (Opus re-review found 5 certification loopholes, fix in progress);
evidence-layer maths corrected; paper v1 (rev2, mostly negative); P1, P3, iceberg and use cases.

| Result | Number | Verdict |
|---|---|---|
| E0 coverage audit | direct fit FOLIO 26/30, Cedar 15/30, Gatekeeper 7/30 whole-template, FRET 0/30; 77 disputed items | measurement; policy text needs extensions |
| E1 VE vs FOL sign-off (Qwen 32B) | false approval 0.293 vs 0.296 | no benefit |
| E4 checked countermodel vs prose (14B) | false approval -0.117 post hoc; checked arm shows the answer | uptake only, not comprehension |
| P1 deference | forged checker line +59pp error vs countermodel; styling +14pp; authentic vs forged-correct -3pp | harm found; signed verdicts adopted |
| P2 natural flaws | invalid steps 35% of 228 flaws | a checker addresses about a third |
| P3 formalisation tax (40 real policies) | faithful 40/40 after repair; 1.47x tokens, 4.3x time; universal properties 6/12 certified | no benefit on per-request questions; benefit only on universal ones |
| V4 fidelity + D pilot | fidelity 87%; judges near ceiling; 0/24 dishonest-consultant wins; Haiku approved 4/24 mistranslated claims | no benefit; 2-15x judge thinking |
| T1 gate (1,500 grants, Opus) | false approval 2/30 | ceiling; full study not run |
| T1b gate (5,000 grants) | Opus 1/30; Haiku FA 6/30 but honest approval 6/30 | headroom only for weak monitor; folded into T1c |
| P5 shifting definitions | VE authoring 0/12 (surface) and 0/12 (JSON schema) | infeasible one-shot; scored run not bought |
| Statement-faithfulness gate | witnesses for 4/33 unfaithful statements (12%) | stopped (under 30%) |
| Iceberg (Barnes-Christiano) | Lean root proof, 15 min, ~2M input tokens | mandatory proof is cheap here; model review is the residual |
| Math mini-paper | 15/19 certified (Python and Lean); 25/25 necessity countermodels | works; gaps listed in section 5 |
| Pushback replication (ToxiGen, L1) | 14/43 flips = 0.33 vs published 0.27 | our pressure matches theirs |
| Pushback L1 on V4 logic items | 0/23 flips | formal items resist simple pushback; L6 gate decides power |

## 3. Wrap-up state (2026-09-23, lead asked to stop starting new work)

The four agents below were left to finish; nothing else was launched. Each item lists its next step.

| Work | Branch / worktree | Where it is | Next step |
|---|---|---|---|
| A: T1d v4 | `opus/t1d`, `~/code/ve-opus-t1d` (8a7cba5; see `experiments/T1d/STATUS.md`) | DONE: generator leak fixes (degree profile, granters), full-entity directory, items 170-195 kB so they fit Haiku, 2,000-permutation audit, NI fix, harness and analysis; 61 tests. The fresh-seed leakage audit HUNG (likely fork-after-threads; fix: use spawn) and was killed, so there is no result; fresh seeds untouched | fix spawn and rerun the fresh-seed audit once; rerun power (shared raw rate); `run.py materialize` + `manifest`; rewrite PREREG from v3 to v4 with the frontier-review requirements; then Astra + Opus re-review, freeze, stamp, run |
| D: Cedar/K8s headroom gate | `opus/dgate`, `~/code/ve-opus-dgate` (6df51d7) | fixes DONE: 43 items / 29 artefacts, ground truth by SymCC and Z3, reproduced independently 3 times; single conservative gate (parsed wrong / all scheduled responses, k=3) used everywhere; OTS via the pinned opentimestamps==0.4.5; PREREG v5; full suite 1711 passed | narrow round-5 review (Astra + Opus xhigh) of 6df51d7; then `freeze`, `stamp`, `run_raw.py --execute` (subscription, $0, main account) |
| `ve assist` held-out (optional B arm) | `opus/assist-eval`, `~/code/ve-opus-assist` (b229366 plus a running fix) | dev-tune-2 done (Opus faithful 4/4 benign in every arm, no flawed item certified); round-2 reviews FIX FIRST; fix pass 2 running (anchoring both ways, no tautology steps, full graph to the auditor, checker hashed in freeze, reserve-before-attempt, auditor sandbox isolation, held-out W disclosure, one <= $0.50 dual-audit dev proxy) | round-3 review; freeze; held-out run: Opus A2 vs A3 primary, A4 uptake, Gemini secondary; Haiku dropped |
| B: T1e build | `opus/t1e`, `~/code/ve-opus-t1e` (909fd58) | DONE, offline: generator, 3 arms (VE, script, Datalog with a small trusted engine), symmetric mutations; 51 tests; fresh-seed leakage audit passes for the 4 count-preserving families, the 3 count-changing families leak and are excluded; power needs 120+120 items (720 authoring sessions, 1,920 decisions); open questions Q1-Q9 in the draft PREREG | Astra + Opus xhigh review of `experiments/T1e/PREREG-T1e.md` (decide Q1-Q9, especially budget and accounts); then the authoring gate |

Blocked on the lead: the saeedi.danial OAuth token was revoked (re-login needed). Pushing the new branches needs the lead's go-ahead.
Note: an assist-eval subagent pushed `opus/assist-eval` to origin without being asked (main untouched).

## 4. Queue (priority order; adopted 2026-09-23 from [PLAN-FRONTIER](PLAN-FRONTIER.md) section 7)

Frontier claims are protocol effects; language expansion alone is not expected to show a frontier benefit.

| # | Study | Spec | Gate / refuted if |
|---|---|---|---|
| A | T1d: robust T1c (fresh subjects, leakage audit, high effort secondary) | [PLAN-T1D](PLAN-T1D.md) Part 1 | lower FA and honest completion NI at 10pp; harm or NI failure refutes; non-rejection inconclusive |
| D | Cedar/K8s universal-property headroom gate (29 artefacts, clustered) | [PLAN-FRONTIER](PLAN-FRONTIER.md) | items, ground truth and reference verifier fixed before spend; raw error < 15% closes this sample |
| B | T1e: untrusted agent's own verification (VE vs script vs Datalog), same semantic mutation in every arm | [PLAN-FRONTIER](PLAN-FRONTIER.md) | authoring gate: audited held-out fidelity >= 80%; refuted if CI excludes a 10pp gain |
| - | `ve assist` held-out evaluation (optional B arm) | [PLAN-ASSIST](PLAN-ASSIST.md) | replays + certified + blind fidelity audit |
| C | Persuasion/injection vs the bridge (replaces the pushback study as specified) | [PLAN-FRONTIER](PLAN-FRONTIER.md) | after B; items correct in both arms; eligible-item gate |
| - | Obfuscation class F: G0/G1 diagnostics only | [PLAN-OBFUSCATION](PLAN-OBFUSCATION.md) | diagnostics, no comparative claims |
| - | Language track (parallel, off critical path): numbers round 2, English-surface proof | [PLAN-EXPAND](PLAN-EXPAND.md) | tests green; Lean soundness; cross-family review |
| - | Paper rev3 (Astra) | `paper/` | after A |
| - | Grant | `~/code/manage-agents/grants/` | paused: the lead will ask when needed |

Every study: plan reviewed by two frontier models (Astra xhigh + Opus xhigh; Opus substitutes while Codex is out)
before spend; preregistered and timestamped; baselines; pilots capped at $40.

## 5. Future phases and backlog (folded from FUTURE.md)

| Phase | What | Trigger |
|---|---|---|
| VEX evidence layer | statistical/approximate leaves carry data + test, recomputed; union/Frechet bounds; no unsupported independence ([design](design/evidence-layer-design.md)) | class S of the obfuscation study |
| Proof-carrying actions | agent names the exact tool call plus a VE proof of compliance; ControlArena-style settings vs frontier monitors | signal in pushback or T1c |
| Policy-grade extensions | numbers (in progress), strings/regex adapters, attributes, sets, obligations with exceptions and priorities (borrow from Catala), attribution, attitudes | same; E0 need: numbers 45/210, closure 27, strings 20 |
| Lean statement layer for mathematics | VE renders Lean theorem statements for sign-off; proofs stay in Lean; gaps: lemma citation, arity > 2, functions, relation parameters | after round 2 |
| Language usability | IDE loop (assistant drafts, author approves), fluent input with legal-style sub-clauses, linter precision pass, sense-bound vocabulary | ongoing |
| Protocol ideas | `meaning_id` commitments before cross-examination; security-game reporting; amplified sampled fidelity checks; append-only verdict log | as arms in existing studies |
| Human studies | E1/E5 packages; "valid proof of the wrong model" study from the formal-proof handoff | deferred by the lead |
| Grant-scale runs | 5,000-step sizes, size scaling, requirement retention under compaction (S1), multi-agent hand-off, adaptive attackers, judge ladders, RL with checked rewards (GPUs later) | grant (~$20K) |

## 6. Paused or dropped

| Item | Why |
|---|---|
| Pushback study as specified ([PLAN-PUSHBACK](PLAN-PUSHBACK.md)) | L1 0/23, L6 0/24 flips on formal items; redesigned as claim C |
| Mixed-property audit | verdicts would show parity; may return as a cost/reuse audit |
| P5 scored run | VE authoring infeasible one-shot (0/12 twice); revisit via `ve assist` |
| T1b full study | ~14,000 serial calls; question folded into T1c; Opus safeguard refused sabotaged code (now programmatic mutation) |
| Independent-formaliser pilot ([PLAN-IF](PLAN-IF.md)) | BBM items are ordering puzzles; checker = answer key; only the no-VE headroom check remains queued |
| Statement-faithfulness witnesses ([PLAN-SF](PLAN-SF.md)) | 12% witness yield < 30% gate; most unfaithful statements are true but weaker |
| Long-context qa15 | strawman (1-2 hops; the checker never sees the context) |
| `claude/open-judges`, Codex open-judge ladder | superseded harness; tagged `archive/open-judges-fcd378c` |
| T4 universal-invariant pilot ([PLAN-T4](PLAN-T4.md)) | closure induction built; pilot replaced by T1c |

## 7. Where things live

| What | Where |
|---|---|
| Integration branch | `~/code/ve-integration` (`ve-integration`, pushed to `git@github.com:panaali/verifiable-english.git`; `main` untouched) |
| Work branches | one worktree per agent under `~/code/` (`git worktree list`), e.g. `ve-opus-numbers`, `ve-opus-pushback`, `ve-opus-t4`, `ve-opus-assist`, `ve-codex-v4` (V4/T1/T1b results) |
| Run log (live state) | `~/code/manage-agents/ve-run-log.md` |
| Plan and paper reviews, literature checks | `~/code/manage-agents/reviews/` |
| Lead's rules | `~/code/manage-agents/LEAD-PREFERENCES.md` |
| Accounts and usage | main, `~/.claude-danielsaeedi37`, `~/.claude-saeedi.danial`; check with `~/code/manage-agents/claude-usage.sh`; one account per arm |
| Keys | `~/code/manage-agents/.env` (never print or commit) |
| Preregistrations and corrections | `experiments/*/PREREG*.md`, `experiments/PREREG-HASHES.txt`, `experiments/CORRECTIONS.md` |

### Plan files

| File | Status |
|---|---|
| [PLAN-PUSHBACK](PLAN-PUSHBACK.md), [PLAN-V5-DEMO](PLAN-V5-DEMO.md), [PLAN-ASSIST](PLAN-ASSIST.md), [PLAN-EXPAND](PLAN-EXPAND.md), [PLAN-OBFUSCATION](PLAN-OBFUSCATION.md) | active specs; "After review" sections are binding |
| [PLAN](PLAN.md), [PLAN-V2](PLAN-V2.md), [PLAN-V3](PLAN-V3.md), [PLAN-V4](PLAN-V4.md) | historical (superseded in turn; V3's queue update is now section 4) |
| [PLAN-T4](PLAN-T4.md), [PLAN-IF](PLAN-IF.md), [PLAN-SF](PLAN-SF.md) | historical (replaced by T1c or stopped) |
| [FUTURE.md](FUTURE.md) | pointer to this file |

## How to maintain

- Update this file whenever status, the queue or a decision changes; append details to the run log.
- One spec per study; its "After review" section is binding; specs never carry status.
- When a spec is superseded, mark it with a one-line banner and list it as historical above.
- Never duplicate status, results or the backlog in spec files or FUTURE.md.
