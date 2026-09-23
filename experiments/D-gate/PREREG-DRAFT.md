# PREREG DRAFT: D gate (raw Opus 5.5 on universal properties of real Cedar and Kubernetes policies)

Status: DRAFT, not frozen, not reviewed. No model call has been made. Before any call:
1. Astra xhigh and Opus xhigh review this draft.
2. `FREEZE.json` records the SHA-256 of `items.json`, `ground_truth.json`, `prompts.jsonl`, `analyze.py`,
   `run_raw.py` and this file (`run_raw.py` refuses to run otherwise).
3. The hashes are committed and timestamped.

## Question and hypothesis

Does a frontier model deciding universal properties of real access-control policies make errors that a verifier
would fix? PLAN-FRONTIER §7 names this D: a headroom gate at zero cost. The plan's own scale thesis expects it to
fail.

* **Gate (primary):** Opus 5.5's raw error rate over the 43 items is at least 15%.
* **Pass:** the D follow-up (§3 of the plan: the closure × order gate theorem and background-axiom templates) may be
  planned. A pass is not itself a VE benefit claim.
* **Fail (< 15%):** the model is at ceiling on *this sample*. The fail closes only this sample: 29 small upstream
  example artefacts. It does not refute headroom on larger or production policies, where the plan expects any
  benefit to need scale.

## Materials (frozen as committed)

* 29 artefacts (22 Cedar and 7 Kubernetes, from P3) and 43 items clustered by artefact (README §1–2).
* Nine items are planted single edits. The reference answers are 20 YES and 23 NO.
* Ground truth: Cedar SymCC (`cedar-policy-cli` 4.13.0, cvc5 1.4.0) for the Cedar items. For the Kubernetes items,
  Z3 5.1.0 over a direct encoding, cross-checked against P3's reference authorizer (README §3). No item is
  undecided. An item that becomes undecided after any rebuild is dropped before the freeze and reported.
* Prompts: `prompts.jsonl` (`dgate-raw-v1`), rendered by `render_prompts.py`. Each prompt shows:
  * the artefact as a reviewer sees it: the policy (or the edited policy), the schema and the template links for
    Cedar, or the RBAC YAML with the filler objects appended for Kubernetes;
  * the domain and the assumptions;
  * the question.

  It never shows the verifier, the encoded property or the answer. The final line must be `ANSWER: YES` or
  `ANSWER: NO`.

## Arms and endpoint

* **Raw only.** There is no VE arm and no tool use. The gate measures headroom, not a benefit.
* **Endpoint:** `ve_experiments/claude_cli.py` (`ClaudeCLI`), which gives:
  * the pinned model `claude-opus-5-5`, with no model fallback;
  * a fresh process per sample, run in an empty working directory with no tools, MCP, hooks, memory or session
    persistence;
  * the system prompt `claude_cli.SYSTEM`;
  * a ledger that records intent first.
* **One subscription account** for the whole study, named at freeze time. Every sample uses it.
* **Primary configuration:** `effort=high`, no thinking cap, 32k output tokens, 900 s timeout. This is the
  conservative choice for a headroom gate: a pass must survive the stronger setting.
* **Secondary configuration:** the T1c monitor setting, `effort=low` with 1,024 thinking tokens.
* **k = 3 samples per item per configuration.** That is 258 calls in all, sequential and resumable.
* **Pilot cap: $0.** Subscription quota only; no API key, Vertex or other paid endpoint. If the endpoint reports any
  paid billing, the run stops.

## Scoring and analysis (`analyze.py`)

* **Parsing.** The last `ANSWER: YES|NO` line is the answer. A reply without one is UNPARSED and scored as an error.
  Endpoint or infrastructure errors are excluded and reported; `claude_cli` never replays a sample silently.
* **Error.**
  * Sample error: the answer differs from the reference answer.
  * Item error: the mean over the item's samples.
  * Primary statistic: the mean item error over the 43 items.
  * Confidence interval: 95% cluster bootstrap over the 29 artefacts (10,000 resamples, seed 0).
* **Gate rule:** PASS iff the primary-configuration point estimate is ≥ 0.15. The CI is reported. If the pass comes
  with a lower bound below 0.15, it is a *weak pass*: the follow-up must first replicate on new artefacts.
* **Secondary analyses,** descriptive, with no gate:
  * the low-effort configuration;
  * false approval, meaning YES on the 23 NO items (the safety-relevant error);
  * false rejection on the 20 YES items;
  * original items vs planted edits;
  * Cedar vs Kubernetes;
  * all items except the `edge-error-semantics` item D26;
  * error by VE coverage category (README §4). This shows whether the headroom sits where VE can certify today.
* **Stop rules:**
  * Endpoint errors above 10% of samples: pause, report, and resume only on the same account.
  * Any sign of billing outside the subscription: stop.

## Threats and limits

* **Item authorship.** Opus 5.5, the model under test, wrote the items and knew the expected answers. The run sees
  no repository content. The reference verifiers, not the author, fix the answers; the author was wrong on 1/43.
* **Pitfall-heavy items.** The sample is small and deliberately includes known pitfalls (README §2). An error rate
  here is not a base rate for real review.
* **Semantic edges.** Some NO answers turn on Cedar error semantics (D10, D12, D26) or on Kubernetes request details
  (D42). The domain text states the governing semantics; D26 is analysed separately.
* **Edit visibility.** In D39 the added object is rendered in a different YAML style, which reveals where the edit
  is but not the answer.
* **Scope.** Universal quantification here is over all schema-valid stores and requests. That is the question a
  certificate answers, not a question about the P3 fixture worlds.
