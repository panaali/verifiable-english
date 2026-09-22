# C calibration infrastructure (not a scaled calibration result)

Seven primary types implement the PLAN-V4 revision: Uncertain, proof by cases, exclusive-or, modus-tollens chains, near-miss distractors, nested binary quantifiers, and belief-inconsistent vocabulary. Instances optionally cross near-miss and belief vocabulary with the primary type on a predetermined index schedule. The nested family shares binary predicates across forall-exists premises and universally quantified implications, with argument reversal; Uncertain variants distinguish forall-exists from exists-forall via explicit models. No LLM generates gold.

Gold is admitted only after VE parsing/type checks. Entailed/negated queries need a replayed VE tableau plus a satisfying model (no vacuous inconsistency). Uncertain needs VE-evaluated models for both query polarities. Gold proofs/models remain local; the answer-alone prompt contains only English premises/query and label semantics.

Each item has 300–308 English content words using satisfiable independent distractor facts. This is approximate word matching, not equal model-token count, premise count, or reasoning difficulty. Distractor padding can be easy to ignore. These are fresh restricted compositional templates adapted from the B propositional approach, plus new relational templates, not the original ProverGen language distribution or a reproduction of ProverQA. Vocabulary/order/predicate IDs are randomized by disjoint fixed split seeds. Dev/heldout instances are disjoint but intentionally share TYPE templates; do not claim unseen-template generalization. Type labels are not balanced in Uncertain families. Current smoke has two items/type and is only engineering evidence.

Frozen generated files: 14 smoke items; 84 dev and 84 heldout items (12/type/split). `manifest.json` records seed/hash, labels and lengths; this generation is local and spends no model calls. Actual CLI model IDs are pinned: Opus `claude-opus-5-5`, Sonnet `claude-sonnet-5`, Haiku `claude-haiku-4-5-20251001`. Same endpoint isolation, date/host guard, effort low and thinking cap 1024 as B; C output cap 3000 and timeout 180s. Model context/overhead are model-specific constants. No retries, fallback, parallel calls or best-of selection.

Only this smoke is authorized now (42 calls):

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run python experiments/V4-calibration/calibrate.py run --split smoke --judge haiku
```

Do not run C at scale without a separately timestamped C protocol and authorization. Proposed next serial commands, after those requirements are met:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run python experiments/V4-calibration/calibrate.py run --split dev --judge sonnet
UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run python experiments/V4-calibration/calibrate.py select
# Commit/timestamp selection.json BEFORE heldout calls.
UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run python experiments/V4-calibration/calibrate.py run --split heldout --judge opus --selection experiments/V4-calibration/selection.json
UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run python experiments/V4-calibration/calibrate.py run --split heldout --judge haiku --selection experiments/V4-calibration/selection.json
```

Calibration uses k=3 throughout. Select types using ONLY complete Sonnet dev data: at least 20% of items must produce the SAME wrong valid label in at least two replicates. An invalid response is an operational failure, not recurring reasoning error; selection rejects runs containing errors. Empty selection is a ceiling finding, not permission to mine Opus failures. Report each model/type separately, including sample accuracy, majority accuracy, all-three correctness, repeated wrong answers, and missing/invalid counts. Opus dev is prohibited. Heldout requires the recorded Sonnet-dev selection; heldout performance must not feed back into selection.

Human English/gold audit and independent-family replication remain pending. No headline oversight, benefit, difficulty-threshold or power claim follows from smoke success.

For a later-date C study, preregister the chosen UTC date and pass `--context-date YYYY-MM-DD` on its first run. The run manifest then fixes that date; changing it for an existing ledger is rejected. Each day's runs must finish before UTC midnight. This argument does not bypass the date guard or change B's frozen controls.

The final pre-smoke generator also randomizes neutral color/object vocabulary, chooses among belief-inconsistent vocabularies, and varies implication-chain settings from 3–7 and xor-chain lengths from 3–6 while compensating with distractor count. `chain_setting` is a generation parameter, not a measured minimal proof depth. Binary relation vocabulary varies independently across fresh nested-quantifier instances. No changes are chosen using Opus outcomes; C has not been sampled during generation.
