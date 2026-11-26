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
