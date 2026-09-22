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
