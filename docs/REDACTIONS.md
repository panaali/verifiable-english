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

**Class C: the CI workflow file**, changed in its own commit after A and B (a commit that changes a workflow file
cannot publish its own Actions result): `.github/workflows/ve-job.yml` old sha256 `1a1c2e3692a5`, new `f3c85b580eb6`;
one comment line, the operations-repository path replaced by `<ops-repo>` with the same map; no pin cites it. The files
that fit neither class are in `docs/infra/relb-privacy-held-1126/classes.md`.
