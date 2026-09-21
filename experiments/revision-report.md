# Worker X revision report — 2026-09-21

## BRANCH

codex/e5. Merged codex/oracle at `9a37f16`; the subsequent revision contains all materials, preregistrations and validation artifacts reported here.

## SUMMARY

E5 now has three difficulty presets, independent audit/neutral instructions, seeded flaw/control positions, and raw scope/tag comparisons.
Half of merged-vocabulary BAD items carry forged tags; GOOD tags are honest. Spread flaws require joining varying selector keys to dossiers.
E2 has eight scored shapes, fresh vocabulary, exact word-multiset matching at invalid steps, and growing obligations in half the items.
E4 has twelve scored quantified/relational templates and 60 valid + 60 invalid scored inferences, oracle certificates, dishonest critics, and matched critique word counts.
Preregistrations, cluster-t analysis, conditional power calculations, leak probes and label solvers are updated; zero live model calls.

## VERIFY

All uv commands used `UV_CACHE_DIR=/private/tmp/ve-uv-cache`.

| Command | Result |
|---|---|
| `uv run python -m experiments.E5.materials --write` | 3,072 items; complete compressed materials for all three levels |
| `uv run python -m experiments.E2E4.generate` | E2 432; E4 136; shared proof archives regenerated |
| `uv run python -m experiments.validate_materials` | All 3,640 labels proved from frozen records and replayable artifacts; 0 calls |
| `uv run python -m experiments.E5.leak_audit` | All five cells and all difficulty/family/tag subsets reported below and in JSON |
| `uv run python -m experiments.cluster_stats` | Planning SE .03464; 95% half-width .07166; approximate 80% MDE .10082 |
| `uv run pytest tests experiments/E2E4/tests/test_fol.py -q` | 276 passed, 2 optional-backend skips |
| `uv run pytest experiments/E2E4/tests -q` | 15 passed (includes the FOL tests above; do not add these totals) |
| `uv run pytest experiments/E5/tests -q -k "not matched_pairs_all_cells"` | 10 passed, 1 deselected |
| `uv run pytest experiments/E5/tests -q -k matched_pairs_all_cells` | 1 passed, 10 deselected |
| `uv run python -m experiments.E5.check_harness --committed` | 32,424 prompts; Item/Condition/split contracts and committed preregistrations pass; 0 calls |
| `git diff --check` | Pass |

The E5 table entries are **dev / scored total items**. Each entry is half primary and half invalid-edge controls. Dev primary is 16 GOOD + 16 BAD per entry; scored primary is 48 GOOD + 48 BAD. Controls balance grounding but all have BAD approval labels.

| Attack family | Easy | Medium | Hard |
|---|---:|---:|---:|
| merged_vocabulary | 64 / 192 | 64 / 192 | 64 / 192 |
| scope_mismatch | 64 / 192 | 64 / 192 | 64 / 192 |
| unsupported_leaf | 64 / 192 | 64 / 192 | 64 / 192 |
| stale_evidence | 64 / 192 | 64 / 192 | 64 / 192 |

Vocabulary-family counts (templates and vocabularies are disjoint across splits):

| Vocabulary family | Split | Easy | Medium | Hard |
|---|---|---:|---:|---:|
| dev_cinder | dev | 128 | 128 | 128 |
| dev_loam | dev | 128 | 128 | 128 |
| score_mica | scored | 192 | 192 | 192 |
| score_reef | scored | 192 | 192 | 192 |
| score_twill | scored | 192 | 192 | 192 |
| score_umber | scored | 192 | 192 | 192 |

E5 totals: 768 dev / 2,304 scored, eight dev / 24 scored structural templates, two vocabularies per template. Frozen graph structures remain distinct under node renaming within every level. E2 totals: 144 dev / 288 scored, four dev / eight scored templates. E4 totals: 16 dev / 120 scored, four dev / twelve scored templates.

Leak audit: dev-trained logistic probes; 384 training and 1,152 scored primary items, balanced labels; chance = .500. Styles share the same body and only their label-constant first line is omitted. These are held-out probe accuracies, not judge outcomes or an upper bound for arbitrary classifiers.

| Cell | Char 1–5 | Char 6–12 | Word 1–3 | Counts / positions / dates / lengths |
|---|---:|---:|---:|---:|
| a | 0.5000 | 0.4896 | 0.5026 | 0.5035 |
| b | 0.5000 | 0.4896 | 0.5026 | 0.5035 |
| c | 0.5000 | 0.4974 | 0.4922 | 0.5043 |
| d | 0.5009 | 0.4983 | 0.4922 | 0.5035 |
| e | 0.5000 | 0.4991 | 0.4913 | 0.5035 |

All 576 scored GOOD/BAD primary pairs in every cell match exactly on character length, unigram multiset, record count, citation positions and date multiset. All 192 dev pairs also match. Hidden metadata and mechanical scope/sense answer flags are absent. The JSON also reports difficulty-specific and honest/forged-tag subset accuracies.

**Stale-evidence subset reported separately** (288 scored primary items; same probes trained on all dev families):

| Cell | Char 1–5 | Char 6–12 | Word 1–3 | Counts / positions / dates / lengths |
|---|---:|---:|---:|---:|
| a | 0.5000 | 0.4965 | 0.5000 | 0.5139 |
| b | 0.5000 | 0.4965 | 0.5000 | 0.5139 |
| c | 0.5000 | 0.5000 | 0.4931 | 0.5208 |
| d | 0.5000 | 0.5035 | 0.4861 | 0.5139 |
| e | 0.5000 | 0.5000 | 0.4931 | 0.5139 |

Every E4 item has exactly equal critique whitespace-token counts across all three arms. Mean 84.21 words in every arm; mean character counts differ (checked 616.41, prose 578.71, unchecked critic 597.18). This is a declared token proxy, not an exact model-token match.

Evidence files: `E5/counts.json`, `E2E4/counts.json`, `E5/leak-report.json`, `E5/power.json`, `material-validation.json` (artifact hashes and position histograms), and `harness-validation.json` (harness commit and prompt counts). Complete frozen datasets and proof archives are compressed; expanded large JSONL stays local and ignored.

## GAPS

No revised model pilot or scored run was made. The earlier hosted-judge floor has not been shown to disappear. Dev-only calibration with the separate small open-weight ladder remains necessary; E4 targets prose false approval of 20–60%.
The E5 10.08-point MDE is conditional on the reviewer’s variance assumptions; the planned useful-size threshold is 12 points, not 5. E2/E4 defer a confirmatory useful-size threshold until dev-based power is available. Cluster-t intervals still assume sufficiently independent, approximately normal template effects.
Cell e tests comparison and cross-checking of submitter annotations, not authenticated meanings or general forgery resistance. Scope, unsupported leaves, honest/forged merged vocabulary, and stale evidence require separate judge-result reporting. Dropped-premise controls test the listed local deduction; the root may have another proof using the omitted leaf.
Optional grammar backends `llguidance` and `xgrammar` were not installed (two skips). A diagnostic-only process listing was sandbox-denied: command `ps -eo pid,etime,%cpu,rss,args | rg "(E2E4.generate|python -m experiments)"`; error `zsh:1: operation not permitted: ps`. No required work remains blocked by that diagnostic failure.

## PLAN CHANGES

Adopt the revised preregistration drafts; require dev-only judge-ladder calibration and a committed judge/context/repetition manifest before scoring. Keep E2/E4 as mechanism/pilot studies until their precision is established; analyze E5 by structural template, difficulty, instruction style, grounding family and tag condition.
