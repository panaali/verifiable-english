# D gate: do frontier models err on universal properties of real Cedar and Kubernetes policies?

Claim D of [PLAN-FRONTIER.md](../../PLAN-FRONTIER.md) (section 7 overrides section 2). This is a zero-spend headroom
gate. Before any model call it needs the items, independent ground truth, the domain and schema assumptions, and a
named reference verifier. All four are here. **No model has been called.** The draft preregistration is in
[PREREG-DRAFT.md](PREREG-DRAFT.md).

| File | What |
|---|---|
| `artefacts.json`, `artefacts/<id>/` | The 29 artefacts: verbatim source, Cedar schema, instantiated template links, planted edits |
| `items.json` | 43 items: question, domain, assumptions, what the model is shown, the verifier encoding, VE coverage |
| `ground_truth.json` | Reference-verifier answers, one record per query, with counterexamples |
| `prompts.jsonl` | The exact raw-arm prompts and their SHA-256 hashes (rendered, not sent) |
| `build_items.py`, `ground_truth.py`, `render_prompts.py` | Rebuild everything (see Reproduce) |
| `run_raw.py`, `analyze.py` | The raw-arm runner (refuses to run until frozen) and the preregistered analysis |

## 1. Artefact inventory (29 = 22 Cedar + 7 Kubernetes)

These are the Cedar and Kubernetes items of P3 ([P3 README](../P3-formalisation-tax/README.md), items `c01`–`c23`
without `c07`, and `k01`–`k07`). `build_items.py` checks each Cedar policy file byte for byte against the pinned
upstream clone (`data/README.md`). The Cedar schemas are copied verbatim from the same clones. Planted edits are
marked `*`. Y/N is the reference answer.

| Artefact | Source (pinned) | Licence | Synthetic parts | Items |
|---|---|---|---|---|
| c01_cit_1a | cedar-policy/cedar-integration-tests@1999ea2 `tests/example_use_cases/policies_1a.cedar` | Apache-2.0 | none | D01:Y |
| c02_cit_2a | cedar-integration-tests@1999ea2 `.../policies_2a.cedar` | Apache-2.0 | none | D02:Y D03*:N |
| c03_cit_2b | cedar-integration-tests@1999ea2 `.../policies_2b.cedar` | Apache-2.0 | none | D04:N |
| c04_cit_2c | cedar-integration-tests@1999ea2 `.../policies_2c.cedar` | Apache-2.0 | none | D05:Y |
| c05_cit_3a | cedar-integration-tests@1999ea2 `.../policies_3a.cedar` | Apache-2.0 | none | D06:N |
| c06_cit_3b | cedar-integration-tests@1999ea2 `.../policies_3b.cedar` | Apache-2.0 | none | D07:N D08:N |
| c08_cit_4a | cedar-integration-tests@1999ea2 `.../policies_4a.cedar` | Apache-2.0 | none | D09:Y |
| c09_cit_4d | cedar-integration-tests@1999ea2 `.../policies_4d.cedar` | Apache-2.0 | none | D10:N |
| c10_cit_4e | cedar-integration-tests@1999ea2 `.../policies_4e.cedar` | Apache-2.0 | none | D11:Y |
| c11_cit_4f | cedar-integration-tests@1999ea2 `.../policies_4f.cedar` | Apache-2.0 | none | D12:N |
| c12_cit_5b | cedar-integration-tests@1999ea2 `.../policies_5b.cedar` | Apache-2.0 | none | D13:Y |
| c13_document_cloud | cedar-policy/cedar-examples@c251f7d `cedar-example-use-cases/document_cloud/policies.cedar` | Apache-2.0 | none | D14:Y D15*:N |
| c14_github | cedar-examples@c251f7d `.../github_example/policies.cedar` | Apache-2.0 | none | D16:Y D17*:N |
| c15_hotel_static | cedar-examples@c251f7d `.../hotel_chains/static/policies.cedar` | Apache-2.0 | none | D18:Y D19*:N |
| c16_hotel_templated | cedar-examples@c251f7d `.../hotel_chains/templated/policies.cedar` + `linked` | Apache-2.0 | none (6 upstream links) | D20:N |
| c17_sales_static | cedar-examples@c251f7d `.../sales_orgs/static/policies.cedar` | Apache-2.0 | none | D21:N D22:Y |
| c18_sales_templated | cedar-examples@c251f7d `.../sales_orgs/templated/policies.cedar` + `linked` | Apache-2.0 | none (2 upstream links) | D23:Y D24:N |
| c19_streaming | cedar-examples@c251f7d `.../streaming_service/policies.cedar` | Apache-2.0 | none | D25:N D26:N D27:Y |
| c20_tags_n_roles | cedar-examples@c251f7d `.../tags_n_roles/policies.cedar` | Apache-2.0 | none | D28:Y |
| c21_tax_preparer | cedar-examples@c251f7d `.../tax_preparer/policies.cedar` + `linked` | Apache-2.0 | none (1 upstream link) | D29:Y D30*:N |
| c22_photoapp | cedar-examples@c251f7d `cedar-policy-language-in-action/PhotoApp/photoapp.cedar` | Apache-2.0 | none | D31:N D32*:Y |
| c23_gitapp | cedar-examples@c251f7d `cedar-policy-language-in-action/GitApp/gitapp.cedar` | Apache-2.0 | none | D33:N D34*:N |
| k01_pod_reader | kubernetes/website@218c4ce `content/en/examples/access/simple-role.yaml`, `simple-rolebinding-with-role.yaml` | CC-BY-4.0 | none | D35:Y |
| k02_secret_reader_rolebinding | kubernetes/website@218c4ce `.../access/simple-clusterrole.yaml`, `simple-rolebinding-with-clusterrole.yaml` | CC-BY-4.0 | none | D36:Y |
| k03_secret_reader_global | kubernetes/website@218c4ce `.../access/simple-clusterrole.yaml`, `simple-clusterrolebinding.yaml` | CC-BY-4.0 | none | D37:Y |
| k04_monitoring_aggregation | kubernetes/website@218c4ce `docs/reference/access-authn-authz/rbac.md#aggregated-clusterroles` | CC-BY-4.0 | binding `sre-monitoring` | D38:Y D39*:N |
| k05_crontab_default_roles | same page, `#aggregated-clusterroles` and `#user-facing-roles` | CC-BY-4.0 | admin/edit/view aggregation skeleton (rules omitted); bindings `ana-admin`, `ed-edit`, `vic-view` | D40:N D41:Y |
| k06_configmap_updater | same page, `#referring-to-resources` | CC-BY-4.0 | binding `ci-configmap` | D42*:N |
| k07_subresource_wildcard | same page, `#referring-to-resources` | CC-BY-4.0 | bindings `lee-logs`, `platform-super` | D43:N |

Licences: Cedar material is Apache-2.0 (copied with attribution; see [NOTICE](NOTICE)). The Kubernetes YAML is
documentation content under CC BY 4.0 (attribution in NOTICE). The P3 fixture worlds are not used: every question
quantifies over all worlds.

## 2. Items (43, clustered by artefact)

There are 34 Cedar items and 9 Kubernetes items. Every artefact has 1–3 items. Nine items carry one planted
single edit: 8 break the property and 1 (D32) restores it. The reference answers split 20 YES and 23 NO. Each item
in `items.json` gives:

* `question`: a yes/no universal property. Some say "every allowed request satisfies X" (a NO is a false approval if
  the model says YES). Others say "every request satisfying X is allowed".
* `domain`: what is quantified. **Cedar:** all requests and all entity stores valid for the schema, under Cedar 4
  semantics (default deny, forbid overrides, a policy whose condition errors is ignored). **Kubernetes:** all resource
  requests (any user, groups, verb, API group, resource, subresource, namespace, name), under the RBAC authorizer.
* `assumptions`: **Cedar:** the upstream schema, verbatim; for templated artefacts, exactly the upstream links.
  **Kubernetes:** a closed world (only the listed objects; no bootstrap `cluster-admin`/`system:masters`); the
  aggregation controller has converged; list and watch requests may carry a name (field selector).
* `shown_to_model`: the policy text (the source, or the edited source), the schema and the links, or the YAML with
  the filler objects appended. The model never sees the verifier encoding.
* `tags`: `planted-edit`, `control` (D01), `edge-error-semantics` (D26).

Some items test known pitfalls:

* `in` is reflexive (D07, D09).
* Entities can have several parents (D08).
* Schema `appliesTo` limits (D05, D06).
* Missing-attribute errors that silently drop a policy (D10, D12).
* An optional context attribute lets a request escape a forbid (D21).
* Action-group membership (D24).
* A forbid scoped to an application (D31).
* `A || B && C` precedence (D19).
* Aggregation chains (D39–D41).
* `resourceNames` with list and field selectors (D42).
* `*` over subresources (D43).
* Datetime overflow errors that disable a forbid (D26; see §3).

## 3. Ground truth and reference verifiers

**Cedar: Cedar SymCC, source-native.** `cedar symcc … implies` from `cedar-policy-cli` 4.13.0 (Apache-2.0, crates.io,
built with `--features analyze`) with cvc5 1.4.0 (release binary `cvc5-macOS-arm64-static.zip`, SHA-256
`6560851586d3aabb2a97e0c19f5f75e28da88149dc916a373debe5f2e435d71c`). SymCC encodes Cedar semantics (errors,
extension types, hierarchy) for one request environment (principal type, action, resource type) over all
schema-valid entity stores and contexts. It is the verifier the Cedar project ships for this purpose. The encoding
writes each property as a one-policy Cedar set, `permit (principal, action, resource) when { φ };`:
* "every allowed request satisfies φ" is `implies(artefact, property)`;
* "every request satisfying φ is allowed" is `implies(property, artefact)`;
* the item's answer is YES iff every environment verifies. There are 112 queries in all, each under 0.1 s.

Templated artefacts are analysed as static policies plus each upstream link, with the slots substituted
(`analysis.cedar`; the model sees the template text and the links). Every NO carries SymCC's concrete
counterexample in `ground_truth.json`.

**Kubernetes: Z3 5.1.0 over a direct Python encoding** of the RBAC authorizer (`ground_truth.py:k8s_encode`: string
theory; group membership as an uninterpreted predicate; aggregation computed to a fixpoint). It does not import
P3's encoding or VE. YES iff the negated property is unsat. There are two independent checks against P3's
reference authorizer (`reference_rbac.py`, written separately):
* every Z3 counterexample is replayed through it, and all agree;
* 3,000 steered samples per item evaluate the property with it. YES items show 0 violations; NO items show 19–383.

**Undecided items: none.** All 43 items were decided, and no answer was guessed. The script would mark an item
UNDECIDED on a solver error, a timeout or a disagreement between Z3 and the reference. The author's expected answers
matched the verifiers on 42/43. The exception is D42: I expected YES. It is NO because a `list` request that names
`my-configmap` through a field selector matches `resourceNames`. The domain text now states this.

**Caveats.**
* D26 (NO) depends on 64-bit datetime overflow. An overflowing `offset` makes the bedtime forbid error, and Cedar then
  ignores it. The item is tagged `edge-error-semantics` and analysed separately.
* SymCC's verdicts are per environment. An action with an empty `appliesTo` cannot be requested, so it is not
  enumerated.
* Ground truth assumes the SymCC and cvc5 builds are correct. The Cedar NO answers ship with counterexamples;
  the YES answers rest on the solver's unsat.

## 4. VE coverage (what VE can express today)

`items.json` → `ve_coverage`:

| Category | Items | YES/NO |
|---|---|---|
| `closure@0` (relational FOL + closure; attributes, sets, records reified; schema background axioms) | 28 | 14/14 |
| `closure@0` + hand-encoded Cedar error/`has` guards (D10, D12, D14, D15, D21, D28, D31–D34) | 10 | 3/7 |
| `closure@0 × order@0`: numbers with hierarchy (D09 jobLevel ≥ 5; D13 filesize ≤ 1/100) | 2 | 2/0 |
| `order@0` + datetime adapter: datetimes as integers, no hierarchy (D25, D27) | 2 | 1/1 |
| Not expressible: `offset(...).toTime()` modulo a day plus 64-bit overflow errors (D26) | 1 | 0/1 |

So 38/43 items fall in the merged `closure@0` profile. Ten of those need Cedar's error semantics hand-encoded, which
caused all three P3 first-pass mistranslations. Universal claims also need schema background axioms (P3 c13 needed
them to prove D14's property). The aggregation items (D38–D41) are expressible, but P3's k05 aggregation proof hit
ResourceLimit, so certification is untested.

The 5 items outside `closure@0` need features VE lacks:
* `order@0` is built but gated off, and its combination with closure awaits the gate theorem (D09, D13).
* VE has no datetime type (D25, D27).
* Modular datetime arithmetic and overflow are out of scope (D26).

No item needs IAM globs; IAM is not in the D sample. String equality and string-literal set membership (D22, D31,
D32) are handled as constants and reified predicates. Strings as a theory (prefix, glob, case) never arise.

## Reproduce

```sh
# tools (not in the repo): cedar CLI with SymCC, cvc5 binary
cargo install cedar-policy-cli@4.13.0 --features analyze --locked --root <dir>
# cvc5: https://github.com/cvc5/cvc5/releases/download/cvc5-1.4.0/cvc5-macOS-arm64-static.zip
cd experiments/D-gate
export CEDAR=<dir>/bin/cedar CVC5=<cvc5 binary> UV_CACHE_DIR=/private/tmp/ve-uv-cache-dgate
DGATE_DATA=~/code/ve-claude/data python3 build_items.py           # needs the pinned Cedar clones
uv run --project solvers --locked python ground_truth.py          # ~5 s; z3-solver 5.1.0 locked in solvers/
uv run --project solvers --locked python render_prompts.py
```
