# P5 execution amendments — 2026-09-22

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
