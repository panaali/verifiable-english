# P3 report: formalisation tax on real artefacts

Date 2026-09-22. Author of the main formalisations: Claude Opus 5.5, acting as the
untrusted model author. Numbers come from [results.json](results.json); the method is
in [README.md](README.md). No paid API calls were made.

## Bottom line

"Faithful" below always means **sampled agreement**: agreement with an independent
source-language reference on the item's questions and on the perturbed worlds the
harness drew. It is not a proof of equivalence, and the tests' power is measured in §2.

* **Sampled faithfulness is high.** For 40 real artefacts (22 Cedar policy
  sets, 7 Kubernetes RBAC configurations, 3 AWS IAM policies, 8 Alloy paragraphs), my
  first-pass VE agreed with the reference on every item question, on 300 random
  perturbed worlds per item, and on 100 targeted perturbations per applicable item
  (added after review) in **37/40** cases. It agreed in 40/40 after the
  differential test prompted repairs. Eight fresh agents, given
  only [AUTHORING_GUIDE.md](AUTHORING_GUIDE.md), wrote first-pass VE that agreed
  for **8/8** of the items they authored. Their versions and mine never disagreed on
  2,000 extra perturbed worlds per item. PLAN-V3's faithfulness clause (below about 30%)
  is far from triggered.
* **In the one sampled comparison, authoring cost more than review.** Paired on 8 items with the same model and the same
  accounting, VE authoring cost **1.47× the tokens and 4.3× the wall-clock** of a
  structured review that answered the same packet questions (10 per item, 5 for
  Alloy `l07`: 75 in all). The review was **75/75 correct**, and VE, run on the same packets, was also 75/75. So
  on these questions VE showed **no accuracy gain**. That is not the same as "saved no
  review": authoring yields a reusable evaluator that was tested across changing
  worlds, while the review answered one fixed packet. Shared infrastructure,
  sign-off of the formalisation (0.5–2.3× the source length for the Cedar and Alloy
  items) and the value of reuse were not measured. **For one sampled review batch
  of per-request questions, the cost clause is met.** A broader refutation, across
  question volumes or artefact lifetimes, is not supported by these data.
* VE bought something the review did not only on **universal properties**. There it
  gave certified answers (a replayed tableau certificate or a finite countermodel)
  in 6 of 12 property tasks. That took hand-written background axioms in one case,
  and in 4 tasks it hit checker limits. P3 did not cost this regime against review.
  If the thesis survives, it survives there.
* **Post-review corrections (cross-family review of `94274a9`).** The IAM reference
  and the IAM encoding both treated context-key names as case-sensitive. That was a
  trusted-side defect: re-casing w02's `aws:RequestedRegion` flipped both answers.
  Both are fixed, with regression tests. c21's encoding ignored extra keys in record
  equality. It is fixed with a new `nattrs_<n>` fact, and the new targeted
  perturbations then also exposed a c20 type-error defect. Both are counted as
  first-pass failures (39/40 became 37/40).

## 1. Items and ground truth

40 items, 221 questions (table in README). All policy, model and YAML text is
verbatim from pinned public repositories. The synthetic parts are labelled in each
`item.json`: K8s and IAM requests, some K8s bindings, the admin/edit/view
aggregation skeleton, and the Alloy instances. The Cedar reference reproduces all
**115/115** decisions recorded by the real Cedar authorizer in the upstream fixtures.
The K8s, IAM and Alloy references have unit tests and hand-checked answers.

## 2. Faithful-formalisation rate

| Author | Items | Sampled agreement on item questions + 300 random + 100 targeted perturbations |
|---|---:|---:|
| Me, first pass (frozen in `items/*/first_pass/`) | 40 | 37/40 |
| Me, after differential feedback | 40 | 40/40 |
| Independent agents (first pass, no reference access) | 8 | 8/8 |

Targeted perturbations (800 in all) exist for the 3 IAM items (re-cased context-key and
`${var}` names) and for the 5 Cedar items whose worlds contain records (an extra key
added to a record). They were added after the review.

There were three first-pass failures:
* **c15 (hotel_chains)**, found by a random perturbation. A string was put into a set
  used with `in`. Cedar raises a type error and skips the policy; my formula fell
  through to the next `||` disjunct. Two of the independent agents had modelled exactly
  this rule. Inspection then found the same latent bug in c17, which the test had not
  exposed.
* **c21 (tax_preparer)**, found by the cross-family review. Cedar record equality
  needs equal key sets, but my formula ignored extra keys in `assigned_orgs` members.
  The first pass disagrees on 17/100 targeted worlds. The repair needed a new encoding
  fact, `nattrs_<n>(r)`, because an open attribute vocabulary cannot say "no other key"
  in the old encoding.
* **c20 (tags_n_roles)**, found by the new targeted perturbations (1/100). A tag value
  that is not a set makes `.contains`/`.containsAll` a type error.

All of these are Cedar error or equality semantics, and all were repaired
(`authoring_log.jsonl`). None of the 300 random perturbations per item caught c20 or
c21. Separately, 6 items need OPAQUE adapter predicates, so only **34/40** agree
*in pure VE* (see §3).

**How much "faithful" means.** An all-green differential test is only as good as its
power, which I measured two ways.
* *Mutation analysis* (`mutation_results.json`): 813 mutants over the 40 items. The differential test (random plus targeted perturbations) killed **536 (66%)**; the item's own questions alone killed 405 (50%). Of the 277 survivors, VE's prover showed 6 equivalent to the original. For 54, a small finite VE structure distinguishes them, but it may be unrealisable in the source language (e.g. aliased constants). 217 are unclassified within budget. Kill rates are lowest for the reused K8s and IAM authorizer formulas (w01: 3/25), whose clauses the item worlds never exercise.
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
* c21 compares record-literal fields as string/long values only (the schema has String).
  Its extra-key gap, previously listed here, turned out to be exercisable and is now fixed (§2).
* c20's `containsAll` compares record-valued set members by node identity (the schema
  has `Set<String>`).
* IAM `Bool` is case-insensitive (w03).
* Kubernetes has `*/subresource` forms. The independent k07 author approximated them
  by enumerating 18 subresources.

A second cost that coverage alone does not show: **Cedar's error semantics had to be
hand-encoded** (has_/bf_/type guards) in 9 of 22 Cedar items. Together with record
equality, this was the source of all three first-pass mistranslations and of most naive
variants the test found hardest.

## 4. Authoring cost

| | Me (40 items) | Independent agents (8) | Structured review (same 8) |
|---|---|---|---|
| Tokens per item | not measurable inside my own context; VE artefacts median ≈1.0k tokens | mean 31.1k (23.6k–38.1k) | mean 21.1k (19.6k–22.8k) |
| Wall-clock per item | 526 s in total; median 13.5 s for non-reused items (upper bound, includes running the checker) | mean 68 s (16–118 s) | mean 16 s (12–20 s) |
| Checker errors / repairs | 0 parse/type errors; 4 repairs (c15 test-driven, c17 same class, c21 review-driven, c20 test-driven after review) | 11 check runs, 3 with syntax errors (all bracket nesting), 0 semantic repairs | n/a |
| Accuracy | 37/40 → 40/40 items (sampled agreement) | 8/8 items | 75/75 answers |

The review arm's 75 answers were rescored against the fixed reference (unchanged), and
VE gives the same 75/75 on those packets. Both agent arms carry the same fixed prompt
overhead, so their *marginal* ratio is larger than 1.47×. The two arms do not produce
the same thing, though. The author ends with an evaluator that answers any further
request on the artefact; the reviewer ends with 10 (or 5) answers. Two structural
points matter more than the constants:
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
2. **Mistranslation in a first pass**: 3 of 40 (c15, Cedar type error of `in` over
   a set with a non-entity member; c21, record equality with extra keys; c20, set
   methods on a non-set tag); 0 of 8 independent first passes. Only c15 was caught by
   the original random test. c21 was found by an outside reviewer, and c20 only by
   targeted perturbations written after that review. Add to this the detection rates
   for seeded mistranslations in §2, including one realistic miss at N=300.
3. **Checker limits**: finite evaluation never hit ResourceLimit (40 items × 300–400 worlds).
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
   * 1 shared defect in the IAM reference **and** the IAM encoding, found by the
     cross-family review. Context-key names (and `${var}` names) are case-insensitive
     in AWS, but both looked them up case-sensitively, so they agreed with each other
     while both being wrong. Both now fold key names to lower case (values keep their
     case). Regression tests: w02 with `AWS:REQUESTEDREGION` in
     `test_reference_other.py` and `test_harness_regressions.py`. The IAM items'
     formalisations needed no change.
   * The reference and adapter machinery as a whole expands what the experiment
     trusts, even though the VE checker itself was not changed.

## 7. Refutation condition

PLAN-V3, package 3: *refuted if faithful formalisation is below about 30%, or
authoring costs more than the review it saves.*

* Faithfulness (sampled agreement): 37/40 first pass (40/40 after repairs), and 8/8
  for independent authors. This clause is **not met**, with two caveats. The test
  catches about 11/14 realistic mistranslations at the budget used, and two of my
  first-pass defects needed targeted perturbations that were written only after an
  outside review.
* Cost: for one sampled review batch (8 items, 75 fixed questions), VE authoring
  cost more than the review (1.47× tokens, 4.3× time). Both arms were at ceiling
  accuracy, so VE showed no accuracy gain on these questions. Whether it saves review
  over repeated questions, sign-off and reuse was not measured. The clause is **met
  for this batch only**.

**Outcome: the refutation condition holds narrowly.** It holds for one sampled review
batch of per-request authorization and constraint questions on real RBAC and Alloy
artefacts. It is not shown for larger question volumes or for reuse of a
formalisation over an artefact's lifetime. Following the plan, the
"tolerable usefulness tax" claim cannot rest on these measurements. The live possibility is
certified universal properties (§5). There VE answered questions review can only
argue about, but needed reviewed background axioms, and its prover stopped at
closure monotonicity and multi-level aggregation. A package that costs that regime
against review is the next test.

## Limitations

* I am not a blind author. I wrote the reference agents' specifications and knew
  Cedar's error semantics, so the 37/40 is an optimistic author. The independent-agent
  arm (8/8) guards against this, but it uses the same model family. The `nattrs_<n>`
  fact and the IAM key-case note were added to `AUTHORING_GUIDE.md` after the
  independent authors ran. None of their 8 items needs `nattrs_<n>`, and the w03
  agent's formalisation passes the key-case perturbations unchanged.
* The review arm used the same model and a small sample (8 items, 75 questions). It
  was not run on property questions. Its cost is for fixed packets, while authoring
  cost buys a reusable evaluator. Neither sign-off nor reuse was costed.
* Perturbations are random edits of the upstream worlds. They exercise only
  constructs present in each world (e.g. no new K8s object kinds), which is why
  mutation kill rates for K8s and IAM are low.
* Wall-clock for my own authoring comes from the log intervals, and a few intervals
  include harness edits. Agent token counts include each agent's fixed prompt overhead.
