# Redactions in sealed files

Sealed experiment directories keep a manifest of SHA-256 digests, and nothing a manifest lists is edited after sealing.
The files below are the exceptions. Each one named a private account directory of the people who ran the experiment,
and that name was replaced by the placeholder `<accounts-dir>`. Each manifest entry was updated to the new digest, and
`sha256sum -c MANIFEST.sha256` passes in both probe directories. No other byte changed. A word diff of the commit shows
one changed token per file. No reader saw these files: the reader sessions, items, prompts, answers and scores are
unchanged and keep their sealed digests.

| path | old sha256 | new sha256 | date | change | manifest entries updated |
|---|---|---|---|---|---|
| `experiments/authoring-gates/risk-wording-probe/seal.py` | `0ec0805e5bb17610ad01b0ad81d82b14a4508a71f2229ddc51fcd282efac64f2` | `ab3a294d2ce448071333a1c679dcb426b96a30c727b7209f60035f969defb57c` | 2026-11-25 | private names removed, nothing else changed | `experiments/authoring-gates/risk-wording-probe/MANIFEST.sha256` (line `seal.py`) |
| `experiments/authoring-gates/risk-wording-probe/readers.json` | `3d4e7e5dd35a56c2b4c82aa8068b9a6ddd32168e4c08a0018517ab7274c61525` | `7fb6b0182f817fa55e194a5d2aac694ce6d51f11afe63fff090ec36e0231de2f` | 2026-11-25 | private names removed, nothing else changed | `experiments/authoring-gates/risk-wording-probe/MANIFEST.sha256` (line `readers.json`); `experiments/authoring-gates/risk-wording-probe-2/MANIFEST.sha256` lists the same bytes under its own `readers.json` |
| `experiments/authoring-gates/risk-wording-probe-2/seal.py` | `d5ddd0fc09b653c3a5a09fea14cf0cb54082d6054ddcc66f762b073f6d1c99d9` | `5e2cd961bf0d086d12cc66b918e6e4f0302f2b3cefeda17067c0fa15eb74dc6f` | 2026-11-25 | private names removed, nothing else changed | `experiments/authoring-gates/risk-wording-probe-2/MANIFEST.sha256` (line `seal.py`) |
| `experiments/authoring-gates/risk-wording-probe-2/readers.json` | `3d4e7e5dd35a56c2b4c82aa8068b9a6ddd32168e4c08a0018517ab7274c61525` | `7fb6b0182f817fa55e194a5d2aac694ce6d51f11afe63fff090ec36e0231de2f` | 2026-11-25 | private names removed, nothing else changed | `experiments/authoring-gates/risk-wording-probe-2/MANIFEST.sha256` (line `readers.json`) |

## The one known exception: `experiments/T1c/PREREG-T1c.md`

Line 122 of the T1c preregistration names one private account directory. The file is left unchanged. Its sha256
(`56c3f7f08699369b26cd9c48c584d8fcefa9fa600723f27fffda74abf8cb4bb7`) is bound by an OpenTimestamps proof
(`experiments/T1c/timestamp.json`, `PREREG-T1c.md.ots`). It is also listed in `experiments/T1c/HASHES`, `HASHES-A1`
and `HASHES-A2`, and the counted T1c results depend on those as `freeze_sha256`. Changing one byte would break the
proof those results rest on. `tests/test_public_tree_privacy.py` allows this one hit only while the file keeps
exactly this sha256.

## Not a private value: `ve_experiments/t1c/transport.py`

This file was also pinned by the T1c manifests. Its only match was the Claude CLI's standard credentials file name,
which is public and names no account. It is unchanged, and the privacy checks no longer count a standard file name or
a generic prefix on its own.

## Host names (relb-privacy-hosts, 2026-11-26)

The names of the project's machines were replaced in the public tree by role names: `build-vm` (the main build VM),
`cloud-vm-2` and `cloud-vm-3` (the second and third cloud VMs) and `mac-runner` (the Mac test runner). One file was
renamed: `docs/infra/tm-drain-vm1-idle/sar/cloud-vm-2.txt`. Nothing else in those lines changed.

Closed by relb-privacy-hosts-code-1 (2026-11-26, orchestrator's word: none of these is timestamped outside or relied on
by a counted read; their pins are our own tool checks). Host name removed, nothing else changed, in:

| Path | Old sha256 | New sha256 | Pin |
|---|---|---|---|
| `conformance/baseline-2026-09/REPLAY-EVIDENCE.md` | `4bcd729790e40c2fa650598d1e66b16085a1dfa7fdec3fb17a46067068ac69d7` | `ad1412d86e9cac6e5b562b4953495b395448d6362f1f1516d3b28efd16984dba` | unchanged: `docs/lean-first/oracle.json` pins this file's bytes in the frozen oracle tree (a past commit), which `tools/lean_first_oracle.py --check` reads from git, not from the working tree |
| `docs/infra/eff-20261103-1/evidence/mac-sa-no-exception-8ef1adbc.gate-result.json` | `ec3ddc2cc5a6db7c0e44aeff831203f7f071cbb81700793d11c629ac887e58b6` | `0bde322343caabf4359feb710ed091a3b335921e5a654e4ca4bd6afda25c58f4` | updated: the `source` line of `tools/test-durations.json` |
| `docs/test-architecture/manifest-ops/measure.py` | `00ec49a821fa1543ce5c058afcce023138d2d1b25b88bf2c727e01991a596123` | `4244260223604a08a487a4de6bf588347a1982663c9a1d5edd8b508d8f652d9e` | updated: the five `source_sha256` of its mutants in `evidence/mutants-run.json` (the change is one docstring word; each mutant's `find` text still occurs once) |

In the gate record the name was two JSON string values (`runner.host` and the host part of `runner.job`); the file
still parses and no other value differs. `tools/platform_contract.py` no longer names the Mac runner: it reads the
name from `VE_MAC_RUNNER_HOST`, default `mac-runner`; its `aarch64` condition is unchanged, and the gate records and
summaries kept outside the tree classify the same with the variable unset (all of them also say `aarch64` or carry
the runner in their file name). `tests/test_public_tree_privacy.py` now allows no machine name anywhere.
This cleans the tree only: past commits, including the frozen oracle tree that `docs/lean-first/oracle.json` names,
still hold the old bytes until the history rewrite (relb-privacy-history-prep), which must remap that manifest.

Five historical evidence scripts under `docs/` match a machine name and now match its role name. Each one replays the
same way over the rewritten copies of its saved evidence in this tree. Run over raw records kept outside the tree,
which still carry the real names, it would select nothing until the records are mapped to the role names first:
`docs/infra/tm-build-timeout-1120/evidence/corr.py` (filters on the second cloud VM),
`docs/infra/tm-drain-vm1-idle/part0_measure.py` (keys each load series by the `sar/` file name, so the renamed
`sar/cloud-vm-2.txt` joins only records whose host reads `cloud-vm-2`), `docs/infra/eff-20261026-1/check.py`,
`docs/infra/speed-vocabpar/check.py` and `docs/infra/eff-20261030-1/chunk_table.py` (match the Mac runner in log
lines). Recorded patches and diffs under `docs/infra` (for example `ps1014-armshard-b1m1/seed-s*.patch`) no longer apply
byte for byte to the original scripts; they are records, and nothing applies them.

The test's digests guard against these names coming back; they do not hide them. A short role-like name can be
recovered from its digest by guessing.

## Owner names and private paths (relb-privacy-paths, 2026-11-26)

Account handles, the login name, the ssh user name and the repository owner (outside the public repository URL) were
replaced by role names: `worker-account-1` (the main account), `worker-account-2`, `worker-account-3` (one account
under two spellings; a handle's name parts alone map to its account), `operator`, `ssh-user` and `repo-owner`.
Private paths were replaced by placeholders: the operations repository by `<ops-repo>`, a VE checkout under the
home directory by `<repo>` (the rest of the path kept: `<repo>/tools/x.py`), another repository by
`<home>/code/<its name>`, the inputs directory by `<inputs>` and any other home directory that starts a path by
`<home>`. A `/home/` segment inside another path (a test sandbox under /tmp) is not a home directory and is kept.
One script did it (`docs/infra/relb-privacy-paths-1126/apply_privacy_map.py`, value-free: it reads every value from
the host); `prove_only_mapped.py` shows that every changed file equals the map applied to its old bytes (proof.txt).
Four T1c ledger archives were renamed (`experiments/T1c/results-*/ledgers-archive/*-judge-worker-account-2-*`).

Code that opens such a path reads an environment variable with a neutral default instead: `VE_OPS_REPO` (the
operations repository; `ve_experiments/colab.py`, paper/analysis, the probe and docs runners), `VE_CLAUDE_BIN`
(default `~/.local/bin/claude`), `VE_REPO`, `VE_COLAB_DIR`, `VE_HF_TOKEN_FILE` and `VE_P3_DATA` (default: this
repository's `data/`). Recorded logs, diffs and evidence keep their text with the placeholders; a recorded command
that names `<ops-repo>` or `<repo>` is a record, not something to replay as it stands.
`experiments/P1-deference/checks/provider-preflight.json` records the counter path of a finished study; it was a
path on another machine and now reads `<repo>/...`; nothing reruns that preflight.

Changed although pinned (its pin updated in the same commit):

| Path | Old sha256 | New sha256 | Pin |
|---|---|---|---|
| `docs/infra/eff-20261103-1/evidence/mac-sa-no-exception-8ef1adbc.gate-result.json` | `0bde322343caabf4359feb710ed091a3b335921e5a654e4ca4bd6afda25c58f4` | `d4f8fc54fea23096c5d382dc4eaba755723f83db399658dcbfd963c63e40713c` | the source line of `tools/test-durations.json` |

Held unchanged: 50 files whose exact bytes another file pins (a manifest sha256, a seal, a fingerprint, a timing
source or a blob id), and `.github/workflows/ve-job.yml` (one comment line naming the pinned-source path: a commit
that changes a workflow file cannot publish its own CI result, because the Actions token may not update workflow
files; it changes in a push that may). `tests/test_public_tree_privacy.py` lists each one in ALLOWED with its exact hit counts and
its sha256; the operations side decides them one by one (row relb-privacy-paths-held). Also left: the text inside 22
gzip files (the sweep scans text files only) and `usecases/pinned_sources.json`, whose `path` fields are
home-relative paths under the operations repository that the pinned-source tests open. This cleans the tree only:
past commits hold the old bytes until the history rewrite.

## Pinned files: class A kept, class B redacted and re-pinned (relb-privacy-held, 2026-11-26)

The 51 files relb-privacy-paths held because another file pins their exact bytes were sorted by one rule (orchestrator
word 2026-11-26), not one by one. The exact lists are in `docs/infra/relb-privacy-held-1126/` (classes.md, class-a.json).

**Class A: documented exceptions, byte-identical (4).** Each file's sha256 is in an outside OpenTimestamps chain, so
changing a byte would break a timestamp proof the counted T1c results rest on. Each keeps its hits and is allowed in
`tests/test_public_tree_privacy.py` only at exactly this sha256. The history rewrite keeps each byte-identical in every
commit (`class-a.json`).

| path | sha256 | in the chain of |
|---|---|---|
| `design/crypto-inspired-oversight.md` | `17bd3eb8c8f4` | experiments/T1c/HASHES, HASHES-A1, HASHES-A2 |
| `experiments/T1c/PREREG-T1c.md` | `56c3f7f08699` | experiments/T1c/HASHES, HASHES-A1, HASHES-A2; its own PREREG-T1c.md.ots |
| `experiments/T1c/README.md` | `5b351679fbff` | experiments/T1c/HASHES-A2 |
| `ve_experiments/t1c/run.py` | `fd3c47a8fb22` | experiments/T1c/HASHES-A2 |

**Class B: redacted and re-pinned (46).** Every other held file's pins live only in this repository's own manifests.
Each file was changed by the same reviewed map as relb-privacy-paths (`docs/infra/relb-privacy-paths-1126/apply_privacy_map.py`,
no new rule; the counts run gave exactly these 46 files and no other). In the same commit every pin that cited the old
digest (sha256, md5 or git blob id) now cites the new one, and no old digest is left in the tree outside this file's
history rows. Notes that record an operations-repository script by name (`md5.txt`, `sha256.txt`, `staged-sha256.txt`)
now give the digest of the redacted copy kept here. Checked: `sha256sum -c MANIFEST.sha256` in both probe directories;
`paper/sources/manifest.json` digests (paper/verify.py's check, 37 files); the B2 shadow check (`docs/test-speed-b2/shadow.py`);
`tests/test_english_lean_seal.py`, `tests/test_bluedot_grant.py`, `tests/test_fidmech_mutants.py`,
`tests/test_definitions_carried.py`, `tests/test_defs_carried_oos.py`, `tests/test_gate_durations.py`; and the
bluedot A/B answers tool (`ab_answers.py`, main against this tree: same answers). Old and new sha256, 12 hex digits:

| path | old sha256 | new sha256 | pins updated / derived files |
|---|---|---|---|
| `bench/PROFILE-GOLDEN.json` | `61f62c4aef76` | `89b3bf1aa27c` | `conformance/english-lean/corpus-seal.json` (sha256) |
| `bench/profile_english.py` | `dd252514a659` | `c23b3989993f` | `conformance/english-lean/corpus-seal.json` (sha256) |
| `conformance/english-lean/corpus-seal.json` | `5b63f700257c` | `b9ff530fbdff` | regenerated by its tool (`python -m conformance.english_lean_seal`; `--check`: 0 differences); it seals the bench, test and document files above |
| `docs/devtime/devtime-1/evidence/full-gate.json` | `49d5e2ccf175` | `7214674cec3c` | `docs/test-speed-b2/evidence/shadow.json` (sha256) |
| `docs/eff-tests/evidence/gate-450a401a-failed.json` | `7c510e5371a3` | `abf8d2c8a1b6` | `docs/test-speed-b2/evidence/shadow.json` (sha256) |
| `docs/eff-tests/evidence/gate-71088e15-passed.json` | `335bd8123559` | `7bb7a2fca665` | `docs/test-speed-b2/evidence/shadow.json` (sha256) |
| `docs/infra/actions-mismatch-scope-1120/mismatch-scope.sh.new-file` | `268f42097ff9` | `83cf4cd10729` | `docs/infra/actions-mismatch-scope-1120/md5.txt` (md5), `docs/infra/actions-mismatch-scope-narrow-1120/md5.txt` (md5) |
| `docs/infra/actions-mismatch-scope-1120/test_actions_mismatch_scope.py.new-file` | `54842850da9e` | `7ce7765ec6a8` | `docs/infra/actions-mismatch-scope-1120/md5.txt` (md5), `docs/infra/actions-mismatch-scope-narrow-1120/md5.txt` (md5) |
| `docs/infra/actions-mismatch-scope-narrow-1120/mismatch-scope.sh.new-amscope2.txt` | `661df26ae74d` | `6d260028ffbd` | `docs/infra/actions-mismatch-scope-narrow-1120/md5.txt` (md5), `docs/infra/cg-actions-shard-1121/md5.txt` (md5) |
| `docs/infra/actions-mismatch-scope-narrow-1120/test_actions_mismatch_scope.py.new-amscope2.txt` | `e14dd0ad824a` | `fa78e5f175d6` | `docs/infra/actions-mismatch-scope-narrow-1120/md5.txt` (md5) |
| `docs/infra/eff-20261103-1/evidence/arm-en-s6b-87475ae6-t724087.gate-record.json` | `fcf8fd73022e` | `26b1824dc0e4` | `tools/test-durations.json` (sha256) |
| `docs/infra/eff-20261103-1/evidence/arm-qt-a4-fd9f25f9-t712041.gate-record.json` | `a2412d400be9` | `266f9edd3208` | `tools/test-durations.json` (sha256) |
| `docs/infra/eff-20261103-1/evidence/arm-sc-5rdb-3564ccc8-t715994.gate-record.json` | `71226c63c438` | `56c70db64ff5` | `tools/test-durations.json` (sha256) |
| `docs/infra/released-main-1117/test_pick_released_main.py` | `b6d3e41479ff` | `6dc8c1942e01` | `docs/infra/released-main-1117/md5.txt` (md5) |
| `docs/infra/specregen-resolve-fallback-1120/test_merge_train_specregen.py.txt` | `5a77b087f650` | `4a3e5769e138` | `docs/infra/specregen-resolve-fallback-1120/sha256.txt` (sha256) |
| `docs/infra/tm-nightly-unknown-disposition-3/evidence/test_tm_nightly_unknown_disposition_3.py.staged` | `24d44e1c75a0` | `0bbb3de3538f` | `docs/infra/tm-nightly-unknown-disposition-3/evidence/staged-sha256.txt` (sha256) |
| `docs/infra/tmshard-harness-update/test-tmshard.zsh` | `ea2fa7608916` | `8c832c6f4a94` | `docs/infra/tmshard-harness-update/sha256.txt` (sha256) |
| `docs/lean-first/b11a/evidence/full-gate.json` | `1612295fa093` | `b61b4ee41f66` | `docs/test-speed-b1/evidence/shadow.json` (sha256), `docs/test-speed-b2/evidence/shadow.json` (sha256) |
| `docs/lean-first/b12/evidence/gate.json` | `457f7424dc54` | `b0c09daae5e7` | `docs/test-speed-b2/evidence/shadow.json` (sha256) |
| `docs/lean-first/b13b/evidence/gate.json` | `36b488440929` | `a89842da9433` | `docs/test-speed-b2/evidence/shadow.json` (sha256) |
| `docs/lean-first/b15a/evidence/full-gate.json` | `84ab3e133643` | `7d89bf5c494e` | `docs/test-speed-b1/evidence/shadow.json` (sha256) |
| `docs/lean-first/b16a/evidence/gate.json` | `a9bb23d6aa6d` | `f4f999fc8b6e` | `docs/test-speed-b1/evidence/shadow.json` (sha256) |
| `docs/lean-first/b16c/evidence/gate.json` | `899358b87739` | `77f26a0c0638` | `docs/test-speed-b1/evidence/shadow.json` (sha256) |
| `docs/lean-first/b17/evidence/gate.json` | `243f96ff0044` | `f63f2ba2a1cd` | `docs/test-speed-b1/evidence/shadow.json` (sha256), `docs/test-speed-b2/evidence/shadow.json` (sha256) |
| `docs/lean-first/b7/evidence/full-gate-first.json` | `14420caf76ec` | `90ec8e9db273` | `docs/test-speed-b1/evidence/shadow.json` (sha256) |
| `docs/lean-first/b7/evidence/full-gate.json` | `1998792871f6` | `ab96ff7a1ea0` | `docs/test-speed-b1/evidence/shadow.json` (sha256), `docs/test-speed-b2/evidence/shadow.json` (sha256) |
| `docs/readings-defaults/integration/gate-code.json` | `e23ee3814ace` | `feb8ca8a0a97` | `docs/test-speed-b1/evidence/shadow.json` (sha256), `docs/test-speed-b2/evidence/shadow.json` (sha256) |
| `docs/readings-defaults/rd6b/evidence/gate-code.json` | `1aa5dfef9d9e` | `29a359cabe26` | `docs/readings-defaults/rd6b/evidence/summary.json` (sha256) |
| `experiments/authoring-gates/risk-wording-probe-2/readers.json` | `7fb6b0182f81` | `982074ed4dd4` | `experiments/authoring-gates/risk-wording-probe-2/MANIFEST.sha256` (sha256), `experiments/authoring-gates/risk-wording-probe/MANIFEST.sha256` (sha256) |
| `experiments/authoring-gates/risk-wording-probe-2/seal.py` | `5e2cd961bf0d` | `f3f1886bada1` | `experiments/authoring-gates/risk-wording-probe-2/MANIFEST.sha256` (sha256) |
| `experiments/authoring-gates/risk-wording-probe/readers.json` | `7fb6b0182f81` | `982074ed4dd4` | `experiments/authoring-gates/risk-wording-probe-2/MANIFEST.sha256` (sha256), `experiments/authoring-gates/risk-wording-probe/MANIFEST.sha256` (sha256) |
| `experiments/authoring-gates/risk-wording-probe/seal.py` | `ab3a294d2ce4` | `80de2087daa9` | `experiments/authoring-gates/risk-wording-probe/MANIFEST.sha256` (sha256) |
| `paper/sources/e4-score-summary.json` | `4c73dfa83d5e` | `d3e2f2eacd4f` | `paper/sources/manifest.json` (sha256) |
| `paper/sources/local-ladder.md` | `8d7a1f0bc55f` | `39dbedd59b74` | `paper/sources/manifest.json` (sha256) |
| `paper/sources/planned-replication.md` | `c915eb829f91` | `e471c0f087ae` | `paper/sources/manifest.json` (sha256) |
| `paper/sources/process-log-excerpts.md` | `961f022b7ccb` | `8f091069b3d8` | `paper/sources/manifest.json` (sha256) |
| `paper/sources/process-log-v1.md` | `4512d9949ba0` | `fe39d48bb2c6` | `paper/sources/manifest.json` (sha256) |
| `paper/sources/process-operations.md` | `9273ffca5862` | `026047bd0ff1` | `paper/sources/manifest.json` (sha256) |
| `paper/sources/review-e5.md` | `110b592023fc` | `e754949d51ee` | `paper/sources/manifest.json` (sha256) |
| `tests/data/fidmech/fp1-inputs/safety-framework/build_document.py.txt` | `aebcec4ecc0f` | `d33c10cffeb4` | hashed whole into every fp-1 value: `tests/data/fidmech/fp1-golden.json` recomputed by uc-audit's own fp-1 code (which gives the old golden exactly on the old bytes); its provenance digest in `tests/test_fidmech_mutants.py` updated |
| `tests/test_assist.py` | `f318d286d03c` | `158cd72be2ba` | `conformance/english-lean/corpus-seal.json` (sha256); its fake token fixture literal is split in two (the export secret scan refuses a new blob that matches the token pattern; the value at run time is unchanged) |
| `tools/regen_generated.py` | `0c51f07bbf9d` | `4ce595b73171` | `docs/kernel/kb-1/trust-mutants.json` (sha256), `docs/kernel/kb-7/trust-mutants.json` (sha256) |
| `usecases/bluedot-grant/document.ve.md` | `e896a62b6772` | `f071e50bbbf1` | `conformance/english-lean/corpus-seal.json` (sha256), `docs/usecases/bluedot-grant/defs-repair-bluedot-grant-1119/ab-answers.json` (sha256); rebuilt with `usecases/bluedot-grant/build_document.py` (spans after the redacted note shift by 49 bytes) |
| `usecases/bluedot-grant/natural-view.md` | `10b79d9c5990` | `dd2d968efb4a` | `tests/data/defs_carried/known_cases.json` (blob) |
| `usecases/bluedot-grant/semantic_readings.py` | `5e9e4b17f1fa` | `ad870f976521` | its constant descriptions are front matter of `document.ve.md`, rebuilt with `build_document.py` (meaning ids of 8 units change: the descriptions are part of identity) |
| `usecases/bluedot-grant/source.md` | `a9fa225acce6` | `8c443dfe915a` | `tests/data/defs_carried/known_cases.json` (blob), `tests/test_bluedot_grant.py` (sha256), `usecases/bluedot-grant/README.md` (sha256); length 7,619 -> 7,570 bytes: `tests/test_bluedot_grant.py` length and coverage literals and the README's coverage table updated |

**Class C (the CI workflow file)** and the files that fit neither class are in `classes.md`.


## Compressed files and archives (relb-privacy-gz-roots, 2026-11-27)

The 22 tracked gzip files below held private values inside them, which a sweep of text blobs could not see (orchestrator
word 2026-11-26 item E). Each one was read in memory (never unpacked to disk). Every text member was rewritten with the
same reviewed replacement map as the plain files (`privacy-rewrite.py`; no new rule). Each file was then repacked
deterministically: gzip level 9, mtime 0, no stored file name; tar members sorted, uid/gid 0, no user or group names,
mtime 0, GNU format. Two independent runs gave byte-identical files. After the rewrite, a sweep of every member finds 0
values. None of these digests is in an outside timestamp chain (T1c `HASHES*`, `PREREG-HASHES.txt`, `.ots`), so there is
no class-A file here. Kinds are those of `tests/test_public_tree_privacy.py` (counts are hits before; values never
shown). Every pin that cited an old digest was updated in the same commit, and a tree-wide search finds 0 old sha256,
sha1, md5 or blob ids, apart from this table.

| path | old sha256 | new sha256 | kinds (hits before) | pins updated / note |
|---|---|---|---|---|
| `docs/eff-tests/evidence/suite-after-cold-junit.xml.gz` | `04422a28c86bfb8317859d4b7abc4480be78b3287581892240e83177988fc4ac` | `5912afa31bda1a7dd9194974115a4aaba8b626d06b9ec832bed7a15ffea9f3cf` | b 2, d 1, e 8 | XML: each placeholder written as `&lt;name&gt;` so the file still parses |
| `docs/eff-tests/evidence/suite-after-warm-junit.xml.gz` | `90d65977a49d1093b1c5468196e00681cad84fbbc23da7f227b050d6dc0b7e59` | `f33238ff151a4673924bcd43f0b0b1864ec357f5ea30eb8e163d1f4cafc0fcbe` | b 1, d 1, e 8 | XML: each placeholder written as `&lt;name&gt;` so the file still parses |
| `docs/eff-tests/evidence/suite-before-junit.xml.gz` | `c45cf91eb72ba62cb2a7ae62df0f07c2914703b1697a009f87d7fb5a9804d348` | `9f25975f9277482b2455221f9bcb033fcd67bf4d26c3b3bbf7b9f834b8952ed6` | b 1, d 1, e 8 | XML: each placeholder written as `&lt;name&gt;` so the file still parses |
| `docs/infra/eff-20261030-1/step1/logs.tar.gz` | `e57132fdbb8e1f574af57d6621911438374d3ac1ba14a0f97c4b27adf0335874` | `ccc81819f738bcca3d7bc74ef650ddf1601997ea7f1d48611e3b5143dc19f43a` | b 27, d 28, e 27 | none |
| `docs/infra/eff-20261030-1/step5/actions-select-run.log.gz` | `200bbdac36fab3bffdb0f9c4648ac6241306c0882178121921e73b06ed3a63f6` | `d97e43996a326bc8a62e0fbc4722b85d567aa5a41a87ba24a3aa89c52e4c0199` | e 41 | runner home, decider 0035Z item 1 (the GitHub-hosted runner home rewritten to `/home/<user>` inside this archive only) |
| `docs/infra/eff-20261030-1/step5/mac-logs.tar.gz` | `ff42673146a31bc92ea80a175e1d808fc0a5bb25395b617adb0c953ed1f31632` | `15826b65381ae4ef7701537a1290030d5027226447d76c8c58a2689ee3da07ce` | b 74, d 74, e 74 | none |
| `docs/lean-first/b15b/evidence/head2-ab.jsonl.gz` | `9d3a09ac4d04a059a338282f3532f970b83b8211b81a37e846021d77b04f01ef` | `6c7aa6b16c180418c2fafbce7fc1b546b7abc7059163cecb218f69100459a255` | b 1, e 1 | none |
| `docs/lean-first/b17/evidence/head-pilots-timeout.jsonl.gz` | `15645321d784a5728248526a284a5e67978b0733e5c67919f5661902b95fd08f` | `1d6c50657f05f6a747f1e552076c733d635c36ef8d85212fc873c27f7a2fa7e4` | b 1, e 1 | none |
| `docs/lean-first/b18/evidence/base-ab.jsonl.gz` | `fa68976ac2a3ce96d361b2ffe77bd02871dc7da4d0c91165493ac5bbc6df54ef` | `0116aa101de1ace535989bd15de49634113414bfbb848571571a07dfe54e1649` | b 3, e 6 | none |
| `docs/lean-first/b18/evidence/head-ab-initial.jsonl.gz` | `70f848f2d84277c1fd9bd76c26ccb8134545cf10ef0a0a8702d937b13756c783` | `0116aa101de1ace535989bd15de49634113414bfbb848571571a07dfe54e1649` | b 3, e 6 | none |
| `docs/lean-first/b18/evidence/head-ab.jsonl.gz` | `91b15a8c264f0dad2eae8363971786fd65d4b16623a89086cf1e30fb2da313f6` | `0116aa101de1ace535989bd15de49634113414bfbb848571571a07dfe54e1649` | b 3, e 6 | none |
| `docs/lean-first/document-corpus.json.gz` | `4d29be8bca6533e868887e8186c6e2d6e31deea9191b2d5ab60b0c9e6f3a1837` | `844d9b81c0191a9a1e228763c3615bafad643383588b1e046722a4887f9614b3` | b 1, e 5 | the bluedot-grant `document.ve.md` seed: its 3 redacted constant descriptions and body are part of identity, so its 59 meaning ids were recomputed with `ve.identity.meaning_id` (the method reproduces all 59 old ids on the old seed) and its 48 moved unit spans remapped through the body edits; the Lean-switch tests fail exactly as on main |
| `docs/readings-defaults/rd5/evidence/ab-rerun.json.gz` | `5eea2abd66b2ffa8a7745973a59c58d707fe34bc5e67b2e474cfd993418aaa91` | `b7f14044f9dc8402ae11e0d5c5e10e9f15c7a6716e7ae903e61deac12f0df7f5` | b 4, e 4 | none |
| `docs/readings-defaults/rd5/evidence/ab.json.gz` | `05392ae5dcdc2210ddc48654aa63631d29de91434727fc15e9cf96b8eda3c75e` | `3cd7b83fe770f84203e3ed72fd65b3ad2247408830f39e5995681270a1e84c5f` | b 7, e 7 | none |
| `docs/readings-defaults/rd6b/evidence/ab-retries.json.gz` | `621aef15b198c3f357ad06693a4f4e7b61c2cbd238d15b4c714347e534477c47` | `e5b7ab32683f3fa9a2d09527589e854e3d7defe1dedf26afb3de0fabd906583c` | b 3, e 3 | `docs/readings-defaults/rd6b/evidence/summary.json` (sha256, updated in place: no generator; its test checks it) |
| `docs/test-architecture/cutoff/evidence/recording-map.json.gz` | `0e98549790135c29334da1b5f472e62e130381b4fd56d3d01d49b0a1b61ccb08` | `f79aac8c12f0d8e6e7eaf13ab9efb8f940083e005de481ffe569bc15e392e5e9` | b 1 | `docs/test-architecture/cutoff/evidence/recording.json` `map_sha256` (updated in place: the recording run is not rerunnable) |
| `docs/test-architecture/slowtail/evidence/after-branch-d159baf4.log.gz` | `05149be4ad76aed149f108b42b923346aa090e84bba23eb8cf09a6e0407fc74b` | `f1a2c4d1da80310d35a0e6176ec7d57fe8b25e9f61e70ed9f351a797a8550b53` | b 32, d 7, e 32 | none |
| `docs/test-architecture/slowtail/evidence/before-main-85b20fcb.log.gz` | `2e1e4cba23ddecf46fb11acb3608dec90ab466ce6002d2eb9ac10f10eef81822` | `e6d6bf1ac2ee04a2c530f166463b8a17770b7b5e61c94de78ad6f77a3381ace2` | b 31, d 7, e 31 | none |
| `experiments/T1c/results-full/ledgers-archive/haiku-judge-worker-account-2-2026-09-23.jsonl.gz` | `0559f5fb0d6c223ce990d847e23580292684286d70268a5534a9107f3035929b` | `b04cbde788207fa28aea56061c8714399339af06d9f009437c381d9efaae5a71` | b 363 | none |
| `experiments/T1c/results-full/ledgers-archive/opus-judge-worker-account-2-2026-09-23.jsonl.gz` | `6370069537b86032629150739d357875305dc9b38547ce351fd98d91f5f5d2d5` | `a5671e7660954f1ae58f41d7267ec18da710e3462360ea79c20909983c9b0652` | b 240 | none |
| `experiments/T1c/results-gate/ledgers-archive/haiku-judge-worker-account-2-2026-09-23.jsonl.gz` | `fd171b9d57250d450f8f49d48912697f9bc645073b65bec74c88a346692ef951` | `e54a9c984b8411e23c12195b815add6aec340e5cc6565d24558872abf92d36f8` | b 120 | none |
| `experiments/T1c/results-gate/ledgers-archive/opus-judge-worker-account-2-2026-09-23.jsonl.gz` | `5a36042cc91c5584c658cdf6ebb9250e72bbb3c94ca97db25aa08c2b1a4972cc` | `bad29b6a334a44440a504c3eadbb517480498291d1556bd7d63663f23d7345b7` | b 120 | none |
