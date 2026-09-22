# P5 execution amendments — 2026-09-22

## P5 Gemini input accounting repair (2026-09-22)

The retained Gemini infrastructure smoke has prompt digest `3f8c59a0...`
and billed input 64. The shared Vertex counter supplied system instructions
and tools, but omitted generationConfig (including response MIME and schema).
Free countTokens checks returned 9 with that legacy config and 17 with the
generation config included. Thus the original discrepancy is 55 tokens;
the measured residual after fixing the config is **47 tokens**. This is an
empirical per-config correction, not a claim about undocumented token internals.
The smoke has no system text. A null `_p1_response_format` was an OpenRouter-only
reporting field, not evidence that Vertex omitted the response schema.

P5 now uses its own Vertex subclass; P1's backend, counters, probes, planning
and freeze are unchanged. P5 sends the same contents, system instruction,
tools and generation fields to countTokens that it supplies for generation.
`calibrate-gemini` performs only free counts of already completed P5 ledger
requests. It records native counts, exact wire and response hashes, served
revision and additive residuals in `checks/gemini-calibration.json`. Refreeze
binds that artifact and embeds the calibration table in `freeze.json`.
Runtime and preflight add the residual to every counted input bound for its
exact config. Visible answer-length checks remain plain native text counts.

Only the smoke config currently has billed evidence. The correction is keyed
by model and the full count config, including system instructions, response
schema/MIME, tools, output limit and generation settings. A different config
is blocked rather than assigned an invented correction. A dedicated coverage
gate enumerates the uncalibrated study configs; independently authorized billing
evidence for those configs is still required before dev. This repair makes no
additional paid smoke or study calls. Repeated `probe --offline` reuses the
retained billing and free-count evidence, verifying **17 + 47 = 64**, without
generation or Vertex access. The billing ledger is not rewritten.

Stage input limits, output caps and scenario dollar ceilings are unchanged:
the calibrated total must fit the existing input cap. Gemini fixture receipts
from the old counter are invalid until recounted with the full config and a
matching calibration. The new freeze invalidates the previous execution
timestamp; all existing material, review, timestamp and dev gates still apply.

Reproduction after this repair (no paid calls):

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache-codex
uv run --offline python experiments/P5-shifting-definitions/run_p5.py preflight-openrouter --offline
uv run --offline python experiments/P5-shifting-definitions/run_p5.py probe --offline
uv run --offline python experiments/P5-shifting-definitions/run_p5.py preflight --offline
```

The calibration refresh, when needed, is `calibrate-gemini` followed by
`freeze --scenario dual_judge`; refreshing requires free Vertex countTokens
access but never dispatches generation. The API supports generationConfig:
https://docs.cloud.google.com/vertex-ai/generative-ai/docs/reference/rest/v1/projects.locations.publishers.models/countTokens

Original PREREG.md and PREREG-DESIGN.md remain byte-for-byte intact. This is a
pre-inference implementation amendment, not externally timestamped. No probe,
dev, scored or paid paraphrase has run in this implementation session.

## P5-1: output feasibility and requested replication

Operator instruction: “judge and attacker max_output_tokens 1,024 … per-call
halt at 1,024 billed”, and “Judges: same as P1 (Gemini Pro primary; Qwen
replication).” This conflicts with the original 2,048 author/repair caps and
Gemini-only judging. All author and repair calls therefore have a **1,024 total
billed output** ceiling; judges/critics/defenders also have 1,024. Isolated answers
retain 512 and adaptive follow-up retains 256. Thinking counts toward every cap.
No hidden formal solution is supplied to compensate for reduced authoring room.
A feasibility failure stops/amends; it does not quietly enlarge a cap.

`primary` retains the Gemini online protocol. `dual_judge` adds Qwen final
judgments of the exact same frozen Gemini protocol transcripts, and a Qwen lone
floor. Qwen is descriptive replication of judgment, not a second equal-strength
online duel or an efficacy substitute selected on outcomes. The original primary
contrast remains Gemini VE−X. This preserves equal Gemini online capability and
fits the $40 cap without discarding items. See execution-inventory.json for exact
ceilings. Freeze a scenario before inference, never choose from scored outcomes.

One schema-constrained provider smoke per endpoint is explicit overhead, using
128 input/1,024 billed output ceilings. `probe` is an alias for these infrastructure
smokes, not an extra P5 efficacy probe: P5 output feasibility uses scheduled dev.
The reused P1 backend permits bounded retries only for retryable infrastructure
failures; holds remain charged, request bytes remain frozen, no replacement
scientific samples. Unknown billing and exhausted retries halt the affected
provider, and unknown billing can halt study dispatch. Reserve complete blocks.

## Material status under the $0 build authorization

The separate offline pass accepts only natural-language dossiers and rewrites
node/argument phrasing. It is reproducible deterministic **draft editing**, not
the independent Qwen72 paraphrase required by §3. Its provenance says so. Do not
claim independent prose or release scoring from these drafts. `paraphrase` later
performs exactly one ledger-backed Qwen call per slot; then both independent
reviewers must annotate all 84 exact resulting packets. This is an explicit
remaining prerequisite, not a waiver. All material-generation API cost is
attributed in full to every online arm. Engineering/manual review time is separate.

Reference construction uses 6 declared leaves: a conjunction of six initial
facts and five conjunctions of forward-chaining rules. There are 24 derived
claims and 24 deduction edges. Ground atoms may use two named units. At least
half the vocabulary occurs in claims or relevant competing senses. Reference
bridge-augmented proofs are compositional certificate graphs, while negative
witnesses check the entire original six-premise set against the original root.
The bridge remains hidden and is never a trusted online premise.

Any tokenizer, leakage, independent review, source-label, replay, provider or dev
failure is a real block. Publish this amendment and the exact aggregate freeze
hash before scoring. A successful reference replay is no semantic-readiness claim.

## P5-2: reconstruction after the blinded NOT READY review

All 84 original packets failed the independent Claude Opus material review.
The original annotations are retained, bound to their old packet hashes, in
`materials/review-ledger.jsonl.gz`; none approves a regenerated packet. The
original preregistration remains unchanged. This amendment changes construction,
not the assigned slots, efficacy endpoints, paid authorization, or review bar.

The generator now makes one fixed source dossier per family with three possible
recorded checks. The declared facts and argument select one check. Its result
establishes either the required property of a lot, a different sense of the same
word for that lot, or the required property of a sample. The downstream rule
requires the lot property in its original sense. In a shift, the argument reuses
the word across those two source-anchored readings; in a smuggle, it uses the
sample result without stating any sample-to-lot transfer assumption. Both
missing bridges remain hidden diagnostic artifacts. The authoritative records
are byte-identical across siblings. The sample/lot naming convention is recorded
in the source and constant descriptions; it asserts no property transfer.

Each item now has 24 full English inference sentences, also collected in
`argument`, rendered from the graph. Claims cite premise content. No public node
contains a `rule_record` pointer. Each proposal discusses the same alternatives,
but only its selected check is declared: alternative checks remain unassumed.
This balances the lexical workload through substantive alternatives rather than
padding. Both senses of two other ambiguous terms are asserted consistently in
every variant. Both critical senses are also established on a separate
comparison lot, so neither is an orphan predicate. Dormant conditional routes and redundant context edges appear in
benign and flawed proposals alike. Sense, predicate, record, entity and claim
indices are seeded permutations independent of the item label. Opaque-ID sorted
packets are shuffled with the fixed `20260921/packet-order-v2` seed for export;
no seed is selected based on labels or model outcomes. A construction-version
namespace gives replacement packets fresh opaque IDs, preventing reuse of the
old review's public ID-to-label mapping; hidden slot identities remain fixed.

There are still 28 distinct family shapes, 24 deductions, six declared premise
claims, 24 source records, and 20/40/60 glossary entries. The first premise now
contains seven facts (the six starting facts plus the selected recorded check);
the other five are conjunctions of rules, as before. Source records may contain
multiple conditional alternatives. The actual formal graph includes the fact
premise at the selected-check deduction; its non-isomorphism is checked in
addition to the original dependency skeleton. These are explicit changes to
what is packed into the six leaves, not extra free bridges.

`checks/leakage.json` reports three fixed logistic-regression probes: unigram
counts, packet structural/length features, and their combination. All 84 slots
are evaluated in 28 leave-family-out folds; vectorizers and scalers fit on the
training fold only. The operative gate now compares the best-of-k probes against refitted
permuted-label best-of-k nulls, passing at **p >= 0.05** (P5-4 below). All variants have the same token multiset (apart from
opaque IDs) and the same structural features within their family. The check
reruns on the exact review bytes, including after paid paraphrasing. Export
position is an external randomization audit, not a packet feature; its three
residue-class label counts are reported separately. Random finite-sample order
imbalance is not repaired by label-aware shuffling. The first unsuccessful
reconstruction audit is retained in `checks/leakage-attempts.jsonl.gz`; its
structural probe included export-position indicators and scored 36/84, while
token and combined probes scored 28/84. The revised construction removes lexical
length differences; no corpus seed or trained hyperparameter was selected.

Remaining specification issue: full English prose and substantive definitions
may exceed the preregistered 2,048-token common-packet limit and the 4,096-token
paraphraser input allowance. Token gates remain binding. No evidence is silently
truncated, no cap is increased, and no paid call is authorized by this amendment.
The paid independent paraphrase and fresh independent review of all 84 final
packets still precede scoring.


## P5-4 — round-3 privacy, context isolation, prose and null correction (2026-09-22)

The operator explicitly requested these repairs and $0 generation. All 84
packet IDs are replaced with 128-bit HMAC-SHA256 outputs keyed by one private
256-bit random nonce, generated once and retained outside the repository with
mode 0600. Neither nonce bytes nor a recoverable public seed enter artifacts.
Repeated generation with that private nonce is stable; there is no ID/nonce
selection based on gate outcomes.

The four-way source grid and proof design remain unchanged. The residual
family-transductive unfired-cell rule is handled by mandatory isolation:
exactly one packet per model/editor context, no few-shot examples, and transcript
entries bound to the same item ID. Review and explanation exports use separate
family-disjoint assignments, one packet per file, with a path-only index.
Reviewer/rater identities cannot submit sibling packets, even across calls.
Two independent reviews are still required **per packet**, including a human or
project lead; this now requires disjoint reviewer pools for the three
assignments instead of two people each reading all siblings. Model contexts
must also be fresh even if the model family is reused. Adjudicators obey the
same exposure rule. Do not send a whole export tree to one reviewer/context.

Arguments are topologically ordered prose paragraphs with stable step labels
for answer localization; premises are stated by content, never parent IDs.
Unqualified references name the immediately preceding result, giving a unique
referent without requalifying or repairing the critical inference. Exactly
three harmless steps per packet use the same device. The node/parent block is
included only in VE model requests; all arms share the prose. These deterministic
offline drafts are not an independent Qwen paraphrase or a review approval.

The earlier flat chance cutoff is replaced by a fixed 199-permutation null.
Each permutation shuffles labels within families, retaining the balanced
matched design, refits all classifiers and single-feature lookups, and repeats
the complete best-of-k selection. Vectorization/scaling fit only on training
folds; label-dependent stratification is rebuilt for each permutation. The
one-sided p-value is (1 + null maxima >= observed maximum) / 200, and the gate
passes at p >= 0.05. There is no classifier/seed/nonce search. Existing token,
budget, formal-soundness, independent-author and independent-review gates remain
binding. No paid generation was authorized or performed by this amendment.


## Revision 5: fourth blinded review repair (2026-09-22)

See [CONSTRUCTION-V5.md](CONSTRUCTION-V5.md). Remove label-bearing inventory
rows and duplicate graph labels; preserve the original inventory's aggregate
budgets but redact its slot manifest. This explicitly supersedes the previous
claim that its bytes remain immutable. Rotate the HMAC namespace because v4
ID/label mappings were published. Gold location sets now have one singleton and
one pair for all three kinds, with identical defect grading and neutral benign
anchors. Remove prose sense tags and use four natural frames. Match all four
back-reference profiles to (3 referents, 2 senses, 2 units) within every packet;
expand to three active ambiguous decoys. Regenerate source/prose/formal artifacts
and invalidate previous reviews. The 2,048 common-packet cap, 84 slots, 28 families,
16 steps, six leaves, paid ceilings and $0 execution authorization are unchanged.


## Revision 5 follow-up: archive isolation and timestamp evidence (2026-09-22)

Explicitly bar the dossiers, scored, dev and paraphrase archives, including
the sibling-group field used by the transductive attack. Preserve the supplied
round-5 review JSON and verification report as barred audit evidence. Operator
attribution: Claude Opus 4.x subagent, cross-family, blind. The verification
report claims 84/84 localization and zero invalid packets; the supplied JSON
contains only 30 partial records and its import was rejected for sibling
exposure. Missing packet hashes, sense mappings, root meanings and evidence
cannot be reconstructed as independent review. No review gate is overridden
and no adjudication is eligible. Original submitted metadata is retained.

MATERIALS-MANIFEST.json lists exact material/archive SHA-256 values.
MATERIALS-HASHES.txt binds that manifest, PREREG.md, this amendment and the
submitted review bytes. Retain its OpenTimestamps calendar receipt and bind
these artifacts into the execution freeze; also stamp freeze-manifest.sha256
for the existing preflight gate. Calendar submission is timestamp evidence,
not verified Bitcoin confirmation. Rewritten paraphrases require fresh review,
counts, material hashes, timestamps and a refreeze before dev/scoring.
The inventory ceilings and $40 study cap are unchanged; this worker spends $0.

## Revision 5 follow-up: shared Qwen smoke counter (2026-09-22)

The retained DeepInfra smoke request with message SHA-256
`3f8c59a0e68023eb1c5bda8090fa898a1175f258ac1ec3da37a8a60ae61d0a0d`
billed 17 input and 11 output tokens. P5 already imported P1's native counter.
The pinned upstream Qwen template inserted an absent system message, adding
21 tokens (38 locally). The shared P1 counter now omits only that template
branch for Qwen requests without tools or an explicit initial system message.
It leaves explicit system content, tools, special-token encoding and tokenizer
assets unchanged. P1's explicit-system Qwen smoke remains 19 tokens and Llama
remains 21. The retained request's JSON-schema response format adds no prompt
text; the correction does not subtract schema or tool tokens.

`preflight-openrouter --offline` reuses the original matching ledger completion
and recounts it, even after a previous passing receipt or refreeze. It permits
no generation or tokenizer downloads, needs no positive spending cap, and fails
closed on missing or changed cached requests. Online reruns also preserve the
original completion when its count disagrees. The command's exit status covers
the requested OpenRouter check; the full provider receipt still requires both
Gemini and Qwen. The original billing ledger is never rewritten by a recount.

Paraphrasing uses one system and one user message, `max_tokens=1024`, no tools,
and no `response_format`; its system instruction asks for JSON. The counter
receives the same wire object as generation and renders the full messages
jointly. All 84 explicit-system paraphrase counts are unchanged by this fix.
This amendment does not add structured-output enforcement to paraphrasing.

## Revision 5 follow-up: resumable infrastructure and authoring routing (2026-09-22)

P1 and P5 infrastructure retry limits now apply to each request within one
client invocation: the initial dispatch may be retried three times after
5, 20 and 60 seconds. Exhaustion stops that invocation but is never a durable
panel halt. A new invocation resumes the identical assignment, including
legacy ledgers with four or more failures. Every failed attempt remains in
the append-only ledger with `sample=false`; it neither creates a trial nor
uses the next invocation's retry allowance. HTTP 429 rejections cost zero.
P1 retains unfinished block reservations. Legacy released blocks with an
unresolved infrastructure failure reopen only their original unspent balance,
after subtracting all completed costs and billing holds; completed blocks
remain cache-only.
Timeout/5xx billing holds remain charged as infrastructure overhead, and all
dollar caps, frozen-request checks and nonretryable validation halts remain.

Only the Qwen PARAPHRASE authoring role may route from DeepInfra to Novita.
Routing is restricted to those two providers, allows fallback, and omits the
judge-only fp8 restriction because the listed Novita endpoint is bf16.
The retained P1 endpoint listing prices Novita input at $0.38/M and output
at $0.40/M, with the existing 1.055 fee factor. Each paraphrase call reserves
that maximum and reconciles to its served provider's price. The aggregate
paraphrase envelope and explicit cap are unchanged; a call that cannot fit
the remaining envelope still stops before dispatch. No budget top-up occurs.
The served provider is retained in both billing and paraphrase provenance.
Paraphrase revision checks are isolated by provider and authoring role;
Qwen judges and provider smoke retain their pinned DeepInfra routing and
revision checks. Completed authoring replies remain reusable without new
samples. These changes were tested locally with no paid calls ($0).

The execution freeze is renewed for this code change. Prior material and
execution timestamp receipts remain historical; they do not certify this
amendment or the renewed freeze. Offline preflight rechecks all fixture hashes
and recounts all Qwen requests locally; it retains Gemini counts only for
matching fixtures. Changed fixtures remain blocked for a free API recount.
Independent prose, review, timestamp, full provider and dev gates
remain binding. No generation, token-count API, or timestamp submission is
authorized or performed by this worker; additional spend is $0.

Offline reproduction from the repository root (with pinned tokenizer assets
already cached):

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache-codex
uv run --offline pytest -q tests/test_p1_native_counter.py tests/test_p5_preflight.py
uv run --offline python experiments/P5-shifting-definitions/run_p5.py preflight-openrouter --offline
uv run --offline python experiments/P5-shifting-definitions/run_p5.py preflight --offline
```

The last command reports the remaining study blockers and exits 2; a passing
Qwen recount does not make P5 ready for paid paraphrases or scoring without
separate spending authorization and the applicable gates.

## Revision 5 follow-up: paraphrase format, leakage validation and resume (2026-09-22)

The operator requested this repair under a $0 authorization after a completed
Qwen authoring response wrapped its JSON in a Markdown fence and copied glossary
sense glosses into inference prose. P5 now shares P1's single-fence formatting
tolerance. Its own schema remains strict: exactly `texts`, every existing node
key exactly once, no other keys, and nonempty string values. Duplicate JSON
keys are rejected. Paragraphs are assembled in the original node order.

The paraphraser receives its own authoring instruction and a separate glossary.
It must keep every step, premise content, order, immediately-preceding references
and any inconsistency. It must not insert parenthetical glosses, sense labels,
or node/rule IDs into prose. Validation rejects glossary sense phrases inside
parentheses (case/whitespace insensitive, excluding the glossary's Rnn suffix)
and node/rule IDs in text values; JSON node keys are required and permitted.
This mechanical check does not certify preservation of meaning or back-references;
the independent source-fidelity review remains required.

At the operator's explicit direction, a failed validation permits exactly one
correction request naming the violation, using the same dossier and constraints,
with turn 1 distinct from initial turn 0. This is a narrow change to §3's original
one-call authoring rule, not a search for persuasive prose. It is still charged
to the existing shared-paraphrase block and the explicit cap: no larger envelope,
call ceiling or automatic top-up. If the remainder cannot fund a correction,
execution stops resumably before dispatch. Infrastructure retries remain separate.

Every terminal slot is checkpointed with request/response hashes, both attempt
identities, violations, revisions and served providers. Two invalid responses
mark a slot `paraphrase-failed`; it has no accepted argument, is excluded from
usable dev/scored packet archives, and is counted with its ID in
`runs/study/paraphrase-status.json`. This implements the requested construction
failure treatment under §3's unready-slot gate. All slot records and paid ledger
entries remain retained. The all-84 review gate and complete-family analysis
requirements stay binding; exclusions do not silently authorize reduced scoring
or post-treatment exclusions prohibited by §7.

Resume revalidates the original billed responses. For an existing identity, only
its original message bytes are restored after exact checks of dossier hash,
metadata, model, ceilings, schema, tools and timeout. The shared paid client's
strict request/cache checks still apply. A valid old response is never repurchased;
a failed one gets only its one correction, which is itself reused on restart.
Original request hashes, costs and infrastructure evidence are not rewritten.
Unattempted slots use the corrected prompt. Checkpoints can be rebuilt from the
ledger after interruption; they are not trusted instead of response validation.
Paraphrase resume permits changes only to its three generated material archives
inside the freeze check. Dossier/code hashes remain mandatory, and ordinary
dev/scored freeze verification permits no such exception.

The execution freeze and retained OpenRouter smoke receipt are refreshed locally
for this change. Original preregistration and material archives remain intact in
this $0 repair session. Existing timestamp receipts remain historical. Independent
review and the remaining study gates must be satisfied before scoring.

After separate spending authorization, resume from the repository root with the
existing aggregate cap (the command below was not run by this worker):

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-codex uv run --offline python experiments/P5-shifting-definitions/run_p5.py paraphrase --cap-usd 0.17
```

`uv --offline` disables dependency downloads; `paraphrase` itself makes paid model
calls when a slot needs its first or correction response.

## Revision 5 follow-up: mechanical glossary sanitisation (2026-09-22)

Operator authorization is $0: revalidate all 84 slots from retained Qwen replies,
including the 19 excluded slots whose 38 attempts failed the glossary-parenthesis
check. Before remaining validation, apply `exact-parenthetical-glossary-sense-v1`
to every response, independent of labels or prior acceptance. Remove only whole,
unnested parenthesised phrases exactly equal to a dossier glossary sense after
casefolding and whitespace normalisation; the glossary term prefix and Rnn label
are not part of a sense. Collapse whitespace and remove spaces before punctuation
when deletion occurs. Do not remove substrings, synonyms, compound glosses or
nested glosses. Retain all steps, restore the original node order, require nonempty
text, and reject node/rule IDs and any remaining parenthetical glossary phrases.
This does not certify semantic fidelity; independent review remains binding.

`paraphrase --offline` revalidates retained attempts in original attempt order,
uses the first passing sanitised reply, and excludes/counts terminal failures.
Missing corrections never trigger purchases. Missing initial completions block.
All response/request hashes and original billing evidence remain intact; output
provenance adds the sanitiser version and sanitised-text hash. The offline path
constructs no provider and writes no billing events. All 84 outputs, including
previously accepted slots, are regenerated through the same validator.

The leakage audit retains the existing full-packet and VE node-block probes and
adds three fixed probes over the exact shared paraphrased argument: unigrams,
prose/paragraph lengths, and their combination. All three use the same
leave-family-out folds, training-only vectorisation/scaling and existing fixed
hyperparameters. Every one of the 199 within-family null permutations refits
them and includes them in the best-of-k maximum. The report binds the exact
paraphrased prose hash. No label-dependent editing or seed/probe search is allowed.

Refreeze and rerun offline gates and tests. Prior reviews and timestamps do not
approve the rewritten packets or renewed freeze. Token counts for changed Gemini
requests require a fresh free countTokens run; local Qwen counts cannot substitute.
Any failing gate remains a blocker. No generation or paid provider call is
performed by this worker. Reproduce the revalidation with:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-codex uv run --offline python experiments/P5-shifting-definitions/run_p5.py paraphrase --offline
```

The cached rebuild accepted **84/84**, recovered all 19 exclusions, and left
0 paraphrase-format failures. The first valid cached attempt policy removed
exact glosses from 39 selected replies (495 steps). A second pass is identical.
The billing ledger remains byte-identical; additional spend is $0. Construction
regressions now explicitly exercise the original dossiers/offline renderer;
post-paraphrase semantic readiness is assessed by the real offline gates, with
an added regression that altered references must fail source soundness.

Validation: the final full offline suite reports 1,502 passed, two skipped,
one deselected, and two unrelated P1 ledger-history failures
(`test_p1_amendment13.py::test_scored_gate_and_cap_reach_only_qwen_attacker_backends`
and `test_p1_amendment14.py::test_recover_and_reconstruct_every_retained_scored_call_without_dispatch`).
All P5 tests pass. The real surface-soundness gate still rejects packet
`i2afbcc296df87f190ef25c465f52f9d1`: its retained Qwen response replaced four
immediately-preceding references with explicit unit claims. Format acceptance
does not waive this gate or authorise a substantive repair.

The fixed permutation audit executes independent null refits in eight local
processes, each with numerical libraries limited to one thread. Permuted labels
are generated serially with the original RNG, and results retain their original
order. This changes execution only: estimators, hyperparameters, seeds, folds,
199 permutations and the best-of-k statistic are unchanged. The slow preliminary
serial run was stopped before producing a gate result; the authoritative audit
is rerun from the final freeze. No classifier, seed or gate threshold is selected
from outcomes.
## Revision 5 follow-up: reference restoration and exact-config calibration (2026-09-22)

The retained Qwen paraphrase for one packet expanded four immediately preceding
references into explicit unit claims. A deterministic source-only rule restores
a reference only when the expanded premise exactly equals the preceding source
conclusion and the source uses that immediate reference. It preserves the
paraphrase's conclusion, inference frame and tail, and records before/after
edits in provenance. The same rule is applied to all 84 retained responses;
four edits in one packet result. No family, label, seed, source record or formal
graph changes, and no paraphrase generation is purchased. Raw provider replies
remain in the append-only ledger. This is an amended Qwen-derived packet, still
requiring independent review; it is not represented as untouched model output.

User authorization permits only Gemini calibration smokes, at most 12 calls and
$0.50 total via Vertex ADC. Twelve distinct study configs receive one minimal
user prompt each with the exact frozen system, schema, tools, thinking config,
seed, temperature and output ceiling. There are no retries. The study ledger
records 12 completions costing $0.053782, with no billing holds. Exact-config
input residuals are zero for 11 configs and 139 tokens for the verdict schema
config. The original provider smoke retains its separate 47-token residual.
These are single-smoke calibrations, not evidence of semantic or dev quality.
Every scheduled request is freely recounted using its own config's overhead;
runtime exact recount and billing checks remain mandatory.

The separately itemized $0.50 calibration ceiling raises maximum primary and
dual-judge all-in ceilings to $33.9097270016 and $35.2512920096 respectively,
both within the unchanged $40 study cap. Per-stage limits, matched arm ceilings
and study sample sizes do not change. Actual calibration charges remain shared
infrastructure overhead, not trial spend or new dev samples.

PARAPHRASE-REVIEW.md specifies independent review of sense preservation,
original root, step completeness and absence of answer-bearing text. The export
contains each final sanitised argument plus the same dossier's original prose,
with family-disjoint assignments and a generated submission schema. No reviews
or approvals are fabricated. Materials and execution manifests receive renewed
OpenTimestamps calendar receipts after the final code/material freeze. This
worker does not run dev or scored inference.

## Revision 6 — Amendment (orchestrator), 2026-09-22

Under the lead's delegation, material review may use two independent model
families: Claude Opus (Anthropic) and Gemini 3.1 Pro (Google, Vertex ADC).
The lead hand-check of a sample is **deferred**. Model reviews remain identified,
family-disjoint by assignment, and bound to the exact reviewed packet hash.
Family aliases do not count as separate families. Semantic disagreements still
require explicit adjudication; this amendment does not approve material.

The delegation described the completed Claude review as blind. Its retained
verification file explicitly says **UNBLINDED (repository and labels consulted)**.
We preserve that disclosure instead of relabeling the review blind. The 84
Claude rows and verification file are imported as historical v5 evidence, with
reviewer_kind=model. They cannot approve the subsequently changed v6 packets.
A current-hash Claude re-review is consequently needed alongside Gemini before
the two-review gate can pass. Gemini sees only one public packet and its source
per fresh request; it never receives Claude's review or the hidden labels.

The old Qwen pass was a no-op in all 84 packets. It is superseded, not counted
as independent rewriting. The new prompt requests substantial structural
rewriting, varied connectives, and sentence merging/splitting within each step.
Step order and literal claim content remain fixed; prose has no step markers.
Ordered IDs are supplied separately to every arm. Temperature remains the
designed **0**, seed 20260921. Exact glossary-only sanitation remains, but the
source-reference restoration is removed from acceptance. New revision-scoped
request identities prevent replay of old paid no-op replies. There is at most
one correction per packet, retaining every attempt and bill.

Acceptance requires normalized character Levenshtein distance **>=0.35** after
sanitation, measured against source text with step markers removed. An
independent public-record licensing search tries zero relaxation, then all
one-relaxation readings; kind, localization and sense assignments must be
recoverable exactly as from the source. Step conclusions, premise atoms,
immediate references and conditional alternatives must also be preserved.
The parser supports explicit ordinary-English inference structures and rejects
unparsed substantive wording; it is a conservative material check, not a claim
to understand unrestricted English. Tests use rewritten fixtures only; they are
never stored as paid paraphrases or represented as independent review.

One conditional-alternative tail remains in every benign and flawed packet.
The first independent random assignment over 16 steps produced 12/56 shortcut
hits (conditional permutation expectation 5/56, p=.0197277). That failed result
is retained in checks/rejected-localization-v6-random.json; no seed was searched.
The final construction samples uniformly from the eight comparison positions
shared by all four reference blocks. All possible producers AND consumers are
excluded by structure, regardless of which block is critical. This is a
construction constraint, not post-hoc selection of particular packet seeds.
The rule "tail producer + following reference consumer" now abstains, so it
adds no information beyond guessing among four reference blocks. The leakage
gate includes its exact family-level null, preserving sibling dependence, in
addition to all existing kind and paraphrase-text probes. Passing a draft
screen does not stand in for auditing the future Qwen prose.

Paid authority is limited to all 84 replacement Qwen paraphrases (at most
**$0.40** including failures/corrections) and Gemini review (at most **$1**).
Separate persistent v6 ledgers enforce these total caps across invocations;
the study ledger conservatively reserves those envelopes inside its $40 cap.
Gemini uses fresh contexts, compact JSON, 1,024 billed output tokens, serial
calls and the existing durable paid-client accounting. A budget or provider
failure stops without assuming missing reviews passed. No dev/scored call is
authorized by this amendment. The OpenRouter key is absent in Worker X's
environment: prepare and freeze v6 source material, then stop before dispatch.
Gemini review is dependent on all 84 accepted new paraphrases and therefore
cannot run on the superseded prose merely to claim completion.

## Amendment (orchestrator, 2026-09-22): paraphrase stage waits for DeepInfra on 429

Novita rejected the v6 paraphrase request (HTTP 400, "does not support endpoint: completions"). The paraphrase stage now retries DeepInfra after 20/60/120 s pauses instead of falling back to another provider. Authoring only; judges unchanged. Refreeze.

## Revision 7 — Amendment (orchestrator), 2026-09-22: constrained rewriting

The v6 re-buy accepted **0/84 slots after 168 completed attempts**, costing
**$0.1597614352** in retained completed-call charges. The instruction to rewrite
substantially and the string-level atomic licensing check were incompatible in
practice. The failures were all at the semantic parsing/licensing gate: retained
messages identify 89 unsupported conclusions, 77 unsupported inference syntaxes,
and 2 unparsed substantive premise wordings. No attempt met acceptance. The
v6 ledger, raw replies, infrastructure records and study envelope remain as
cost/evidence; this amendment neither erases them nor relabels them accepted.

Superseding v6's rewriting instruction and 0.35 raw-text distance threshold,
v7 requires a **CONSTRAINED rewrite**. Every occurrence of each atomic claim
phrase (`unitN is <predicate>`) and every unit name stays verbatim at its source
step. Surrounding prose may be independently re-structured: sentence order
within a step, connectives, merged/split premises, active/passive discourse
framing, and conditional-alternative framing. This is **independently
re-structured prose with atomic claims verbatim, not a free paraphrase**. The
restriction limits claims about linguistic independence and generalization.

Acceptance requires all steps in source order, no IDs/glosses in final prose,
unchanged premise/conclusion/reference content and conditional alternatives,
and the same complete zero-then-one-relaxation licensing readings (including
kind and localization) as the source. The parser remains conservative about
unparsed substantive wording. Each atomic phrase is replaced by the same
single `#` character in both source and sanitized candidate. Normalized
character Levenshtein distance on these masked ordered packet strings must be
**at least 0.20**, divided by their maximum length. Step markers are excluded;
all other characters, spacing and punctuation remain. Atomic multiplicities
and unit names are checked independently, so masking cannot hide a synonym,
omission, duplicate or changed unit. No generated rewrite is accepted solely
because its distance passes.

The re-buy retains a **$0.40 cumulative cap**, separate v7 ledger and request
namespace, at most one correction per slot, durable checkpoints, and cached
response revalidation on resume. Failed v6 attempts are never replayed as v7
responses. The unchanged $40 study cap contains both historical and new
envelopes. No new paid calls are authorized for Worker X: prepare, test, commit
and print the command only. No dev/scored call occurs under this amendment.
See REVISION7.md for the exact command and RESULTS.md for the required disclosure.

## Amendment (Worker X, 2026-09-22): conservative interrupted-call reconciliation

The orchestrator restarted during `paraphrase --revision v7`, leaving one call
reserved without a completion. After stopping the caller, `reconcile` now
appends an `interrupted` event for each outstanding call reservation, charging
its **full original ceiling** as worst-case accounting against the existing
cap. The event records the original reservation time/hash, request identity,
model, metadata, charge, and any unresolved halt belonging to that attempt.
It is explicitly **not a trial** (`sample=false`), supplies no response, and
does not establish a model revision. No unknown call is assumed free. Existing
completed calls, settled infrastructure failures, and validation/revision/price
halts on completed responses remain unchanged. Unused block planning envelopes
are not calls and are not charged as interruptions.

The same request may be re-issued with its exact frozen contract and a new
full-ceiling reservation inside the remaining budget. Repeated reconciliation
without another dispatch adds no charge; another interrupted dispatch incurs
another full charge. Original ledger rows are never edited. Block resumption,
per-item matched caps, and cost attribution retain interruption charges. P1
uses this same shared ledger logic and its reconciliation command applies it
to the study and auxiliary billing ledgers.

P5 reconciliation includes separately capped revision ledgers. Their charges
stay inside their already retained study envelopes, avoiding double counting
or any reset/increase of the **$0.40 v7** or **$40 study** cap. The interrupted
v7 correction request is charged **$0.0020742144**; nine completed calls retain
**$0.0092151296**, for **$0.0112893440** accounted in v7 and **$0.3887106560**
remaining in its block. The study's retained commitment is **$0.9694671176**,
including the v7 envelope. This is an accounting upper bound, not a provider
invoice. Audited releases/allowance adjustments still use `--receipt`.

This recovery makes **zero paid calls / $0 new provider spend**. Refresh the
execution freeze and offline gates without regenerating material. Incomplete
rewriting, review, token coverage and timestamp gates remain explicit blockers
to scoring; this amendment permits only resuming the authorized authoring run.

## Revision 8 — orchestrator amendment, 2026-09-22: generator-rendered prose

The independent-paraphrase requirement is dropped before dev/scored inference.
v6 accepted 0/84 after 168 completed calls ($0.1597614352); v7 accepted 2/84
after 167 completed calls ($0.1770597638), with 165 acceptance violations:
97 unsupported inference syntax, 38 changed atomic phrases, 26 insufficient
rewrite/changed licensing, and 4 unparsed premises. Mechanical acceptance
recognizes the generator's restricted sentence frames; the attempted genuine
restructuring was incompatible with this acceptance scheme. All attempts, raw
responses, exclusions, infrastructure charges and interruption holds remain
in the ledgers; the final v7 acceptance archive is retained separately. v6
holds total $0.0041484288 and v7 holds $0.0290390016. No refund or successful
independent paraphrase is inferred.

Judges will read **generator-rendered topological prose from the same VE
graphs**. VE formalisation is therefore easier than on independently authored
prose, a material limitation on the comparison and its generalization. The
VE arm still authors its formalisation and pays for its diagnostic repair call
when used. No generator proof or reference mapping is given to the VE model.
The tail-placement fix is kept: the alternative sentence is placed on an
independently chosen comparison step, never on a producer/consumer. All 84
current public packets are checked against the retained round-5 packets: only
the conditional-tail position may differ, with its exact content preserved.

The review gate now accepts (a) the retained round-5 Claude Opus blind report
whose material verdict is READY and (b) a new Gemini 3.1 Pro review, via Vertex
ADC, of all 84 current packets in separate fresh contexts. This explicitly
supersedes the old requirement for two complete per-packet annotation imports
and independent prose. The round-5 partial submission originally failed the
importer (missing fields/hashes and sibling exposure); those facts remain in
the record. Round 6 supports fidelity and no kind leak, but explicitly consulted
labels and is **unblinded**; its localisation finding motivates the retained fix.
Neither historical report is relabelled as a new hash-bound independent review.
Current Gemini reviews provide a material verdict, kind, producer/consumer pair
(or empty benign location), record-grounded evidence and issues. Missing,
malformed, negative, uncertain or disagreeing reviews keep the gate closed;
no annotations are filled in from gold. Final mapping anchors retain their
reference provenance, conditional on both material reviews and source checks.

The only new paid authorization is **at most $1 cumulative** for Gemini material
review, with a separate durable v8 ledger and a $1 envelope inside the unchanged
$40 study cap. Each request uses one public packet only, at most 3,500 input
and 768 total billed output tokens (including thinking), serial dispatch and
existing bounded infrastructure recovery. Compact review output avoids the
old redundant full-map format. No efficacy/dev/scored call is authorized.
The old independent-prose gate is replaced by a generator-provenance and
historical-transfer gate. Refreeze, rerun every offline gate including kind
and localisation probes, exact tokenizer checks and Lean replay, and renew
the external timestamp before the separately authorized dev command.

### Revision 8 review output feasibility correction (same $1 cap)

The first three Gemini reviews cost $0.042556. With a 768-billed-token
ceiling, one was complete, one truncated, and one reported 824 billed tokens
and triggered the per-call halt. All remain in the ledger. The bounded
continuation uses the existing 1,024-billed-token ceiling and the exact
judge-visible English packet (including every premise, authoritative record,
step and original root), avoiding redundant JSON/glossary serialization.
The complete prior review is retained, even if it disagrees; only incomplete
reviews may be retried under a distinct request version. No substantive
negative judgment is retried. The cumulative $1 limit is unchanged and missing
reviews remain blockers if the review cannot finish within that limit.

Cost attribution includes the physical v6/v7 rewrite charges and their holds
in each arm's full shared-material cost and per-item ceiling check. Study
envelopes reserve those same charges and are not added a second time as
physical spending. Gemini material review is reported as separate overhead.

### Revision 8 review outcome (2026-09-22)

The continuation produced five valid current-packet reviews, all marked ready
and agreeing with reference kind/localisation. Nine completed calls cost
$0.124892, plus a $0.019288 infrastructure hold: **$0.144180 total**. The last
call reported 1,068 billed output tokens against 1,024 and caused another
provider validation halt. This second halt is **not** covered by the narrow
768-to-1,024 recovery. No further calls are dispatched. The $1 cap remains
intact and the review gate remains blocked on the 79 unapproved slots.
This is a failed attempt to complete review, not an amended claim that five
packets suffice. All other offline checks and timestamp renewal proceed.

The final offline packet-safety audit exposed an implementation mismatch: it
rejected every leading `[nNN]` localization label in generator-rendered prose.
It now permits only a leading label matching that step's expected ID and order;
IDs in the prose body, wrong markers, non-topological parents and invalid
back-references remain rejected. This changes validation of the already
reviewed format, not material bytes or any label/content restrictions.


### Revision 8 review thinking-budget amendment (2026-09-22)

Explicit Worker X authorization raises material-review `max_output_tokens` and
its total billed-output halt threshold to **4,096**, including Gemini 3.1 Pro
thinking. The 768/1,024 limits truncated reviews; thinking remains enabled at
LOW and is billed as output. This changes only material review, not study calls.
The task authorizes **$1.50 additional** Vertex ADC spending, including any
infrastructure holds. Prior ledger spending is $0.144180, so the durable
cumulative ceiling is **$1.644180**. A supplemental $0.644180 review envelope
extends the old $1 envelope inside the unchanged $40 study budget.

Resume reconstructs all reviews from hash-bound paid ledger evidence. Every
schema-valid, normally completed (`STOP`), untruncated judgment is reused,
including negative judgments. Only truncated/incomplete reviews may be reissued
under version 3 (4,096) identities; subsequent incomplete attempts get distinct
retry identities. Historical token-cap halts are acknowledged only for the old
768/1,024 requests whose billed output fits 4,096 and whose input/revision checks
pass. Raw responses, halts and every charge remain append-only; a new 4,096
halt is not silently recovered. Reports separately count accepted packets,
completed reviews flagging defects (grouped exact defect text and packet IDs),
and incomplete/unreviewed packets. Any defect or incomplete review blocks dev.
Only 84 accepted reviews permit review-gate evaluation and final refreeze;
kind/localisation agreement and all other existing dev gates remain required.
No dev/scored call is authorized or dispatched by this task.


The authorized continuation finished with **83 accepted / 1 completed defect
report / 0 incomplete**, reusing five complete reviews and making 79 new calls.
Task spending is **$1.129784**; cumulative review accounting is **$1.273964**.
The extra-meaning-shift defect on `ib9279ca87379a78c8da58ec68a9d4b42` is retained
verbatim in RESULTS.md and the status report. Five other material-ready reviews
disagree with reference diagnoses; they remain acceptance reports, with those
disagreements separately retained. The existing gate remains blocked; no dev or
scored call was dispatched and no negative judgment was retried.


### Revision 8 mechanical dispute adjudication (2026-09-22)

Explicit Worker X authorization permits offline exhaustive sense-assignment
adjudication of the documented one defect claim and five diagnosis disagreements.
The six original Gemini responses remain unchanged. Only these six packet IDs
may use this route: evidence is bound to the current packet and original review,
recomputed at the gate, and checked against the intended kind and localization.
The defect claim is rejected: n03 is the sole unlicensed step (the intended
clear shift); n20/free is licensed. The other five packets are benign under
zero-relaxation readings. This supersedes the prior requirement that all 84
Gemini responses themselves agree before refreezing. Review acceptance now rests
on 78 direct agreements plus six documented mechanical adjudications. The
original report remains 83 accepted / 1 reported defect / 0 incomplete.
Refreeze and timestamp renewal are authorized; no paid calls are authorized.

### Revision 9 — dev harness contract amendment (2026-09-22)

Worker X is authorized to diagnose the failed dev attempt and change only
harness/infrastructure, with **no paid calls / $0 new spending**. The 15 dev
completions cost $0.1476830522 and are superseded as an incomplete infrastructure
attempt. All raw requests, outputs, billing and historical trials remain intact.
See [the per-response audit](DEV-CONTRACT-AUDIT.md) and its machine-readable
`checks/dev-contract-audit.json`; neither is efficacy evidence.

Only eight final judgments were observed. The old 0.041667/0.083333 rates divide
2/4 and 4/4 valid observed responses by 48 assigned outcomes per judge. Six calls
hit MAX_TOKENS: all four VE roles, one S author and one pro lone judge. The last
VE defender billed 1,095 tokens against 1,024 and halted the primary panel,
leaving 88 final judgments missing. One complete pro judgment cited record r02
in locations. No complete judgment violated vocabulary, fields or explanation
length; unknown is permitted and there is no maximum explanation length.

The amended wire **and billed-output** limit is **4,096** for VE stages, the S
author, and pro final/lone judges; Gemini LOW thinking remains enabled and billed.
Other stage limits are unchanged. Prior-output reserves and downstream input
limits grow by the corresponding maximum text increments; no transcript is
truncated. `prompts.json` records effective per-arm/model stage limits separately
from the historical base stage table. Both scenario and block ceilings use the
actual amended request limits. No cap overrun is forgiven on the new requests.

Both judge providers already attached the verdict schema. Transport regressions
now verify Vertex's actual generate config and OpenRouter's HTTP JSON. P5 judge
requests refuse OpenRouter's schema-less `json_object` fallback; P1's fallback
policy is unchanged. Nonjudge free-text roles do not receive a verdict schema.
VE artifact correctness remains an authoring outcome; this amendment supplies
no reference environment, corrected source, proof or mapping.

The prompt explicitly distinguishes paragraph/declared-premise nNN locations
from rNN record evidence, requires distinct locations and nonempty explanation,
and describes empty locations and the allowed unknown verdict. JSON shape,
field set, vocabularies, at-most-two distinct strings and nonempty explanation
remain contract rules. **Location membership and correctness are scored behavior**:
wrong/unknown/record IDs and missing localization cannot produce detection credit,
but no longer make a well-formed verdict a contract failure. Exact reference
localization, issue-type correctness, benign empty-location completion and
source-grounded explanation requirements are unchanged. No gold location enum
is supplied to providers. MAX_TOKENS/LENGTH final judgments fail the completion
contract even if their partial text happens to parse.

Contract reports now show observed valid/observed counts, assigned coverage and
the legacy assigned-valid fraction separately. The >=90% criterion is unchanged;
full assigned coverage and source-fidelity review are still required to pass dev.
Missing outcomes continue to score zero in assigned-denominator analysis.

New request and block identities use `study-v9/`; new result directories are
`runs/dev-v9` and `runs/scored-v9`, including explanation ratings and analyses.
Old dev outputs cannot satisfy the new gate or be reused from the provider cache.
A narrow append-only recovery acknowledges only the documented 1,095/1,024
old VE defender halt and releases the unused old dev reservation. Costs stay
charged to the same study/item/arm; no refund or completed block is inferred.

The **$40 study and $0.16 item/arm ceilings are retained**. The larger request
reservations yield a dual-judge worst-case schedule of $69.8036611616 and a
maximum combined VE item/arm bound of $0.3753408992; the budget gate must fail
rather than hide that incompatibility. Calibration and native-count receipts
for changed configs remain invalid until genuinely renewed; no paid calibration
or inferred replacement receipt is created in this task. Offline checks may
inspect a budget-blocked freeze, while all paid execution still enforces it.
Historical timestamps are archived; a new executable freeze needs a fresh
external timestamp. This is a frozen, diagnosed repair with explicit blockers,
not authorization to exceed budgets or a claim of scored readiness.

### Revision 9 — $40 schedule selection amendment (2026-09-22)

The orchestrator retains the $40 study cap and orders alternatives (a) both
judges/reduced scored families; (b) Gemini only/24 families; (c) Gemini
only/reduced families. X/S/VE/L, cross-examination k and every v9 stage bound
are unchanged. The first study-cap fit is (a), nine scored families, with a
$35.2264590298 worst-case total including retained commitments and the full
$0.30 calibration reserve. The unchanged $0.16 item/arm gate is separately
infeasible; a $0.45 common ceiling is pending explicit amendment. See
[SCHEDULE-AMENDMENT.md](SCHEDULE-AMENDMENT.md) for all scenarios, deterministic
balanced selection, retained cost accounting and the reduced-power consequence.
Six new Gemini config smokes cost $0.035710; no dev/scored calls were made.

## Amendment (orchestrator, 2026-09-22): common item/arm ceiling $0.16 -> $0.45; scenario (a) with 9 scored families

After the 4,096-token Gemini caps (Gemini thinking is billed output), VE retained-plus-future cost per item reaches $0.4465, above the $0.16 matched ceiling. The ceiling is raised to $0.45 for EVERY arm (matched-ceiling framing unchanged). Budget: scenario (a) selected (Gemini + Qwen judges, all arms, preregistered k, 9 scored families; worst case $35.23 of the $40 cap). With 9 families the primary-contrast half-width is about +/-0.49: P5 is explicitly a FEASIBILITY pilot; no efficacy claim will be made from it.


## Amendment (orchestrator, 2026-09-22): infrastructure is study-only spending

The resumed v9 dev observed 13/48 assignments per judge with 100% contract
compliance on observed judgments, then stopped at the matched $0.45 item/arm
ceiling because provider failures and infrastructure holds were attributed to
reasoning. This is an accounting failure, not evidence about arm efficacy.

The common **$0.45 ceiling counts only successful calls producing an accepted
provider response**, identically for X/S/VE/L and both judges. HTTP 500s,
connection resets, failed/retried attempts, panel infrastructure holds, and
interrupted calls reconciled at their full reservation ceiling consume the
**$40 cumulative study cap only**. A successful retry counts its accepted
response once; its failed attempts do not consume matched reasoning budget.
A billed completion rejected by provider token/price/revision validation is
also study-only, even if a later amendment recovers its halt. Accepted means
accepted by the provider-validation layer, never a correct or favorable scored
answer: malformed, truncated, unknown, or semantically wrong responses that
pass that layer still consume reasoning budget and retain existing scoring.

Accepted shared paraphrase calls remain fully attributed to every arm.
There are no future paraphrase calls in this schedule, so no phantom paraphrase
minimum is charged. The local CPU allowance remains in the study ledger; it is
not an accepted provider call. Before dispatch, the matched check reserves
room for one successful response at its full call ceiling. Planning, runtime,
and cost-report views use the same accepted-completion rule. Physical costs,
failed attempts, reservations, raw outputs, request identities and retry locks
remain intact; no study charge is refunded and no efficacy retry is enabled.

The retained-plus-future maximum matched bound is now **$0.4275424776** (VE).
The selected dual-judge/nine-scored-family schedule stays **$35.2264590298**,
with its retained commitments and CPU allowance unchanged. Existing v9 outputs
remain resumable. Offline tests/refreeze and timestamp renewal are authorized;
**no paid calls** are authorized by this repair. Dev completion and source-
fidelity review remain required before scored execution.
