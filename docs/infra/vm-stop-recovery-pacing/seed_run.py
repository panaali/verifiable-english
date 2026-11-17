"""Seeded bugs for tools-local/vm-stop-recover.sh (row vm-stop-recovery-pacing).
usage: python3 -I docs/infra/vm-stop-recovery-pacing/seed_run.py   (writes seeded-bugs.json next to this file)
Each seed is one text replacement in a COPY of the script (the live file is never edited); the test file
tools-local/test_vm_stop_recover.py runs against the copy (VMSR_SCRIPT) and must fail. Seed 0 is the unmutated baseline."""
import json, os, re, subprocess, tempfile

M = "/home/seyran/code/manage-agents"
SCRIPT = f"{M}/tools-local/vm-stop-recover.sh"
TESTS = f"{M}/tools-local/test_vm_stop_recover.py"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "seeded-bugs.json")

SEEDS = [
    ("baseline (no change)", "", ""),
    ("order: file order instead of trains first",
     "ORDER=(); for i in {1..$#CLS}; do [[ $CLS[i] = train ]] && ORDER+=$i; done; for i in {1..$#CLS}; do [[ $CLS[i] = job ]] && ORDER+=$i; done",
     "ORDER=({1..$#CLS})"),
    ("load hold: 48 itself passes (> instead of >=)",
     "[[ -n $L1 ]] && (( L1 >= LOAD_MAX ))", "[[ -n $L1 ]] && (( L1 > LOAD_MAX ))"),
    ("young cap: a 7th relaunch in 15 min passes",
     "(( young >= YOUNG_MAX )) && why+=", "(( young > YOUNG_MAX )) && why+="),
    ("young window counts 10 min, not 15",
     "LOAD_MAX=48 YOUNG_MAX=6 YOUNG_SEC=900", "LOAD_MAX=48 YOUNG_MAX=6 YOUNG_SEC=600"),
    ("restore: no 10-min wait after the last relaunch",
     "while stopped; (( NOW < last + RESTORE_SEC )); do", "while stopped; (( 0 )); do"),
    ("pause: the dry run moves the flag",
     'if (( dry )); then say "pause: would move $f -> ${p:t}"',
     'if (( dry )); then mv -n -- $M/$f $p; say "pause: would move $f -> ${p:t}"'),
    ("pause: flags not moved in a real run",
     "else mv -n -- $M/$f $p && [[ -e $p && ! -e $M/$f ]]", "else [[ 1 = 1 ]]"),
    ("dry run launches",
     'if (( dry )); then say "launch (dry run: not started)', 'if (( 0 )); then say "launch (dry run: not started)'),
    ("restore: a re-created flag is overwritten",
     "elif [[ -e $M/$f ]]; then say \"restore: $f exists again", "elif false; then say \"restore: $f exists again"),
    ("skip: a running job is relaunched",
     "if out=$(busy $KEYS[$1]); then", "if false; then"),
    ("skip: an unreadable scope list is read as no scope",
     '(( r )) && { print -r -- "scope list unreadable', '(( 0 )) && { print -r -- "scope list unreadable'),
    ("record: no CURRENT-STATE.md line in a real run",
     '$NOW) (vm-stop-recover $D): $*" >> $M/CURRENT-STATE.md', '$NOW) (vm-stop-recover $D): $*" >> /dev/null'),
    ("jobs file: $(...) accepted",
     "if [[ $line == *'$'* || $line == *'`'* ]]; then", "if false; then"),
    ("lock: the launched job inherits the lock fd",
     " {lockfd}>&- &!", " &!"),
    ("interrupt: flags restored instead of left paused",
     '  exit 130; }', '  restore_flags; exit 130; }'),
]


def main():
    src = open(SCRIPT).read()
    rows = []
    for name, old, new in SEEDS:
        if old:
            assert src.count(old) == 1, (name, src.count(old))
        d = tempfile.mkdtemp(prefix="vmsr-seed-")
        path = os.path.join(d, "vm-stop-recover.sh")
        open(path, "w").write(src.replace(old, new) if old else src)
        r = subprocess.run(["python3", "-I", TESTS], env={**os.environ, "VMSR_SCRIPT": path},
                           capture_output=True, text=True, timeout=1800)
        failed = sorted(set(re.findall(r"^(?:FAIL|ERROR): (\w+)", r.stderr, re.M)))
        ran = re.search(r"^Ran (\d+) tests", r.stderr, re.M)
        rows.append({"seed": name, "file": SCRIPT, "old": old, "new": new, "rc": r.returncode,
                     "ran": int(ran[1]) if ran else None, "failing_tests": failed,
                     "caught": bool(old) and r.returncode != 0 and bool(failed)})
        print(f"{'baseline' if not old else ('CAUGHT' if rows[-1]['caught'] else 'MISSED')}: {name}: rc {r.returncode}, "
              f"failing {failed}")
    json.dump({"script": SCRIPT, "tests": TESTS, "seeds": rows}, open(OUT, "w"), indent=1)
    base = rows[0]
    assert base["rc"] == 0 and not base["failing_tests"], base
    missed = [r["seed"] for r in rows[1:] if not r["caught"]]
    print(f"{len(rows) - 1 - len(missed)}/{len(rows) - 1} caught; missed: {missed}")
    return 1 if missed else 0


if __name__ == "__main__":
    raise SystemExit(main())
