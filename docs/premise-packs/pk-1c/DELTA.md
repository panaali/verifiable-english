# pk-1c: delta

Feature item pk-1c (`docs/spec/premise-packs.md` 2.6; DRI decision 2026-10-27, item 3).

**What users see does not change.** The item adds theorems and `#guard` fixtures only: no definition, relay, response
shape, schema, Python or Rust file changes, so no answer, refusal, text or verdict changes (no output differential
is needed: no evaluated definition differs). Trust: K +0, S +0, V +0 (`tools/trust_map.py --check` on the final HEAD).

The one delta is to an approved statement, which the DRI signed:

| # | Change | Ruling |
| --- | --- | --- |
| S1 | The approved `legacy_labels_nodup` (`docs/spec/premise-packs/SpecStubs_pk1.lean:163`), false by fixture F1′ (`cx`), is replaced by `legacy_labels_nodup_of_actKeys` (`lean/VE/NormDefaults/PacksLabels.lean:342`): the same statement plus `(hk : ∀ k ∈ VE.Rights.condKeys R, ':' ∉ k.2.1.toList)`, proved. `legacy_labels_nodup` is not built. | SIGNED by the DRI 2026-10-27 (reviews/dri-decisions-20261027-featureplan-gates.md item 3); condition tests: F1′'s guards kept, including the refusal `InvalidInput: premise label … is used twice` (`PacksLegacyExamples.lean:121–129`); `bridge_identifier_sep` (`PacksLabels.lean:280`) and its fixtures (`PacksLegacyExamples.lean:139–141`) show `VE.Bridge.identifier` refuses `:`, and `legacy_labels_nodup_of_identifiers` (`PacksLabels.lean:392`) discharges `hk` from it |
