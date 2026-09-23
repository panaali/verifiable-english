# P3: formalisation tax on real artefacts

Package 3 of [PLAN-V3.md](../../PLAN-V3.md). The question: in a domain VE's
`closure@0` profile fits (role-based access control, group nesting, resource
hierarchies, reachability, Alloy-style relational constraints), how often is an
untrusted author's VE formalisation of a **real** artefact faithful, how much of
the source can VE express, what does authoring cost, and how does that compare
with a structured review that answers the same questions without VE?

Refutation condition (fixed in PLAN-V3): *faithful formalisation below about 30%,
or authoring costs more than the review it saves: the thesis is then confined to
synthetic items.* Results and the verdict are in [REPORT.md](REPORT.md); numbers
are in [results.json](results.json).

## Items (40)

| Family | Items | Source (pinned) | What is real / synthetic |
|---|---|---|---|
| Cedar | 22 (`c01`–`c23`, no `c07`) | `cedar-policy/cedar-integration-tests@1999ea2` (11 scenarios) and `cedar-policy/cedar-examples@c251f7d` (11 applications) | Policies, entity stores, schema action hierarchies, template links **and** 115 request decisions recorded by the real Cedar authorizer are all upstream. |
| Kubernetes RBAC | 7 (`k01`–`k07`) | `kubernetes/website@218c4ce`, `docs/reference/access-authn-authz/rbac.md` and `examples/access/*.yaml` | Role/ClusterRole/binding YAML is verbatim; requests and objects marked `"synthetic": true` (some bindings; the admin/edit/view aggregation skeleton of the upstream bootstrap policy) are filler. |
| AWS IAM | 3 (`w01`–`w03`) | IAM User Guide example pages (URLs in `item.json`, fetched 2026-09-22) | Policy JSON verbatim; requests synthetic; `w02` pairs the deny policy with an Allow-all document so the deny is observable. |
| Alloy | 8 (`l01`–`l08`) | `AlloyTools/models@886447d` (genealogy, grandpa1, util/graph + util/relation, mark-and-sweep GC, addressBook3a) | Model text verbatim; finite instances synthetic. `l08`'s query `t in lookup[b, n]` is written for the experiment over the source's `fun lookup`. |

`items/<id>/` holds the exact source text (`source.*`, SHA-256 in `item.json`),
`item.json` (provenance, the neutral JSON world, the questions, recorded Cedar
decisions), and the author's `environment.json`, `formalisation.ve`,
`bindings.json` with a frozen `first_pass/` copy. Eight items also have
`agent/` (an independent author's formalisation) and some have
`naive_variants.json`. Cedar `3c` was dropped only to keep the set at 40.
`build_items.py` / `build_items_extra.py` regenerate `items/*/item.json` and
sources from the pinned clones (`data/README.md`) and from files fetched into
`/private/tmp/p3src` (K8s at the commit above, AWS pages by URL).

## Trust split

* **Reference** (`reference.py` → `reference_cedar.py`, `reference_rbac.py`,
  `reference_alloy.py`): interprets the source artefact directly (a Cedar
  subset interpreter, the Kubernetes RBAC authorizer, IAM evaluation logic, an
  Alloy parser/evaluator with a bounded assertion check). Written by two
  separate agents that never saw any VE formalisation and do not import `ve`.
  The Cedar reference reproduces **all 115** upstream recorded decisions
  (`test_reference_cedar.py`); the others have unit tests and hand-checked
  answers (`test_reference_other.py`).
* **Encoding** (`harness.py`, `adapters.py`): a fixed, per-family, mechanical
  encoding of a world into a VE finite model (the "fact base"), plus per-item
  OPAQUE hooks for what VE cannot express (numeric comparison, datetime, string
  globbing). Hooks are counted against coverage.
* **Author** (untrusted): `environment.json`, `formalisation.ve`, `bindings.json`.
  Statement 0 is true iff the answer is allow / the target holds.
  `AUTHORING_GUIDE.md` is the complete brief given to independent authors.

## Measurements

| Script | Output | What |
|---|---|---|
| `harness.py diff <ids>` | stdout | VE vs reference on the item's questions and on `P3_N` (default 300) seeded perturbations of the world (Cedar: request fields, parent edges, attributes, context, policy-aware links; K8s: request fields, subjects, namespaces, labels, verbs; IAM: action/resource/context; Alloy: tuple toggles and random redraws). |
| `mutation.py` | `mutation_results.json` | Test power: up to 25 syntactic mutants per item (rtc↔tc, swapped direction, closure→edge, and↔or, dropped conjunct/disjunct/negation, ∃↔∀, →consequent); killed if the same differential test disagrees. Survivors classified with VE itself (proved equivalent / finite distinguishing model / unknown). |
| `write_naive.py`, `naive.py` | `naive_results.json` | 14 hand-written realistic mistranslations (ignoring Cedar error semantics, `in` as `==`, one-level aggregation, IAM missing-key rules, ...): does the differential test catch them? |
| `proofs.py` | `proof_results.json` | Prove/countermodel arm: property questions ("can anyone outside the group be allowed?", "is a private document viewable only by its owner?", `check NoSelfGrandpa`, `ring ⇒ weaklyConnected`, ...) with replayed certificates, cross-checked by the reference (sampling or exhaustive bounded enumeration). |
| `make_review_packets.py` + review agents | `review_packets/answers/`, `arms_usage.json` | Structured review without VE on 8 sampled items (10 questions each); fresh agents read the source and answer. |
| independent authors | `items/<id>/agent/`, `arms_usage.json` | Fresh agents author VE for the same 8 items from `AUTHORING_GUIDE.md` alone (paired with the review arm). |
| `nversion.py` | `nversion_results.json` | My formalisation vs the independent author's on 2,000 perturbed worlds per item; the reference arbitrates disagreements. |
| `summarize.py` | `results.json` | Everything above plus coverage (`coverage.py`) and authoring cost (`authoring_log.jsonl`, via `log.py`/`snap.sh`). |

Reproduce (sequentially, from this directory; no network, no paid API):

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache-p3
uv run python test_reference_cedar.py && uv run python test_reference_other.py
P3_N=300 uv run python mutation.py      # ~20 min
python3 write_naive.py && P3_N=300 uv run python naive.py
P3_N=300 uv run python proofs.py
P3_NV=2000 uv run python nversion.py
P3_N=300 uv run python summarize.py     # writes results.json
```

The review and independent-author arms were run as fresh Claude Opus 5.5
subagents in the session; their answers and files are committed, and their
token and time usage (as reported by the agent runtime) is in `arms_usage.json`.
