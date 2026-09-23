# PREREG DRAFT: D gate (raw Opus 5.5 on universal properties of real Cedar and Kubernetes policies)

Status: DRAFT v5, not frozen. No model call has been made. v2 addressed the first Astra xhigh and Opus xhigh reviews;
v3 addresses both re-reviews (both FIX FIRST): missingness and formatting gates, truncation from stream evidence,
the stop-rule bypasses, the account UUID, the OpenTimestamps step and cross-day drift. v4 addresses the third
reviews (both FIX FIRST): a joint missingness-and-formatting gate, a deserialized OpenTimestamps check, the D-1
citation and a more tolerant final-line parser. v5 addresses the fourth reviews (both FIX FIRST): INVALID responses
could still shrink the joint denominator, and the robustness conditions used available-case means. The gate is now a
single conservative estimate (parsed wrong answers ÷ all scheduled responses) used by every gating condition, and
the OpenTimestamps check requires the pinned `opentimestamps` library (no hand-written parser). Before any call:
1. Both reviewers re-review this draft.
2. `run_raw.py freeze --account <label>` runs on a clean committed tree. It writes `FREEZE.json` with the commit, the
   SHA-256 of every frozen input, and the execution identity (below). `FREEZE.json` is committed.
3. `run_raw.py stamp` writes `FREEZE-STAMP.txt` (the SHA-256 of `FREEZE.json` and the commit that froze it) and
   stamps it with OpenTimestamps (`ots stamp`, as in the earlier VE preregistrations; a pending calendar receipt
   suffices, no Bitcoin claim). Both files are committed. Nothing is pushed.
4. `run_raw.py run` refuses to call the model unless every freeze check passes, including the committed stamp and a
   `.ots` receipt that binds it. The receipt is deserialized by the `opentimestamps` library, pinned in
   `pyproject.toml` (`opentimestamps==0.4.5`); if it is absent the run refuses (there is no fallback parser). The
   whole file must deserialize with no trailing bytes, including each attestation payload and a valid https
   calendar URI; it must commit to the stamp file's SHA-256 and carry a pending calendar attestation or a completed
   Bitcoin timestamp. A header without a timestamp fails.

**Metric amendment (recorded; PLAN-FRONTIER amendment D-1).** PLAN-FRONTIER's table row for D states the gate as
false approval (FA) < 15%. Amendment D-1 in PLAN-FRONTIER (commit c56cb55 on the `ve-integration` branch; it is not
an ancestor of this branch) replaces that with the **overall error rate** on the non-edge items, and this
preregistration applies it. Reason: 25 of the 41 primary items are not restriction-NO items, where FA is not defined,
and a verifier fixes errors in both directions. FA on the 16 restriction-NO items is kept as the key secondary. The
gate below is stricter than D-1, never looser: it counts only parsed wrong YES/NO answers, over every scheduled
response. D-1's required sensitivity (missing responses count as correct) is built into it, and so are D-1's
robustness conditions (no planted edits, ≥ 5 artefacts, leave-one-artefact-out) and its weak-pass rule.

## Question and hypothesis

Does a frontier model deciding universal properties of real access-control policies make errors that a verifier
would fix? PLAN-FRONTIER §7 names this D: a headroom gate at zero cost. The plan's own scale thesis expects it to
fail.

* **Gate (primary):** Opus 5.5's conservative raw error rate at `effort=high` over the 41 non-edge items (parsed
  wrong YES/NO answers ÷ all 123 scheduled responses) is at least 15%, and the preregistered robustness conditions
  hold on that same estimate (see Scoring).
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
  * the account label and the SHA-256 of the OAuth account UUID. The UUID is read from the CLI's account metadata
    (`<config>/.claude.json`, `oauthAccount.accountUuid`). Only its hash is stored or printed. It binds the config
    directory whose token the endpoint uses. It is not token introspection, which would need a network call;
  * the endpoint controls that every ledger row carries: host system and release, shell, locale, timezone, backend
    revision.

  `run` then requires all of the following:
  * a clean tree (outside `runs/`);
  * FREEZE.json committed;
  * the frozen commit an ancestor of HEAD, with nothing under `experiments/D-gate`, `ve` or `ve_experiments`
    changed since it;
  * every hash equal;
  * `--account` equal to the frozen account, with the same account-UUID hash;
  * the host and endpoint controls equal to the freeze;
  * `FREEZE-STAMP.txt` and its `.ots` committed, naming the committed `FREEZE.json` and its commit, with the `.ots`
    binding the stamp file's SHA-256;
  * every repository module loaded under those paths.
* **One subscription account** for the whole study, both arms. Every ledger row must carry it.
* **Every call:** the served model must equal the frozen model. `claude_cli` checks it, and so do the runner and
  the analysis. A failed call may have `served_model = None`. This is accepted only when `reported_models` is empty
  or exactly the frozen model and the stored stream names no other model. Otherwise the run STOPs (execution and
  recovery) and the analysis refuses the data.
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
* **Ledger audit before every call.** Before its first call, every run audits the whole ledger (all daily
  segments) against the frozen baseline. This covers the recovery after a crash. The audit checks billing, model
  identity, identity fields, controls and input tokens. It runs again after every call. Any problem writes
  `STOP.json`. A crash between a billed call and its stop therefore still stops the arm before any further call.
* **Resume** skips every sample that has an answers row. A sample that the ledger shows as started but that has no
  answers row, for example after a crash, gets its row derived from the ledger:
  * the logged outcome, if there is one;
  * otherwise `ENDPOINT_ERROR` ("interrupted").

  It is never called again, so failure rows cannot be duplicated.
* **Billing stop.** Any sign of billing outside the subscription writes `STOP.json` and stops the run for good:
  * an init `apiKeySource` other than `"none"`;
  * a rate-limit record with `isUsingOverage: true`.

  A served-model mismatch does the same.
* **Usage limit.** A usage-limit rejection that produced no model output is **excluded**. It has no answers row and
  is not an `ENDPOINT_ERROR`. The run aborts. After the reset the same account retries that sample in a new ledger
  segment, `ledger-<date>-q<n>.jsonl`, because the endpoint never reuses a call key within one ledger file. Only an
  excluded rejection may precede a sample's final attempt; any other repeated start is a replay and the analysis
  refuses it. A usage-limit rejection after model output records the sample, then aborts. The number of excluded
  rejections is reported.
* **Drift across days.** Drift is checked against the frozen baseline, not per daily ledger. Every row's controls
  must equal the frozen arm and endpoint controls; only `context_date` follows the segment. Each item's input tokens
  must equal its baseline, which is its first successful call in any segment. An endpoint drift error is also
  treated as drift. Drift stops the run, and the analysis refuses drifted data.
* **Endpoint-error stop.** Once `ENDPOINT_ERROR` samples exceed 10% of an arm's scheduled samples (more than 12 of
  129), the runner writes `STOP.json` and stops. A stopped arm is never resumed and gets no gate verdict. A new
  attempt needs an amended, re-frozen preregistration.

## Scoring and analysis (`analyze.py`)

* **Parsing.** The answer is the final nonempty line only, and it must be `ANSWER: YES` or `ANSWER: NO`.
  Tolerated on that line: surrounding whitespace; one leading markdown heading or list marker followed by a space
  (`#` to `######`, `-`, `*`, `+`, `1.`, `1)`, e.g. `## ANSWER: YES` or `- ANSWER: NO`); markdown emphasis (`*`, `_`,
  backticks, e.g. `**ANSWER: YES**` or `**ANSWER:** NO`); letter case (`Answer: Yes`); and trailing punctuation
  (e.g. `ANSWER: NO.`). An earlier answer line never counts.
* **Sample status:**
  * `YES` or `NO`;
  * `UNPARSED`: a complete reply without a final answer line;
  * `TRUNCATED`: the frozen model produced output but hit the output-token limit. This is read from the stored stream
    records: a `stop_reason` of `max_tokens`, a `<synthetic>` max-output-tokens message (the pinned CLI's truncation
    signal, which `claude_cli` rejects as a served-model mismatch), or output tokens at the cap. The error text alone
    is not evidence;
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
* **Gate estimate (conservative; the only estimate that gates).**
  * Item error = (parsed `YES`/`NO` answers that differ from the reference) ÷ 3, the number of scheduled samples.
  * Every scheduled response that is not a parsed wrong answer counts as **not wrong**: a correct answer,
    `ENDPOINT_ERROR`, `UNPARSED`, `TRUNCATED`, or a missing response. The denominator is always all scheduled
    primary responses (41 × 3 = 123), never shrunk.
  * Why: the reviews found, round after round, that available-case, valid-only and joint estimates let a mix of
    non-answers raise the estimate (12 endpoint errors took 9.8% to 19.5%; 12 items [wrong, UNPARSED, UNPARSED]
    reached 29.3% on 9.8% wrong answers; INVALID samples shrank the joint denominator). Under this estimate no mix of
    non-answers can create a pass: the numerator counts only actual wrong answers and the denominator is fixed.
* **Descriptive estimates (reported, never gating):**
  * available case: INVALID counts as an error, ENDPOINT_ERROR samples are excluded, and an item with no model
    outcome counts as 0;
  * INVALID excluded (valid-only item means);
  * ENDPOINT_ERROR imputed as correct with INVALID counted as an error;
  * joint: ENDPOINT_ERROR imputed as correct and INVALID excluded.
* **Primary statistic:** the mean conservative item error over the 41 non-edge items at `effort=high`, clustered by
  artefact.
  * 95% cluster bootstrap over the 28 artefacts (10,000 resamples, seed 0), on the conservative estimate.
  * Also reported: a 95% Student-t interval over the artefact means, and the error share of the top artefact.
* **Gate rule (high effort only).** PASS iff all four hold, each on the conservative estimate:
  * the point estimate is ≥ 0.15;
  * with the planted edits excluded, it is still ≥ 0.15;
  * parsed wrong answers fall on at least 5 artefacts;
  * every leave-one-artefact-out estimate is ≥ 0.15.

  If the estimate is ≥ 0.15 but a robustness condition fails, the result is FAIL and the failed conditions are
  named. A pass whose cluster-bootstrap lower bound (conservative estimate) is below 0.15 is a **WEAK PASS**: the
  follow-up must first replicate on new artefacts. The low-effort arm gets no gate.
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
  * the number of excluded usage-limit rejections;
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
