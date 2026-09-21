# data/

Third-party datasets downloaded on 2026-09-21 for the E0/E1 dataset survey (`experiments/E0/SURVEY.md`). Nothing here was modified except: `AlloyTools/models` was cloned into `alloy-models/`, and only selected files of FRET were fetched.

The git clones contain their own `.git` directories. Do not `git add` them as-is (they would become embedded repositories); either gitignore them and re-download, or vendor only the needed files with the licence file.

| Subdir | Size (`du -sh`) | Source and version | Licence | Commit to this repo? |
|---|---|---|---|---|
| `folio/` | 3.2M | HF mirror `tasksource/folio` (sha 295b95fb4fe9be4ff3f933b73142d142cf6b2c97), FOLIO v2 train+validation; plus GitHub `Yale-LILY/FOLIO` @ 5d7bb84c (v0.0 data) | GitHub LICENSE: CC BY-SA 4.0. HF mirror card: `license: cc` (no version stated) | Prefer gitignore. Share-alike; the v2 files come from a third-party mirror because the official HF repo `yale-nlp/FOLIO` is gated (HTTP 401) |
| `proofwriter/` | 4.1M | HF mirror `tasksource/proofwriter` (sha ee4d22d49b8486786cbc01c0b6f6f6266e56f3bd), validation split only | Not stated on the mirror card. Upstream AllenAI licence not checked | No (licence not stated) |
| `cedar-examples/` | 2.7M | github.com/cedar-policy/cedar-examples @ c251f7d1ad171bd12dee5d1d7a1cceaec994518f | Apache-2.0 | Allowed by licence; gitignore the clone |
| `cedar-integration-tests/` | 7.6M | github.com/cedar-policy/cedar-integration-tests @ 1999ea249229e26cabb398a279fea721854a471d | Apache-2.0 | Allowed by licence; >5 MB (3.8 MB fuzz corpus tarball + 3.7 MB .git), gitignore |
| `gatekeeper-library/` | 13M | github.com/open-policy-agent/gatekeeper-library @ 22a40962f83268769bcec5dfe55e44b5a85c392a | Apache-2.0 | Allowed by licence; >5 MB, gitignore |
| `alloy-models/` | 892K | github.com/AlloyTools/models @ 886447d3369a9036aa4c3b49a82d7c557ab2e5f9 | Apache-2.0 | Allowed by licence; gitignore the clone |
| `clover/` | 11M | github.com/ChuyueSun/Clover @ 02144bec1bbf8d38951ef2df6f0c2870965a214e | MIT | Allowed by licence; >5 MB, gitignore |
| `fret/` | 1.6M | github.com/NASA-SW-VnV/fret @ cf0f913cc15c41705e803593297e89cd6056b839, four `caseStudies/` JSON files + README + LICENSE.pdf | Apache-2.0 (LICENSE.pdf, README) | Allowed by licence |

Total: 44M.

## Re-download

Run from this directory. `git clone --depth 1` fetches the current head; check out the commit above for an exact reproduction.

```sh
# FOLIO
mkdir -p folio proofwriter fret
git clone --depth 1 https://github.com/Yale-LILY/FOLIO.git folio/FOLIO-github
for f in README.md folio_v2_train.jsonl folio_v2_validation.jsonl; do
  curl -sS -L -o folio/tasksource_$f https://huggingface.co/datasets/tasksource/folio/resolve/main/$f
done

# ProofWriter (validation split of the tasksource mirror; reading it needs pyarrow)
curl -sS -L -o proofwriter/validation.parquet \
  https://huggingface.co/datasets/tasksource/proofwriter/resolve/main/data/validation-00000-of-00001-8f79b25dd5b0f2c3.parquet
curl -sS -L -o proofwriter/tasksource_README.md \
  https://huggingface.co/datasets/tasksource/proofwriter/resolve/main/README.md

# Policy and spec repositories
git clone --depth 1 https://github.com/cedar-policy/cedar-examples.git cedar-examples
git clone --depth 1 https://github.com/cedar-policy/cedar-integration-tests.git cedar-integration-tests
git clone --depth 1 https://github.com/open-policy-agent/gatekeeper-library.git gatekeeper-library
git clone --depth 1 https://github.com/AlloyTools/models.git alloy-models
git clone --depth 1 https://github.com/ChuyueSun/Clover.git clover

# NASA FRET case-study requirements (selected files only)
SHA=cf0f913cc15c41705e803593297e89cd6056b839
for p in caseStudies/FiniteStateMachine/fsm_reqts_and_vars.json caseStudies/LMCPS/LM_requirements.json \
         caseStudies/LiftPlusCruise/LPC_full_reqts_and_vars.json caseStudies/LiquidMixer/LM_reqts_and_vars.json \
         LICENSE.pdf README.md; do
  curl -sS -L -o fret/$(basename $p) https://raw.githubusercontent.com/NASA-SW-VnV/fret/$SHA/$p
done
echo $SHA > fret/COMMIT
```

## Failed or gated downloads

- `curl -L https://huggingface.co/datasets/yale-nlp/FOLIO/resolve/main/folio_v2_train.jsonl` -> HTTP 401 (gated dataset, no token available). Used the `tasksource/folio` mirror instead.
- `https://raw.githubusercontent.com/NASA-SW-VnV/fret/<sha>/LICENSE` -> HTTP 404; the licence is `LICENSE.pdf` (Apache-2.0), which was fetched.
- Not attempted: PURE requirements corpus, DafnyBench, the full AllenAI ProofWriter zip (CWA variants and logical forms are only there).
