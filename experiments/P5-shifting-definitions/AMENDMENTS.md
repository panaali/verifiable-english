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
training fold only. Every probe must achieve **at most 1/3 accuracy** before the
review gate can pass. All variants have the same token multiset (apart from
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
