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
renamed: `docs/infra/tm-drain-vm1-idle/sar/cloud-vm-2.txt`. Nothing else in those lines changed. Four files keep a
machine name and are unchanged: three whose sha256 another file records
(`conformance/baseline-2026-09/REPLAY-EVIDENCE.md` in `docs/lean-first/oracle.json`;
`docs/infra/eff-20261103-1/evidence/mac-sa-no-exception-8ef1adbc.gate-result.json` in `tools/test-durations.json`;
`docs/test-architecture/manifest-ops/measure.py` in its `evidence/mutants-run.json`), which wait for a decision, and
`tools/platform_contract.py`, where the name is a match condition in code. `tests/test_public_tree_privacy.py` allows
exactly these hits while each file keeps its recorded sha256.

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
