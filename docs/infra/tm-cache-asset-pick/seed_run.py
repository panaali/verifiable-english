#!/usr/bin/env python3
"""Seeded bugs of tm-cache-asset-pick: each is planted in a TEMPORARY copy of the staged lean-cache-publish.sh.new-tmcache
(the staged file is never edited), tools-local/test_tm_cache_asset_pick.py runs on the copy (LCP=<copy>), and the seed must
make at least one test FAIL. Writes seeds.log and seeded-bugs.json next to this file.
usage: python3 -I docs/infra/tm-cache-asset-pick/seed_run.py"""
import json, os, subprocess, sys, tempfile

M = "/home/seyran/code/manage-agents"
STAGED = f"{M}/lean-cache-publish.sh.new-tmcache"
TEST = f"{M}/tools-local/test_tm_cache_asset_pick.py"
HERE = os.path.dirname(os.path.abspath(__file__))
SEEDS = [
    ("B1-release-prune-ignores-pin", "(1) the release prune never deletes the nightly's asset",
     'if x["name"] != sys.argv[4]: print', 'print'),
    ("B2-manifest-slice-drops-pin", "(1) manifest.json keeps the nightly's row (and url) past its 6-row cut",
     'm["assets"][:6] + [x for x in m["assets"][6:] if pin and x["name"] == pin]', 'm["assets"][:6]'),
    ("B3-no-resume-check", "(2) only a head tm-nightly.py resume would resume is pinned (complete/old/no-resume: as today)",
     'out=$(TEST_SKIP_DIR=$TSD python3 -I $M/tm-nightly.py resume $R $rb 2>/dev/null) || return 0',
     'out=$(TEST_SKIP_DIR=$TSD python3 -I $M/tm-nightly.py resume $R $rb 2>/dev/null) || out="$TSD/nightly/$rec\t'
     '$(python3 -I -c "import json,sys; print(json.load(open(sys.argv[1]))[\\"head\\"])" $TSD/nightly/$rec)\t3"'),
    ("B4-quarantine-ignored", "(2) a quarantined asset is never the pin (the dispatcher's own quarantine)",
     '$MF ${VE_CACHE_QUARANTINE:-$M/ve-cache-quarantine.tsv} --k', '$MF /dev/null --k'),
    ("B5-platform-suffix-ignored", "(3) the pin is of this platform's manifest and name (aarch64 --pack)",
     '"^lean-build-[0-9a-f]{12}$sfx\\\\.tar\\\\.zst\\$"', '"^lean-build-[0-9a-f]{12}\\\\.tar\\\\.zst\\$"'),
    ("B6-exact-tree-only", "(1) the pin is lean-near's within K from the record's base (the dispatcher's), not the exact tree only",
     '--k ${ACTIONS_FIRST_NEAR_K:-4} --base $rb 2>/dev/null)', '--k 0 2>/dev/null)'),
]


def main():
    src = open(STAGED).read()
    d = tempfile.mkdtemp(prefix="tmcache-seeds-")
    rows, lines, bad = [], [], 0
    for sid, beh, a, b in SEEDS:
        if src.count(a) != 1:
            lines.append(f"{sid}: NOT PLANTED (anchor not found once)"); bad += 1; continue
        p = f"{d}/{sid}.sh"; open(p, "w").write(src.replace(a, b))
        r = subprocess.run([sys.executable, "-I", TEST], env=dict(os.environ, LCP=p), capture_output=True, text=True)
        failing = [l.strip()[5:].split("  [")[0].strip() for l in r.stdout.splitlines() if l.startswith("  FAIL ")]
        caught = r.returncode != 0 and bool(failing)
        bad += 0 if caught else 1
        lines.append(f"{sid}: {'CAUGHT' if caught else 'NOT CAUGHT'} (exit {r.returncode}, {len(failing)} failing)"
                     + "".join(f"\n    FAIL {f}" for f in failing))
        rows.append({"id": sid, "behaviour": beh, "language": "shell (zsh) with embedded Python", "file": STAGED,
                     "test": f"{TEST}::{failing[0]}" if failing else TEST, "failing_tests": failing, "caught": caught})
    open(f"{HERE}/seeds.log", "w").write("\n".join(lines) + f"\n{len(SEEDS) - bad} of {len(SEEDS)} caught\n")
    json.dump({"item": "tm-cache-asset-pick", "planted_in": "temporary copies of the staged file; the staged file is never edited",
               "command": "python3 -I docs/infra/tm-cache-asset-pick/seed_run.py", "mutants": rows},
              open(f"{HERE}/seeded-bugs.json", "w"), indent=1)
    print("\n".join(lines)); return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
