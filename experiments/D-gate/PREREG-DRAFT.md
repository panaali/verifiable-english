# PREREG DRAFT: D gate (raw Opus 5.5 on universal properties of real Cedar and Kubernetes policies)

Status: DRAFT v2, not frozen. No model call has been made. Revised after the Astra xhigh and Opus xhigh reviews
(both FIX FIRST); every A and B finding is addressed below. Before any call:
1. Both reviewers re-review this draft.
2. `run_raw.py freeze --account <label>` runs on a clean committed tree. It writes `FREEZE.json` with the commit, the
   SHA-256 of every frozen input, and the execution identity (below). `run_raw.py run` refuses to call the model
   unless every freeze check passes.
3. `FREEZE.json` is committed and timestamped.

## Question and hypothesis

Does a frontier model deciding universal properties of real access-control policies make errors that a verifier
would fix? PLAN-FRONTIER §7 names this D: a headroom gate at zero cost. The plan's own scale thesis expects it to
fail.

* **Gate (primary):** Opus 5.5's raw error rate at `effort=high` over the 41 non-edge items is at least 15%, and the
  preregistered robustness conditions hold (see Scoring).
* **Pass:** the D follow-up (§3 of the plan: the closure × order gate theorem and background-axiom templates) may be
  planned. A pass is not itself a VE benefit claim.
* **Fail (< 15%):** the model is at ceiling on *this sample*. The fail closes only this sample: 29 small upstream
  example artefacts. It does not refute headroom on larger or production policies, where the plan expects any
  benefit to need scale.

## Materials (frozen as committed)

* 29 artefacts (22 Cedar and 7 Kubernetes, from P3) and 43 items clustered by artefact (README §1–2).
* Nine items are planted single edits. The reference answers are 20 YES and 23 NO.
* **Edge items:** D26 (Cedar datetime overflow; the question now requires the local time to be defined) and D42
  (Kubernetes `list` with a field selector; the domain text states the rule). Both are run and reported
  separately. They are excluded from the primary endpoint and from every robustness condition.
* **Primary set:** the 41 non-edge items on 28 artefacts. By direction: 16 restriction-NO, 15 restriction-YES,
  5 guarantee-NO and 5 guarantee-YES items.
* **Domains.** Cedar: all schema-valid requests and entity stores in which every referenced entity exists. This is
  SymCC's own assumption; `domain_check.py` confirms it in native Cedar. Kubernetes: get, update, patch and delete
  requests name an object. The Z3 encoding enforces this. Re-verification after both changes left every answer
  unchanged (README §3).
* Ground truth: Cedar SymCC (`cedar-policy-cli` 4.13.0, cvc5 1.4.0) for the Cedar items. For the Kubernetes items,
  Z3 5.1.0 over a direct encoding, cross-checked against P3's reference authorizer. No item is undecided. An item
  that becomes undecided after any rebuild is dropped before the freeze and reported.
* Prompts: `prompts.jsonl` (`dgate-raw-v2`), rendered by `render_prompts.py`. Each prompt shows:
  * the artefact: the policy (or the edited policy), the schema and the template links for Cedar, or the RBAC
    objects for Kubernetes;
  * the domain and the assumptions;
  * the question.

  It never shows the verifier, the encoded property or the answer.
* **Presentation, normalised uniformly.** Comments are removed from every Cedar policy and schema. The stripped text
  is checked to be semantically identical via `cedar translate-*`. Every Kubernetes object is rendered by one dumper
  in a fixed kind order. This removes the comment cues (D34's edit, the comments on D10 in c09 and c11, and those in
  k02 and k03) and D39's style and position cue (README §2a). Only comments and layout differ from upstream bytes,
  so no cue-sensitivity analysis is needed.

## Arms and endpoint

* **Raw only.** There is no VE arm and no tool use. The gate measures headroom, not a benefit.
* **Endpoint:** `ve_experiments/claude_cli.py` (`ClaudeCLI`), which gives:
  * the pinned model `claude-opus-5-5`, with no model fallback;
  * a fresh process per sample, run in an empty working directory with no tools, MCP, hooks, memory or session
    persistence;
  * the system prompt `claude_cli.SYSTEM`;
  * a ledger that records intent first.
* **Freeze (checked before every run).** `FREEZE.json` records:
  * the commit, taken from a clean tree;
  * the SHA-256 of the study files and of `claude_cli.py` and `ve/stream_audit.py`;
  * the SHA-256 of `SYSTEM`, the model id, the per-arm controls, and the `claude` binary hash and version;
  * the account label (never a credential).

  `run` then requires all of the following:
  * a clean tree (outside `runs/`);
  * FREEZE.json committed;
  * the frozen commit an ancestor of HEAD, with nothing under `experiments/D-gate`, `ve` or `ve_experiments`
    changed since it;
  * every hash equal;
  * `--account` equal to the frozen account;
  * every repository module loaded under those paths.
* **One subscription account** for the whole study, both arms. Every ledger row must carry it.
* **Every call:** the served model must equal the frozen model. `claude_cli` checks it, and so do the runner and
  the analysis.
* **Primary configuration:** `effort=high`, no thinking cap, 32k output tokens, 900 s timeout.
* **Secondary configuration:** the T1c monitor setting, `effort=low` with 1,024 thinking tokens. It is descriptive
  only: **a pass at low effort alone does not count.**
* **k = 3 samples per item per configuration.** That is 129 calls per arm, 258 in all, sequential and resumable.
* **UTC days.** The endpoint pins the context date to the current UTC date. Each UTC day therefore writes its own
  ledger segment (`runs/<arm>/ledger-<date>.jsonl`), with identical controls apart from `context_date`. No call
  starts within `timeout_s` + 120 s of UTC midnight; the runner waits and continues in the next day's segment.
  Resume reconciles all segments, so no sample is ever started twice. Each answer records its context date.
* **Pilot cap: $0.** Subscription quota only.

## Execution rules and stop rules (`run_raw.py`)

* A started sample is never replayed. There are no infrastructure retries.
* A **global error** is a refusal before the call starts: budget, controls or binary drift, date, credentials, or
  CLI version. It aborts the run and writes no per-sample row. The run may be resumed.
* **Resume** skips every sample that has an answers row. A sample that the ledger shows as started but that has no
  answers row, for example after a crash, gets its row derived from the ledger:
  * the logged outcome, if there is one;
  * otherwise `ENDPOINT_ERROR` ("interrupted").

  It is never called again, so failure rows cannot be duplicated.
* **Billing stop.** Any sign of billing outside the subscription writes `STOP.json` and stops the run for good:
  * an init `apiKeySource` other than `"none"`;
  * a rate-limit record with `isUsingOverage: true`.

  A served-model mismatch does the same.
* **Usage limit.** A rejection from the subscription's usage limit records that sample, then aborts. Resume after
  the reset.
* **Endpoint-error stop.** Once `ENDPOINT_ERROR` samples exceed 10% of an arm's scheduled samples (more than 12 of
  129), the runner writes `STOP.json` and stops. A stopped arm is never resumed and gets no gate verdict. A new
  attempt needs an amended, re-frozen preregistration.

## Scoring and analysis (`analyze.py`)

* **Parsing.** The answer is the final nonempty line only, and it must be exactly `ANSWER: YES` or `ANSWER: NO`
  (surrounding whitespace allowed). An earlier answer line never counts.
* **Sample status:**
  * `YES` or `NO`;
  * `UNPARSED`: a complete reply without a final answer line;
  * `TRUNCATED`: the reply stopped without a final turn, for example at the token limit;
  * `ENDPOINT_ERROR`: an endpoint or infrastructure failure, including a timeout.

  UNPARSED and TRUNCATED together are **INVALID**. Truncation is a model outcome, not an infrastructure failure.
* **Data completeness (frozen missingness rules).** The analysis refuses to run (exit 2) unless the data is
  complete and consistent:
  * every scheduled sample (43 × 3 per arm) has exactly one answers row;
  * each row matches exactly one ledger start and the ledger outcome: same key and segment, and the status that
    re-parsing the ledger text gives;
  * every ledger row carries the frozen account, SYSTEM, prompt hash, controls and binary;
  * each ledger row's `context_date` matches its segment;
  * no sample was started twice.

  A stopped arm, or one whose endpoint errors exceed the threshold, gets no verdict.
* **Error.**
  * Sample error: the answer differs from the reference answer, or the sample is INVALID.
  * ENDPOINT_ERROR samples are excluded (available-case item means).
  * Item error: the mean over the item's remaining samples.
  * An item with no model outcome is reported by id and counts as error 0 in every gate statistic, so missingness
    can never create a pass.
* **Primary statistic:** the mean item error over the 41 non-edge items at `effort=high`, clustered by artefact.
  * 95% cluster bootstrap over the 28 artefacts (10,000 resamples, seed 0).
  * Also reported: a 95% Student-t interval over the artefact means, and the error share of the top artefact.
* **Gate rule (high effort only).** PASS iff all four hold:
  * the point estimate is ≥ 0.15;
  * with the planted edits excluded, the error is still ≥ 0.15;
  * errors fall on at least 5 artefacts;
  * every leave-one-artefact-out estimate is ≥ 0.15.

  If the estimate is ≥ 0.15 but a robustness condition fails, the result is FAIL and the failed conditions are
  named. A pass whose cluster-bootstrap lower bound is below 0.15 is a **WEAK PASS**: the follow-up must first
  replicate on new artefacts. The low-effort arm gets no gate.
* **Key secondary: false approval on the restriction-NO items** (16 items). This is the rate of actual `YES`
  answers where the reference is NO and access must be denied. INVALID samples are never in a directional
  numerator. They stay in the denominator, and a sensitivity analysis drops them.
* **Direction split** (same rules):
  * restriction-NO false approval;
  * guarantee-NO wrong YES (an availability overstatement, not a safety error);
  * restriction-YES wrong NO;
  * guarantee-YES wrong NO.
* **Other analyses,** descriptive:
  * the low-effort configuration;
  * the primary statistic with INVALID samples excluded (a pass that disappears there is flagged in the verdict);
  * original items vs planted edits;
  * Cedar vs Kubernetes;
  * error by VE coverage category (README §4);
  * the edge items D26 and D42, item by item;
  * all 43 items together;
  * per-item results.

## Threats and limits

* **Item authorship.** Opus 5.5, the model under test, wrote the items and knew the expected answers. The run sees
  no repository content. The reference verifiers fix the answers, not the author, who was wrong on 1/43.
* **An authored challenge set, not a base rate.** The items are pitfall-targeted (README §2). A pass shows headroom
  on this authored set. It is not an error rate for real policy review. Results are reported separately:
  * original vs planted;
  * Cedar vs Kubernetes;
  * by VE coverage;
  * by direction.
* **Semantic edges.** The domain text states the governing semantics: Cedar errors (D10, D12) and entity
  existence, and Kubernetes request details. D26 and D42 are edge items outside the primary endpoint.
* **Context date.** The injected date follows the UTC day of each call. The items do not depend on the current
  date.
* **Scope.** Universal quantification here is over all schema-valid stores and requests. That is the question a
  certificate answers, not a question about the P3 fixture worlds.
