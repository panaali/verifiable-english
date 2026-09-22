# Independent review of the sanitised paraphrases

REVIEW remains blocked until all 84 current packets have two independent,
identified reviews, including at least one human or project lead per packet.
Mechanical checks and the preparing worker do not supply these approvals.

Export from the repository root with:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-codex uv run python experiments/P5-shifting-definitions/run_p5.py review --export /private/tmp/p5-paraphrase-review-20260922.json
```

This exports the **sanitised-paraphrase** version, a path-only index, 84
individual packet files in three assignments, and
`/private/tmp/p5-paraphrase-review-20260922.submit-schema.json`.
Each packet file is a one-element submission array. `packet.argument` is the
exact final argument under review; `source_argument` is the original prose for
the same dossier, supplied only for fidelity comparison. Premises, records,
glossary and original root are shared. Preserve `item_id` and `packet_sha256`.

Give each reviewer ONE assignment only; use different reviewer identities
across assignments and two independent reviewer pools. Each model review must
start a fresh context for each file. Supply only this instruction file, the
schema and the assigned individual packet. Do not supply the repository,
archives, Git history, construction labels, formal witnesses, other reviewers'
answers or sibling packets. Work independently before discussing disagreements.

For every packet, check the following against authoritative records and the
source argument, without repairing the proposal:

1. **Sense preservation.** Trace every occurrence and each immediately preceding
   reference to its actual producer, unit and record-licensed glossary sense.
   Map every proposed step ID in `annotation.sense_use_mapping`, with source
   anchors in each value. The rewrite must retain the source's meanings,
   ambiguity, and any inconsistent sense or unit transfer. A glossary lists
   possible senses; it does not license a use. Set `source_fidelity` and
   `complete_sense_mapping` explicitly.
2. **Original root.** Record the root's intended meaning in `root_meaning` and
   check that the final step asserts the same unit, predicate, scope and sense
   as the source root. A conditional or substitute conclusion is not the original
   root. Set `root_preserved` explicitly.
3. **Step completeness.** Compare all 16 steps in their original order, all six
   declared premises, both branches, their join, and all four immediate
   references. Every inference and conditional alternative must remain present;
   alternatives must not become declared facts. No step may silently supply a
   bridge, drop a premise, repair a flaw or change a referent. Record required
   assumptions, including whether each is declared, in `required_assumptions`.
   Set `source_fidelity`, `no_added_assumption` and `no_repaired_flaw` explicitly.
4. **No answer-bearing text.** Check the final argument for inserted sense
   labels, explanatory glossary parentheticals, embedded node/rule IDs,
   verdicts, flaw names, hints, editorial diagnoses or formal witness content.
   Bracketed step headings and the separate glossary/records are intentional
   navigation/source material. Removal of parenthetical glosses must not erase
   substantive content. Set `no_answer_leakage` explicitly.
5. **Independent diagnosis and localization.** Recover `kind` as `shift`,
   `smuggle` or `benign` from the sources. Supply exactly two acceptable location
   sets: a singleton consumer and the producer/consumer pair containing it.
   Benign packets also require neutral inspection anchors in this review form.
   Cite supporting record IDs and passages in `source_evidence` and set
   `localization_anchored` explicitly. Unsupported justification does not by
   itself establish that the root is false.

The deterministic sanitation removes only exact glossary-sense parentheticals.
Where a paraphrase expanded a source immediate reference to the exact preceding
claim, a recorded mechanical edit restores the source reference. Review these
edits with the same standards as every other step. They are not independent
semantic approval. No family was regenerated or seed searched.

Fill every checklist field with a JSON boolean, including `false` for any
failure. Supply a stable `reviewer_id`, `reviewer_kind` (`human`, `project_lead`
or `model`), model family for model reviewers, actual positive `minutes`,
`corrections` and `notes`. Do not alter the packet or hash to make a review pass.
List uncertainties and proposed corrections; a failed check leaves the slot
unready. The JSON schema describes the shape; the importer additionally checks
current hashes, complete step coverage, localization IDs and sibling exposure.

Submit completed one-packet arrays separately, or combine only rows from the
same reviewer assignment:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-codex uv run python experiments/P5-shifting-definitions/run_p5.py review --submit /path/to/completed-review.json
```

Disagreeing annotations require identified, source-grounded adjudication bound
to the exact review digests through `review --adjudicate`; otherwise leave the
packet blocked. A construction-label mismatch requires a construction repair
and amendment, never silent relabeling. Any packet correction invalidates old
hashes and requires fresh independent reviews. After actual reviews, refresh
material hashes, the freeze, timestamps and all gate receipts before `dev`.
