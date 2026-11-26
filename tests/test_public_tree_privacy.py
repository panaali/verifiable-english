"""relb-privacy-scrub, -hosts and -paths: no private operational detail in the public tree.

Scans every git-tracked text file (and every tracked path, as line 0) for six private-detail kinds and reports each
hit as path:line plus a MASKED value (first 2 characters + "***" + length); no private value is written in this file
or printed by it.

  a  account directory names: per-account Claude/Codex configuration directories, the accounts directory,
     CLAUDE_CONFIG_DIR set to a home-directory path;
  b  owner names and handles (relb-privacy-paths): the worker account handles and their name parts, the login name,
     the ssh user name and the repository owner, as sha256 hex digests of the lowercased names in DIGESTS["b"]. The
     owner is allowed inside the public repository URL (<owner>/verifiable-english), matched by its digest. The tree
     calls them worker-account-1..n, operator, ssh-user and repo-owner;
  c  e-mail addresses (allowed: example.com/.org, .invalid, the public noreply forms, the git@github.com clone form);
  d  host names of our machines (relb-privacy-hosts): the cloud VM names, the Mac runner's name and the build VM's
     hostname, as sha256 hex digests in DIGESTS["d"]. Their IP addresses are not listed: a digest of an IPv4
     address is reversed by trying all 2**32 addresses, and the tree holds none of them;
  e  private paths (relb-privacy-paths): a home directory that starts a path (/home/<user>, /Users/<user>; a /home/
     segment inside another path, such as a test sandbox, is not one), ~/code/<dir>, $HOME/code/<dir>, the inputs
     directory under the home directory and ~/.ve-* files. The tree writes <home>, <repo>, <ops-repo> and <inputs>;
  f  token or key file names: the project's key/token files, private web-app directories, a checkout's .env.

A digest kind matches lowercased word tokens of each line (the same tokenisers as the masked sweep) and of each tracked
path, so the names themselves never appear in the tree. A hyphenated token also yields its runs of 1 to 4 consecutive
hyphen-separated pieces, so a name glued to another word by a hyphen still matches. The digests guard against the
names coming back; they do not hide them (a short role-like name can be guessed from its digest).

ALLOWED lists the files that keep a hit on purpose, each with its exact hit count per kind and its reason: the T1c
preregistration (a timestamped digest the counted T1c results depend on) and the files relb-privacy-paths HELD because
another file pins their exact bytes (a sha256 or blob id in a manifest, a seal, a fingerprint or a timing source; row
relb-privacy-paths-held). A held file with more hits than listed fails (a new hit), and one with fewer fails too
(update the count), so the list only shrinks; each is held at its exact sha256. No file may hold a machine name
(kind d). This file holds no hit itself: its fixtures are joined at run time.
"""
import functools
import hashlib
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SELF = "tests/test_public_tree_privacy.py"

GENERIC = {
    "a": re.compile(r"\.claude-[A-Za-z0-9][\w.-]*|\.codex-[A-Za-z0-9][\w.-]*|\.[a-z]+-accounts\b"
                    r"|CLAUDE_CONFIG_DIR=[\"']?(?:[~/]|\$HOME|\$\{HOME)[^\s\"'`;)]*"),
    "c": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.(?:com|org|net|io|dev|edu|gov|ai|co|uk|de"
                    r"|me|app|ca|us|info|biz|xyz|invalid|local|test)\b"),
    # a home directory starting a path (not a /home/ segment inside another path), code and inputs directories under
    # the home directory, and ~/.ve-* files ("[s]" keeps this file's own text from matching)
    "e": re.compile(r"(?<![\w.$}/])(?:/home|/Users)/[A-Za-z0-9_][\w.-]*|(?:~|\$HOME|\$\{HOME\})/code/[\w.-]+"
                    r"|(?:~|\$HOME)/ve-input[s]\b|(?:~|\$HOME)/\.ve-[\w.-]+"),
    "f": re.compile(r"\.ve-[\w.-]*(?:key|token)\b(?:\.json)?|\.[a-z]+-private\b"
                    r"|\b[\w-]+/\.env\b"),
}
# value filters per kind: a match for which the filter is true is not a hit
EXEMPT = {
    "c": re.compile(r"@(?:[\w-]+\.)*(?:example\.com|example\.org|invalid)$|^noreply@anthropic\.com$"
                    r"|@users\.noreply\.github\.com$|^noreply@github\.com$|^git@github\.com$", re.I),
}
# sha256 hex digests of lowercased private names, matched against lowercased word tokens (rows above fill these)
DIGESTS = {
    # relb-privacy-paths (2026-11-26): the worker account handles (14, 13, 13 and 8 characters) and two name parts (6
    # each), the login name (6), the ssh user name (8) and the repository owner (7; allowed in the public URL).
    "b": frozenset({
        "1083ffafcdbd45c1cfca5e3703437d68b302805dd35be082c16974748c451a73",
        "14fbd8f96d602fbd59230decbef094d52943a12b7164b30d3b05f3cf6d8f9f65",
        "31fabf8de2d5fe5609b50a9d48154d4361101d5609c92fee0bc900daa8a96e0f",
        "380547094aa5e274f9ad6e016586a34d44810c40017cbe762d9099adc0184322",
        "72b6df644dae8dc31eb2bd7859295e92b8823bf9b23ba57b845c25afdace5b96",
        "b39466e305abda45366903f3565f3fad695a44765855e421691768f1164ef318",
        "b6614267a8f6464375addbb8af5fcba42951df7482b05a5da575879bfa38ea9f",
        "dce0d39921b78cbe795e647254e60b2df2be4af024df4f03e111059d325386cf",
        "f16f3103c0dc5e0c4ed458e6480434b19cc2f6c0b02a26f8c21e9e64b179e86d",
    }),
    # relb-privacy-hosts (2026-11-26): the build VM's hostname (15 characters), two cloud VM names (10 each) and the
    # Mac runner's name (8); the tree calls them build-vm, cloud-vm-2, cloud-vm-3 and mac-runner.
    "d": frozenset({
        "51961b9ef6b3fe38bca2fcc7472851174c866924d26ec36bc57517f116e22d4f",
        "a443a8d2a896752b0c83381f1564b01f35ee19749b5e0a9cc933f46e208cd3fd",
        "714b7fcf7e868b59876edbb2e79910f1048d285463f0755f7155250a5cd17e83",
        "a266b6064223b5a33b9f328c8a4e9aab50d3167379ecbb8371fb7c5af48238a6",
    }),
}
TOKENIZERS = [re.compile(p) for p in (r"[a-z0-9]+", r"[a-z0-9-]+", r"[a-z0-9.]+", r"[a-z0-9._-]+")]
# the public repository URL (or its owner/name slug): allowed when the owner part is the owner's digest
OWNER_DIGEST = "b39466e305abda45366903f3565f3fad695a44765855e421691768f1164ef318"
PUBLIC_URL = re.compile(r"(?:github\.com[/:])?([\w.-]+)/verifiable-english", re.I)

# A standard file name (the Claude CLI's credentials file) or a generic prefix alone is not a hit (orchestrator word
# 2026-11-25 on relb-privacy-s1b): it carries no private value. A path that names a private account directory still
# hits kind a, and the project's own key/token file names still hit kind f.
_PREREG = ("held, the one documented exception (docs/REDACTIONS.md; orchestrator word 2026-11-25): the timestamped T1c "
           "preregistration; its sha256 is OpenTimestamped and the counted T1c results depend on it")
_HELD = ("held unchanged (relb-privacy-paths 2026-11-26; follow-up row relb-privacy-paths-held, the orchestrator decides "
         "each): ")
ALLOWED = {
    "experiments/T1c/PREREG-T1c.md": ({'a': 1, 'b': 3}, _PREREG),
    "bench/PROFILE-GOLDEN.json": ({'b': 10, 'e': 10}, _HELD + "bytes pinned in conformance/english-lean/corpus-seal.json (sha256)"),
    "bench/profile_english.py": ({'b': 5, 'e': 5}, _HELD + "bytes pinned in conformance/english-lean/corpus-seal.json (sha256)"),
    "conformance/english-lean/corpus-seal.json": ({'b': 10, 'e': 10}, _HELD + "generated from the held bench/PROFILE-GOLDEN.json; its seal_id digests its own body"),
    "design/crypto-inspired-oversight.md": ({'b': 1}, _HELD + "bytes pinned in experiments/T1c/HASHES (sha256), experiments/T1c/HASHES-A1 (sha256) (+1)"),
    "docs/devtime/devtime-1/evidence/full-gate.json": ({'b': 101, 'e': 22}, _HELD + "bytes pinned in docs/test-speed-b2/evidence/shadow.json (sha256)"),
    "docs/eff-tests/evidence/gate-450a401a-failed.json": ({'b': 102, 'e': 23}, _HELD + "bytes pinned in docs/test-speed-b2/evidence/shadow.json (sha256)"),
    "docs/eff-tests/evidence/gate-71088e15-passed.json": ({'b': 101, 'e': 22}, _HELD + "bytes pinned in docs/test-speed-b2/evidence/shadow.json (sha256)"),
    "docs/infra/actions-mismatch-scope-1120/mismatch-scope.sh.new-file": ({'b': 1, 'e': 1}, _HELD + "bytes pinned in docs/infra/actions-mismatch-scope-1120/md5.txt (md5), docs/infra/actions-mismatch-scope-narrow-1120/md5.txt (md5)"),
    "docs/infra/actions-mismatch-scope-1120/test_actions_mismatch_scope.py.new-file": ({'b': 3, 'e': 4}, _HELD + "bytes pinned in docs/infra/actions-mismatch-scope-1120/md5.txt (md5), docs/infra/actions-mismatch-scope-narrow-1120/md5.txt (md5)"),
    "docs/infra/actions-mismatch-scope-narrow-1120/mismatch-scope.sh.new-amscope2.txt": ({'b': 1, 'e': 1}, _HELD + "bytes pinned in docs/infra/actions-mismatch-scope-narrow-1120/md5.txt (md5), docs/infra/cg-actions-shard-1121/md5.txt (md5)"),
    "docs/infra/actions-mismatch-scope-narrow-1120/test_actions_mismatch_scope.py.new-amscope2.txt": ({'b': 5, 'e': 6}, _HELD + "bytes pinned in docs/infra/actions-mismatch-scope-narrow-1120/md5.txt (md5)"),
    "docs/infra/eff-20261103-1/evidence/arm-en-s6b-87475ae6-t724087.gate-record.json": ({'e': 24}, _HELD + "bytes pinned in tools/test-durations.json (sha256)"),
    "docs/infra/eff-20261103-1/evidence/arm-qt-a4-fd9f25f9-t712041.gate-record.json": ({'e': 24}, _HELD + "bytes pinned in tools/test-durations.json (sha256)"),
    "docs/infra/eff-20261103-1/evidence/arm-sc-5rdb-3564ccc8-t715994.gate-record.json": ({'e': 24}, _HELD + "bytes pinned in tools/test-durations.json (sha256)"),
    "docs/infra/released-main-1117/test_pick_released_main.py": ({'b': 16, 'e': 1}, _HELD + "bytes pinned in docs/infra/released-main-1117/md5.txt (md5)"),
    "docs/infra/specregen-resolve-fallback-1120/test_merge_train_specregen.py.txt": ({'b': 1, 'e': 4}, _HELD + "bytes pinned in docs/infra/specregen-resolve-fallback-1120/sha256.txt (sha256)"),
    "docs/infra/tm-nightly-unknown-disposition-3/evidence/test_tm_nightly_unknown_disposition_3.py.staged": ({'b': 1, 'e': 1}, _HELD + "bytes pinned in docs/infra/tm-nightly-unknown-disposition-3/evidence/staged-sha256.txt (sha256)"),
    "docs/infra/tmshard-harness-update/test-tmshard.zsh": ({'b': 1, 'e': 1}, _HELD + "bytes pinned in docs/infra/tmshard-harness-update/sha256.txt (sha256)"),
    "docs/lean-first/b11a/evidence/full-gate.json": ({'b': 16, 'e': 20}, _HELD + "bytes pinned in docs/test-speed-b1/evidence/shadow.json (sha256), docs/test-speed-b2/evidence/shadow.json (sha256)"),
    "docs/lean-first/b12/evidence/gate.json": ({'b': 16, 'e': 20}, _HELD + "bytes pinned in docs/test-speed-b2/evidence/shadow.json (sha256)"),
    "docs/lean-first/b13b/evidence/gate.json": ({'b': 101, 'e': 22}, _HELD + "bytes pinned in docs/test-speed-b2/evidence/shadow.json (sha256)"),
    "docs/lean-first/b15a/evidence/full-gate.json": ({'b': 7, 'e': 10}, _HELD + "bytes pinned in docs/test-speed-b1/evidence/shadow.json (sha256)"),
    "docs/lean-first/b16a/evidence/gate.json": ({'b': 16, 'e': 20}, _HELD + "bytes pinned in docs/test-speed-b1/evidence/shadow.json (sha256)"),
    "docs/lean-first/b16c/evidence/gate.json": ({'b': 90, 'e': 10}, _HELD + "bytes pinned in docs/test-speed-b1/evidence/shadow.json (sha256)"),
    "docs/lean-first/b17/evidence/gate.json": ({'b': 19, 'e': 23}, _HELD + "bytes pinned in docs/test-speed-b1/evidence/shadow.json (sha256), docs/test-speed-b2/evidence/shadow.json (sha256)"),
    "docs/lean-first/b7/evidence/full-gate-first.json": ({'b': 16, 'e': 20}, _HELD + "bytes pinned in docs/test-speed-b1/evidence/shadow.json (sha256)"),
    "docs/lean-first/b7/evidence/full-gate.json": ({'b': 16, 'e': 20}, _HELD + "bytes pinned in docs/test-speed-b1/evidence/shadow.json (sha256), docs/test-speed-b2/evidence/shadow.json (sha256)"),
    "docs/readings-defaults/integration/gate-code.json": ({'b': 16, 'e': 20}, _HELD + "bytes pinned in docs/test-speed-b1/evidence/shadow.json (sha256), docs/test-speed-b2/evidence/shadow.json (sha256)"),
    "docs/readings-defaults/rd6b/evidence/gate-code.json": ({'b': 101, 'e': 22}, _HELD + "bytes pinned in docs/readings-defaults/rd6b/evidence/summary.json (sha256)"),
    "experiments/T1c/README.md": ({'b': 3, 'e': 1}, _HELD + "bytes pinned in experiments/T1c/HASHES-A2 (sha256)"),
    "experiments/authoring-gates/risk-wording-probe-2/readers.json": ({'b': 2, 'e': 3}, _HELD + "bytes pinned in docs/REDACTIONS.md (sha256), experiments/authoring-gates/risk-wording-probe-2/MANIFEST.sha256 (sha256) (+1)"),
    "experiments/authoring-gates/risk-wording-probe-2/seal.py": ({'b': 3, 'e': 3}, _HELD + "bytes pinned in docs/REDACTIONS.md (sha256), experiments/authoring-gates/risk-wording-probe-2/MANIFEST.sha256 (sha256)"),
    "experiments/authoring-gates/risk-wording-probe/readers.json": ({'b': 2, 'e': 3}, _HELD + "bytes pinned in docs/REDACTIONS.md (sha256), experiments/authoring-gates/risk-wording-probe-2/MANIFEST.sha256 (sha256) (+1)"),
    "experiments/authoring-gates/risk-wording-probe/seal.py": ({'b': 3, 'e': 3}, _HELD + "bytes pinned in docs/REDACTIONS.md (sha256), experiments/authoring-gates/risk-wording-probe/MANIFEST.sha256 (sha256)"),
    "paper/sources/e4-score-summary.json": ({'b': 2, 'e': 2}, _HELD + "bytes pinned in paper/sources/manifest.json (sha256)"),
    "paper/sources/local-ladder.md": ({'e': 3}, _HELD + "bytes pinned in paper/sources/manifest.json (sha256)"),
    "paper/sources/planned-replication.md": ({'e': 1}, _HELD + "bytes pinned in paper/sources/manifest.json (sha256)"),
    "paper/sources/process-log-excerpts.md": ({'e': 8}, _HELD + "bytes pinned in paper/sources/manifest.json (sha256)"),
    "paper/sources/process-log-v1.md": ({'e': 2}, _HELD + "bytes pinned in paper/sources/manifest.json (sha256)"),
    "paper/sources/process-operations.md": ({'e': 2}, _HELD + "bytes pinned in paper/sources/manifest.json (sha256)"),
    "paper/sources/review-e5.md": ({'b': 1}, _HELD + "bytes pinned in paper/sources/manifest.json (sha256)"),
    "tests/data/fidmech/fp1-inputs/safety-framework/build_document.py.txt": ({'e': 1}, _HELD + "hashed whole into every fp-1 value of tests/data/fidmech fp1-golden.json"),
    "tests/test_assist.py": ({'b': 1, 'e': 1}, _HELD + "bytes pinned in conformance/english-lean/corpus-seal.json (sha256)"),
    "tools/regen_generated.py": ({'e': 2}, _HELD + "bytes pinned in docs/kernel/kb-1/trust-mutants.json (sha256), docs/kernel/kb-7/trust-mutants.json (sha256)"),
    "usecases/bluedot-grant/document.ve.md": ({'b': 4, 'e': 5}, _HELD + "bytes pinned in conformance/english-lean/corpus-seal.json (sha256), docs/usecases/bluedot-grant/defs-repair-bluedot-grant-1119/ab-answers.json (sha256)"),
    "usecases/bluedot-grant/natural-view.md": ({'b': 1, 'e': 2}, _HELD + "bytes pinned in tests/data/defs_carried/known_cases.json (blob)"),
    "usecases/bluedot-grant/semantic_readings.py": ({'b': 3, 'e': 3}, _HELD + "builds the front matter of the held usecases/bluedot-grant/document.ve.md (tests/test_bluedot_grant.py)"),
    "usecases/bluedot-grant/source.md": ({'b': 1, 'e': 2}, _HELD + "bytes pinned in OPS:reviews/orchestrator-mistakes-1123/transcript/orchestrator-2026-10-01.txt (sha256), OPS:reviews/progress-review-1121/transcript/orchestrator-2026-10-01.txt (sha256) (+3)"),
    "ve_experiments/t1c/run.py": ({'b': 1}, _HELD + "bytes pinned in experiments/T1c/HASHES-A2 (sha256)"),
}
# A held file is held at exactly these bytes: any change to it must come back to review.
HELD_SHA256 = {
    "bench/PROFILE-GOLDEN.json": "61f62c4aef76b22f6982f07049da7cef933973cd9e2a5df406912a164e122b0e",
    "bench/profile_english.py": "dd252514a6597efa74ca94c6f62c9f621dda1a6910d25a5ce7bf189ce7f295c1",
    "conformance/english-lean/corpus-seal.json": "5b63f700257cfde1593b0b844c2a7239920f6d49e576ad720d28d9cc136881d5",
    "design/crypto-inspired-oversight.md": "17bd3eb8c8f43f6762c9b10accbcc7e683d37d8ec07f1a992cfa6367fa8dfda8",
    "docs/devtime/devtime-1/evidence/full-gate.json": "49d5e2ccf1751f24011e031ab0100b5b3f4d6d5c758606878ff595a48157feb1",
    "docs/eff-tests/evidence/gate-450a401a-failed.json": "7c510e5371a36db6e11d620a613a1ced053b648b830b3e8cd61bb4cee0adf2da",
    "docs/eff-tests/evidence/gate-71088e15-passed.json": "335bd81235599041ec184dbf5a5b8842078b1ec41ce8dfcb0dcf0a4681b0a3a8",
    "docs/infra/actions-mismatch-scope-1120/mismatch-scope.sh.new-file": "268f42097ff9e5f100df9b813ba595cf4cb1d4470839da46ce5afabf17d27aba",
    "docs/infra/actions-mismatch-scope-1120/test_actions_mismatch_scope.py.new-file": "54842850da9ec08366892854fb110d3d57d739622d87a1f55eea80f9b6b33c92",
    "docs/infra/actions-mismatch-scope-narrow-1120/mismatch-scope.sh.new-amscope2.txt": "661df26ae74d9f7dd9fc5b6080b4df4ec6cb3fdebb5e169d6daa2525a7209146",
    "docs/infra/actions-mismatch-scope-narrow-1120/test_actions_mismatch_scope.py.new-amscope2.txt": "e14dd0ad824a1e3c7300e2e53891eda274c35e3a76c6785d9cf4c9771986bc29",
    "docs/infra/eff-20261103-1/evidence/arm-en-s6b-87475ae6-t724087.gate-record.json": "fcf8fd73022e43a91ea5dfe12d2b2f3410ee25382934108970636123e9831687",
    "docs/infra/eff-20261103-1/evidence/arm-qt-a4-fd9f25f9-t712041.gate-record.json": "a2412d400be9da05c586fc421af072a00332ef4f0b8b277172c8a4f93588462d",
    "docs/infra/eff-20261103-1/evidence/arm-sc-5rdb-3564ccc8-t715994.gate-record.json": "71226c63c4383909b3a0badeda1cb5d33395038c5b7c927c4d1d6ed2a070c2f9",
    "docs/infra/released-main-1117/test_pick_released_main.py": "b6d3e41479ff110237c5f0ec388f2d9eb60b5d3a2080f84477f3184b98522488",
    "docs/infra/specregen-resolve-fallback-1120/test_merge_train_specregen.py.txt": "5a77b087f650711e6e13c1aa632e5f13f654bd11cb3c0fbf43a1461e9a3948c6",
    "docs/infra/tm-nightly-unknown-disposition-3/evidence/test_tm_nightly_unknown_disposition_3.py.staged": "24d44e1c75a06d6937f86b6f1748dfcf4fc767a70c8987ce8b365e46af8201a1",
    "docs/infra/tmshard-harness-update/test-tmshard.zsh": "ea2fa7608916c2e9d738a41ce42bedb454c37fb1ed679660f7348d19a05c588d",
    "docs/lean-first/b11a/evidence/full-gate.json": "1612295fa09394a87e67bc7c60eedd333e1b374409ff844e9405d235c6313e03",
    "docs/lean-first/b12/evidence/gate.json": "457f7424dc54049b329b4b1ce91147cb1239739201d1a6196e0fe14579318e59",
    "docs/lean-first/b13b/evidence/gate.json": "36b4884409298bebe42aa62516df0735c60a9548a293b8e885569d9cbbea424f",
    "docs/lean-first/b15a/evidence/full-gate.json": "84ab3e13364330766eae31f46fdb13b7dba3fb534f1d034f40de2016606c621f",
    "docs/lean-first/b16a/evidence/gate.json": "a9bb23d6aa6d123f228109e20d3f8e1691ad6264cc0741db0033d45e0be41394",
    "docs/lean-first/b16c/evidence/gate.json": "899358b877393aa7aca4bf51b40b1ddedaaf42de966310d2dfd8692b100d3bd7",
    "docs/lean-first/b17/evidence/gate.json": "243f96ff004465c12c53fba9b1776b79d09f322ad6b2fdd81a921fb4a2b75d4f",
    "docs/lean-first/b7/evidence/full-gate-first.json": "14420caf76ecfcf91550b8605ac8d883f4c396a89255a29547ef54fc022bdfe3",
    "docs/lean-first/b7/evidence/full-gate.json": "1998792871f672c380ea6f33c8133f3c6872681e9d2b4074689641ba6daa085a",
    "docs/readings-defaults/integration/gate-code.json": "e23ee3814ace39d9a65eaec9eb61b6f9bdad42a816845f6316f11150bd3c6fc9",
    "docs/readings-defaults/rd6b/evidence/gate-code.json": "1aa5dfef9d9e528d56ebdedb2510732ed3f8ad4dea6aef2ca3ec079cd04bd90f",
    "experiments/T1c/PREREG-T1c.md": "56c3f7f08699369b26cd9c48c584d8fcefa9fa600723f27fffda74abf8cb4bb7",
    "experiments/T1c/README.md": "5b351679fbffd75d3f0df508afcbb64cf13ad6b92172ccec589019d4f612d5a1",
    "experiments/authoring-gates/risk-wording-probe-2/readers.json": "7fb6b0182f817fa55e194a5d2aac694ce6d51f11afe63fff090ec36e0231de2f",
    "experiments/authoring-gates/risk-wording-probe-2/seal.py": "5e2cd961bf0d086d12cc66b918e6e4f0302f2b3cefeda17067c0fa15eb74dc6f",
    "experiments/authoring-gates/risk-wording-probe/readers.json": "7fb6b0182f817fa55e194a5d2aac694ce6d51f11afe63fff090ec36e0231de2f",
    "experiments/authoring-gates/risk-wording-probe/seal.py": "ab3a294d2ce448071333a1c679dcb426b96a30c727b7209f60035f969defb57c",
    "paper/sources/e4-score-summary.json": "4c73dfa83d5e8b6eb3bfee5d5741e6665c808726bdd36283833ede73e48e9d31",
    "paper/sources/local-ladder.md": "8d7a1f0bc55f46605af049a8fe68f9cd475a7fdca5a0c3e150c13e070bf85848",
    "paper/sources/planned-replication.md": "c915eb829f91080a7d244e6e7a65d30904143b565c2111e17102973bcd4e438a",
    "paper/sources/process-log-excerpts.md": "961f022b7ccbc75f946e857a395f3b71941d0639be81ff2f4c78d091f5643893",
    "paper/sources/process-log-v1.md": "4512d9949ba0d186f8688c96c7d1727e273cb2713997bd5a151f04c0691404af",
    "paper/sources/process-operations.md": "9273ffca58624fbda00e293c420da334516da6dab2ea7e9f3f6bda1bca9dc4e3",
    "paper/sources/review-e5.md": "110b592023fc2c84d7c0d19a61eff29192b62e8a8e6adbbc86d8f55ce58bab60",
    "tests/data/fidmech/fp1-inputs/safety-framework/build_document.py.txt": "aebcec4ecc0f0cc67d49841bc2483d36d51969866b0570cdd9b0aae9ea47d249",
    "tests/test_assist.py": "f318d286d03c1f3d7d6952ffb944beb7a21a4f83e6761003532d1ba6819fc3fc",
    "tools/regen_generated.py": "0c51f07bbf9d93ac239cd56fd72124395ec8134409a76ad64cc8a3a2b4dd360d",
    "usecases/bluedot-grant/document.ve.md": "e896a62b6772dc1d004111452d6bc4f61a1b17c20ccecd6242c31e584a65710f",
    "usecases/bluedot-grant/natural-view.md": "10b79d9c5990d505162222b58d7c718a51f7c093ccae035b3ed4164c1431a024",
    "usecases/bluedot-grant/semantic_readings.py": "5e9e4b17f1fa5bb0daecfc02b2153020b916e7141de48cae41f7f66e8d3bbf4c",
    "usecases/bluedot-grant/source.md": "a9fa225acce6a684af7519c9c6fa82a20fc3a7e685a04b7e1a4bac88a0d6ed22",
    "ve_experiments/t1c/run.py": "fd3c47a8fb2245d53d331fda5ae913b91ed18cd28df0f4eb983140d8311d62cc",
}


def _digest(value):
    return hashlib.sha256(value.lower().encode()).hexdigest()


def mask(value):
    return f"{value[:2]}***({len(value)})"


def kinds():
    return sorted(GENERIC) + sorted(k for k, v in DIGESTS.items() if v)


def _tokens(low):
    out = set()
    for t in TOKENIZERS:
        out.update(m.group(0).strip(".-_") for m in t.finditer(low))
    for tok in [t for t in out if "-" in t]:
        parts = [p for p in tok.split("-") if p]
        out.update("-".join(parts[i:j]) for i in range(len(parts)) for j in range(i + 1, min(i + 4, len(parts)) + 1))
    return out


def scan_line(line):
    """[(kind, value)] for one line."""
    hits = []
    for kind, rx in GENERIC.items():
        for m in rx.finditer(line):
            v = m.group(0)
            if kind in EXEMPT and EXEMPT[kind].search(v):
                continue
            hits.append((kind, v))
    active = {k: v for k, v in DIGESTS.items() if v}
    if active:
        line = PUBLIC_URL.sub(lambda m: " " if _digest(m.group(1)) == OWNER_DIGEST else m.group(0), line)
        for t in _tokens(line.lower()):
            d = hashlib.sha256(t.encode()).hexdigest()
            hits.extend((k, t) for k, v in active.items() if d in v)
    return hits


def path_hits(rel):
    """[(kind, (path, 0, masked value))] for a tracked path itself (a file named after a host is a hit too)."""
    return [(kind, (rel, 0, mask(v))) for kind, v in scan_line(rel)]


@functools.lru_cache(maxsize=1)
def tree_hits():
    """{kind: [(path, line, masked value)]} over every tracked text file."""
    try:
        out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"], capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("not a git checkout")
    hits = {}
    for rel in out.decode("utf-8", "replace").split("\0"):
        p = ROOT / rel
        if not rel:
            continue
        for kind, h in path_hits(rel):
            hits.setdefault(kind, []).append(h)
        if p.is_symlink() or not p.is_file():
            continue
        data = p.read_bytes()
        if b"\0" in data[:8000]:
            continue
        for i, line in enumerate(data.decode("utf-8", "replace").splitlines(), 1):
            for kind, v in scan_line(line):
                hits.setdefault(kind, []).append((rel, i, mask(v)))
    return hits


@pytest.mark.parametrize("kind", kinds())
def test_no_private_detail_of_kind_in_the_tracked_tree(kind):
    bad = [h for h in tree_hits().get(kind, []) if kind not in ALLOWED.get(h[0], ({}, ""))[0]]
    assert not bad, f"{len(bad)} kind-({kind}) hits (masked): " + "; ".join(f"{p}:{n} {v}" for p, n, v in bad[:40])


def test_every_held_file_has_exactly_its_listed_hits():
    off = []
    for path, (counts, _reason) in ALLOWED.items():
        for k, want in counts.items():
            got = [h for h in tree_hits().get(k, []) if h[0] == path]
            if len(got) != want:
                off.append(f"{path} ({k}): {len(got)} hits, ALLOWED says {want}: "
                           + "; ".join(f":{n} {v}" for _p, n, v in got[:5]))
    assert not off, "held files off their counts (a new hit, or update/remove the entry): " + " | ".join(off)


def test_every_held_file_is_held_at_its_exact_bytes():
    assert set(HELD_SHA256) == set(ALLOWED)
    for path, digest in HELD_SHA256.items():
        got = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        assert got == digest, f"{path} changed (sha256 {got[:12]}...): a held file comes back to review before its entry moves"


def test_no_file_is_allowed_a_machine_name():
    assert not [path for path, (counts, _reason) in ALLOWED.items() if "d" in counts]


def test_this_file_holds_no_hit():
    assert SELF not in ALLOWED
    assert not [h for hs in tree_hits().values() for h in hs if h[0] == SELF]


def _j(*parts):
    """Join fixture pieces at run time, so no fixture is itself a hit in this file."""
    return "".join(parts)


@pytest.mark.parametrize("line, kind", [
    (_j("cfg=~/.claude", "-someone"), "a"),
    (_j("export CODEX_HOME=$HOME/.codex", "-two"), "a"),
    (_j("ls ~/.my", "-accounts/x"), "a"),
    (_j("CLAUDE_CONFIG_DIR", "=~/x claude -p"), "a"),
    (_j("Author: A <someone", "@mail.test>"), "c"),
    (_j("token in ~/.ve", "-some-token"), "f"),
    (_j("key at ~/.ve", "-thing-key.json"), "f"),
    (_j("cat ~/.team", "-accounts/claude-x/.credentials.json"), "a"),  # a private dir with the standard name
    (_j("under .site", "-private/"), "f"),
    (_j("source ops-repo/", ".env"), "f"),
    (_j("cd /ho", "me/someone/x"), "e"),
    (_j("ls /Us", "ers/someone"), "e"),
    (_j('"/ho', 'me/runner/work/x"'), "e"),
    (_j("C=${X:-/ho", "me/someone/.local/bin/claude}"), "e"),
    (_j("cd ~/co", "de/some-repo/tools"), "e"),
    (_j("cd $HOME/co", "de/x"), "e"),
    (_j("cd ${HOME}/co", "de/x"), "e"),
    (_j("ls ~/ve-in", "puts/a"), "e"),
    (_j("cat ~/.ve", "-notes"), "e"),
])
def test_the_patterns_find_each_kind(line, kind):
    assert kind in {k for k, _ in scan_line(line)}


@pytest.mark.parametrize("line", [
    "mail a@example.com or b@x.example.org or c@host.invalid",
    "Co-Authored-By: X <noreply@anthropic.com>; 1+x@users.noreply.github.com; git@github.com:o/r.git",
    _j("CLAUDE_CONFIG_DIR", "=$cfg claude -p"),
    "Path.home() / f'.claude-{label}'",
    "path = (config or Path.home() / '.claude') / '.credentials.json'",
    "the CLI keeps its login in .credentials.json",
    _j("/tmp/sandbox-x/ho", "me/fake/killed"),
    _j("zsh $T/ho", "me/tm-nightly.sh --once"),
    "see <home>/.local/bin/claude, <repo>/tools/x.py, <ops-repo>/reviews/a.md, <inputs>/b, <home>/code/other-repo",
    "pytest-of-operator, worker-account-2 and ssh-user, repo-owner",
])
def test_public_forms_are_not_hits(line):
    assert scan_line(line) == []


def test_a_digest_kind_matches_tokens_without_the_name_in_the_tree(monkeypatch):
    monkeypatch.setitem(DIGESTS, "d", frozenset({hashlib.sha256(b"build-host-zz").hexdigest()}))
    assert ("d", "build-host-zz") in scan_line("ssh Build-Host-ZZ uptime")
    assert scan_line("ssh build-host-zy uptime") == []


def test_the_host_digest_set_is_four_sha256_hex_digests():
    for d in DIGESTS["d"]:
        assert re.fullmatch(r"[0-9a-f]{64}", d)
    assert len(DIGESTS["d"]) == 4


def test_long_lines_are_scanned_to_their_end(monkeypatch):
    monkeypatch.setitem(DIGESTS, "d", frozenset({hashlib.sha256(b"build-host-zz").hexdigest()}))
    assert ("d", "build-host-zz") in scan_line("x" * 30000 + ' "where": "build-host-zz"')


@pytest.mark.parametrize("line", ["old build-host-zz-old box", "logs/ssh-build-host-zz.txt", "x_build-host-zz_y"])
def test_a_host_name_glued_by_a_hyphen_still_matches(monkeypatch, line):
    monkeypatch.setitem(DIGESTS, "d", frozenset({hashlib.sha256(b"build-host-zz").hexdigest()}))
    assert ("d", "build-host-zz") in scan_line(line)


def test_tracked_paths_are_scanned(monkeypatch):
    monkeypatch.setitem(DIGESTS, "d", frozenset({hashlib.sha256(b"build-host-zz").hexdigest()}))
    assert path_hits("docs/x/sar/build-host-zz.txt") == [("d", ("docs/x/sar/build-host-zz.txt", 0, "bu***(13)"))]
    assert path_hits("docs/x/sar/build-host-zy.txt") == []


def test_the_name_digest_set_is_nine_sha256_hex_digests_and_holds_the_owner():
    for d in DIGESTS["b"]:
        assert re.fullmatch(r"[0-9a-f]{64}", d)
    assert len(DIGESTS["b"]) == 9
    assert OWNER_DIGEST in DIGESTS["b"]


@pytest.mark.parametrize("line", ["tmp/pytest-of-someone-zz/pytest-0", '"account": "claude-someone-zz"',
                                  "test_gets_someone_zz_over_44", "Someone-ZZ said", "x/someone-zz/verifiable-englis"])
def test_a_name_digest_matches_names_in_paths_and_words(monkeypatch, line):
    monkeypatch.setitem(DIGESTS, "b", frozenset({hashlib.sha256(b"someone-zz").hexdigest()}))
    assert any(k == "b" for k, _ in scan_line(line.replace("someone_zz", "someone-zz")))


def test_the_owner_is_allowed_only_inside_the_public_repo_url(monkeypatch):
    monkeypatch.setitem(DIGESTS, "b", frozenset({hashlib.sha256(b"owner-zz").hexdigest()}))
    monkeypatch.setattr(sys.modules[__name__], "OWNER_DIGEST", hashlib.sha256(b"owner-zz").hexdigest())
    assert scan_line("git clone https://github.com/Owner-ZZ/verifiable-english.git") == []
    assert scan_line("see owner-zz/verifiable-english#12") == []
    assert ("b", "owner-zz") in scan_line("asked owner-zz about it")
    assert ("b", "owner-zz") in scan_line("https://github.com/owner-zz/other-repo")


def test_another_owner_in_a_repo_url_is_not_allowed(monkeypatch):
    monkeypatch.setitem(DIGESTS, "b", frozenset({hashlib.sha256(b"someone-zz").hexdigest()}))
    assert ("b", "someone-zz") in scan_line("github.com/someone-zz/verifiable-english")


def test_every_held_file_names_its_reason():
    for path, (counts, reason) in ALLOWED.items():
        assert counts and reason, path
        assert not set(counts) - set("abcdef"), path
