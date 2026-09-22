# P3 report: formalisation tax on real artefacts

Date 2026-09-22. Author of the main formalisations: Claude Opus 5.5, acting as the
untrusted model author. Numbers come from [results.json](results.json); the method is
in [README.md](README.md). No paid API calls were made.

## Bottom line

* **Faithfulness is not the problem.** For 40 real artefacts (22 Cedar policy
  sets, 7 Kubernetes RBAC configurations, 3 AWS IAM policies, 8 Alloy paragraphs), my
  first-pass VE agreed with an independent source-language reference on every item
  question and on 300 perturbed worlds per item in **39/40** cases, and in 40/40
  after one repair that the differential test prompted. Eight fresh agents, given
  only [AUTHORING_GUIDE.md](AUTHORING_GUIDE.md), wrote faithful VE on the first pass
  for **8/8** of the items they authored. Their versions and mine never disagreed on
  2,000 extra perturbed worlds per item. PLAN-V3's faithfulness clause (below about 30%)
  is far from triggered.
* **Cost is the problem.** Paired on 8 items with the same model and the same
  accounting, VE authoring cost **1.47× the tokens and 4.3× the wall-clock** of a
  complete structured review that answered the same 10 questions per item. The review
  was **75/75 correct**. On per-request authorization questions, VE therefore saved
  no review at all: accuracy was already at ceiling. Someone would still have to sign
  off the formalisation, which for the Cedar and Alloy items is 0.5–2.3× the length of the source. **PLAN-V3's
  cost clause is met: P3's refutation condition holds** for this question type.
* VE bought something the review did not only on **universal properties**. There it
  gave certified answers (a replayed tableau certificate or a finite countermodel)
  in 6 of 12 property tasks. That took hand-written background axioms in one case,
  and in 4 tasks it hit checker limits. P3 did not cost this regime against review.
  If the thesis survives, it survives there.

## 1. Items and ground truth

40 items, 221 questions (table in README). All policy, model and YAML text is
verbatim from pinned public repositories. The synthetic parts are labelled in each
`item.json`: K8s and IAM requests, some K8s bindings, the admin/edit/view
aggregation skeleton, and the Alloy instances. The Cedar reference reproduces all
**115/115** decisions recorded by the real Cedar authorizer in the upstream fixtures.
The K8s, IAM and Alloy references have unit tests and hand-checked answers.

## 2. Faithful-formalisation rate

| Author | Items | Faithful on item questions + 300 perturbations |
|---|---:|---:|
| Me, first pass (frozen in `items/*/first_pass/`) | 40 | 39/40 |
| Me, after differential feedback | 40 | 40/40 |
| Independent agents (first pass, no reference access) | 8 | 8/8 |

The single first-pass failure was **c15 (hotel_chains)**. A perturbation put a string
into a set used with `in`. Cedar raises a type error and skips the policy; my formula
fell through to the next `||` disjunct. Two of the independent agents had modelled
exactly this rule. Inspection then found the same latent bug in c17, which the test
had not exposed; both were repaired (`authoring_log.jsonl`). Separately, 6 items
need OPAQUE adapter predicates, so only **34/40** are faithful *in pure VE* (see §3).

**How much "faithful" means.** An all-green differential test is only as good as its
power, which I measured two ways.
* *Mutation analysis* (`mutation_results.json`): 813 mutants over the 40 items. The differential test killed **539 (66%)**; the item's own questions alone killed 406 (50%). Of the 274 survivors, VE's prover showed 6 equivalent to the original. For 59, a small finite VE structure distinguishes them, but it may be unrealisable in the source language (e.g. aliased constants). 209 are unclassified within budget. Kill rates are lowest for the reused K8s and IAM authorizer formulas (w01: 3/25), whose clauses the item worlds never exercise.
* *Hand-written realistic mistranslations* (`naive_results.json`): 14 variants such as
  ignoring Cedar error semantics, reading `action in [..]` as `==`, one-level ClusterRole
  aggregation, or IAM's missing-key rule for negated operators. The test caught
  **11/14** at 300 perturbations; the item's own questions alone caught only **4/14**.
  Of the three misses, one (`l05` swapped closure direction) VE *proved* equivalent.
  One (`l08` `^` as `*`) is equivalent on instances whose signatures are disjoint. One
  is a real miss: `c11` ignores error semantics. It was caught at 1,000 perturbations,
  and a Cedar hierarchy mistranslation (`c04`) was caught by only 1 of 300.
  Random-world differential testing detects plausible mistranslations, but slowly.
  A policy-aware perturbation (linking request entities to policy literals) had to
  be added after a first probe at N=60 caught only 8/14.

## 3. How much of each source VE expresses (E0-style)

126 source units (policies, RBAC objects, IAM statements, Alloy paragraphs plus the
functions they call). Classes follow `experiments/E0/SURVEY.md`:

| Family | Units | a direct | b reified | c opaque adapter | d none | Fully expressible items |
|---|---:|---:|---:|---:|---:|---:|
| Cedar | 91 | 58 | 27 | 6 | 0 | 19/22 |
| Kubernetes | 12 | 8 | 4 | 0 | 0 | 7/7 |
| IAM | 8 | 0 | 0 | 8 | 0 | 0/3 |
| Alloy | 15 | 12 | 3 | 0 | 0 | 8/8 |
| **All** | **126** | **78** | **34** | **14** | **0** | **34/40** |

112/126 units (89%) are expressible, and the closure profile did real work. Group
nesting, action groups and resource hierarchies (`rtc[parent]`) appear in most Cedar
items. ClusterRole aggregation needs a Body closure whose edge contains a universal
(label-subset) test. Alloy `^`/`*`, including closure over a ternary field with a
captured parameter (`n.^(b.addr)`), is expressed directly.
Class c is numeric comparison (c08, c12), datetime arithmetic (c19), and string
globbing with policy variables (all IAM). Known gaps are noted in `coverage.py` and
never exercised by the tests:
* Cedar record equality also requires no extra keys (c21).
* IAM `Bool` is case-insensitive (w03).
* Kubernetes has `*/subresource` forms. The independent k07 author approximated them
  by enumerating 18 subresources.

A second cost that coverage alone does not show: **Cedar's error semantics had to be
hand-encoded** (has_/bf_/type guards) in 8 of 22 Cedar items. This was the source of
the only real mistranslation, and of most naive variants the test found hardest.

## 4. Authoring cost

| | Me (40 items) | Independent agents (8) | Structured review (same 8) |
|---|---|---|---|
| Tokens per item | not measurable inside my own context; VE artefacts median ≈1.0k tokens | mean 31.1k (23.6k–38.1k) | mean 21.1k (19.6k–22.8k) |
| Wall-clock per item | 526 s in total; median 13.5 s for non-reused items (upper bound, includes running the checker) | mean 68 s (16–118 s) | mean 16 s (12–20 s) |
| Checker errors / repairs | 0 parse/type errors; 1 differential-driven repair (+1 same-class) | 11 check runs, 3 with syntax errors (all bracket nesting), 0 semantic repairs | n/a |
| Accuracy | 39/40 → 40/40 items | 8/8 items | 75/75 answers |

Both agent arms carry the same fixed prompt overhead, so their *marginal* ratio is
larger than 1.47×. Two structural points matter more than the constants:
* The K8s and IAM formalisations are **one formalisation of the authorizer**, reused
  across artefacts (k02–k07 and w02–w03 cost 0 s). Only the Cedar and Alloy items
  were written per artefact.
* The authors' formulas were often longer than the source: c17 is 2.5k characters of
  Cedar and 5.5–5.7k of VE. VE has no definitions, so the agents wrote throwaway
  generator scripts to keep the brackets balanced.

Break-even: a formalisation answers further requests at zero model cost. The review
answered 10 questions for about 21k tokens, much of it fixed overhead. VE's roughly
10k-token premium would pay back after some tens of further questions on the same
artefact. That holds only if the formalisation needs no sign-off of its own, and it
does. For executable policies, the source engine answers per-request questions
exactly at zero model cost anyway.

## 5. Prove / countermodel arm

`proof_results.json`, 12 property tasks. Every VE "proved" verdict has a
certificate that replayed; references were computed by sampling (Cedar) or by
exhaustive bounded enumeration (Alloy).

| Task | VE | Reference | |
|---|---|---|---|
| c02: allowed ⇒ principal in jane_friends | proved (2 steps) | holds | ✓ |
| c03: VacationPhoto94 is the only viewable resource | countermodel | fails | ✓ |
| c13: private doc viewable only by owner, no background axioms | countermodel (all constants aliased), prover ResourceLimit at 50k steps | holds | spurious |
| c13: same + schema axioms (distinct action UIDs, actions without parents, owner present/unique, Boolean exclusivity) | proved (146 steps) | holds | ✓ |
| c14: bob may push `secret` from a 4-edge group chain | proved (3,194 steps) | holds (recorded) | ✓ |
| k05: rule aggregated view→edit→admin reaches an admin binding | ResourceLimit (prover and countermodel) | holds | unknown |
| l03: `check NoSelfGrandpa` (grandpa1.als) | proved (83 steps) | holds (scope 3) | ✓ |
| ring ⇒ weaklyConnected (± typing) | ResourceLimit; no countermodel | holds (≤3 nodes) | unknown: needs closure monotonicity, not implemented |
| tree ⇒ weaklyConnected | countermodel (edge from a non-node atom) | holds | spurious: Alloy's `r: node->node` typing missing |
| tree ⇒ weaklyConnected + typing | ResourceLimit; no countermodel | holds (≤3 nodes) | unknown: valid only on finite graphs |
| weaklyConnected ⇒ ring | countermodel | fails | ✓ |

## 6. Failure taxonomy

1. **Inexpressible constructs**: 14/126 units in 6 items, all class c (numbers,
   datetimes, string globs), plus the unexercised semantic gaps in §3. No class d.
2. **Mistranslation caught by the differential test**: 1 of 40 first passes (c15,
   Cedar type error of `in` over a set with a non-entity member); 0 of 8 independent
   first passes. Plus the detection rates for seeded mistranslations in §2, including
   one realistic miss at N=300.
3. **Checker limits**: finite evaluation never hit ResourceLimit (40 items × 301 worlds).
   The prover hit ResourceLimit in 6 of 12 property tasks: a 15-policy formula without
   axioms, a 3-level aggregation chain, closure monotonicity (not implemented), and
   finite-only validity (no sound certificate exists). Bounded countermodel search
   hit ResourceLimit once (k05, five sorts).
4. **Background-axiom gap**: open-world countermodels are spurious unless the author
   also states what the source language guarantees: unique entity names, the schema's
   action hierarchy, functional attributes, Alloy field typing. This is 2 of 12
   property tasks, and more authoring that someone has to review.
5. **Trusted-side defects (not the author's)**. Getting the "trusted" machinery right
   took more fixes than the untrusted author needed:
   * 3 encoder bugs: string "5" vs long 5 collided; Booleans in sets were stringified;
     the `value` sort was missing in scalar-free worlds.
   * 2 item-builder bugs: duplicate schema actions; Cedar schema datetime typing, which
     the reference agent flagged.
   * 1 reference deviation from Cedar's spec: `in` over a mixed set short-circuited.
     `cedar-spec` `Evaluator.lean` `inₛ` type-checks every member first. It was found
     while diagnosing c15, fixed, and unit-tested; no recorded decision exercises it.

## 7. Refutation condition

PLAN-V3, package 3: *refuted if faithful formalisation is below about 30%, or
authoring costs more than the review it saves.*

* Faithfulness: 39/40 first pass (40/40 after one test-driven repair), and 8/8 for
  independent authors. This clause is **not met**, with the caveat that the test
  catches about 11/14 realistic mistranslations at the budget used.
* Cost: VE authoring cost more than the complete review (1.47× tokens, 4.3× time).
  The review was already 100% accurate, and it saved nothing. This clause is **met**.

**Outcome: the refutation condition holds for per-request authorization and
constraint questions on real RBAC and Alloy artefacts.** Following the plan, the
"tolerable usefulness tax" claim cannot rest on these items. The live possibility is
certified universal properties (§5). There VE answered questions review can only
argue about, but needed reviewed background axioms, and its prover stopped at
closure monotonicity and multi-level aggregation. A package that costs that regime
against review is the next test.

## Limitations

* I am not a blind author. I wrote the reference agents' specifications and knew
  Cedar's error semantics, so the 39/40 is an optimistic author. The independent-agent
  arm (8/8) guards against this, but it uses the same model family.
* The review arm used the same model and a small sample (8 items, 75 questions). It
  was not run on property questions.
* Perturbations are random edits of the upstream worlds. They exercise only
  constructs present in each world (e.g. no new K8s object kinds), which is why
  mutation kill rates for K8s and IAM are low.
* Wall-clock for my own authoring comes from the log intervals, and a few intervals
  include harness edits. Agent token counts include each agent's fixed prompt overhead.
