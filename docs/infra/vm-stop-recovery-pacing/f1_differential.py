"""Review F1 (fix round): the reviewed script vs the fixed one, dry runs on the 1108 list, one row per load trigger.
usage: python3 -I docs/infra/vm-stop-recovery-pacing/f1_differential.py <reviewed-script-copy>
  (the reviewed copy: git -C /home/seyran/code/manage-agents show 74b44c00:tools-local/vm-stop-recover.sh, md5 12b06170...)
Writes f1-old-vs-new.txt and dry-run-1108-high-load.log next to this file. Every run uses an empty temp dir as VMSR_M,
so no live flag is read or moved. Where the load is low or changes (no dry-run release) the outputs must be identical;
where a load >= 48 no longer changes (or is unreadable), the old script breaks the 6-in-15-min limit (7/6 ... 15/6) and
the new one gives the low-load schedule."""
import hashlib, os, re, subprocess, sys, tempfile

M = "/home/seyran/code/manage-agents"
NEW = f"{M}/tools-local/vm-stop-recover.sh"
JOBS = f"{M}/tools-local/vm-stop-recover-jobs-20261108.txt"
HERE = os.path.dirname(os.path.abspath(__file__))
LOW = "12.50 10.00 9.00 1/1 1\n"
CASES = [  # name, loadavg file text (None: no file), --dry-loads list, release path hit?
    ("low live load 12.50", LOW, None, False),
    ("rising --dry-loads profile ending low", LOW, "3 9 17 26 35 44 51 58 63 66 61 55 50 47 52 49 46 38 34 30", False),
    ("live load 60 (PROBE F1)", "60.00 50.00 40.00 1/1 1\n", None, True),
    ("live load exactly 48", "48 50.00 40.00 1/1 1\n", None, True),
    ("--dry-loads ending high", LOW, "10 60", True),
    ("unreadable load file", None, None, True),
]


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def run(script, d, load_text, dry_loads):
    lf = os.path.join(d, "loadavg")
    if os.path.exists(lf):
        os.remove(lf)
    if load_text is not None:
        open(lf, "w").write(load_text)
    argv = ["zsh", script, "--dry-run", "--date", "20261108", *(["--dry-loads", dry_loads] if dry_loads else []), JOBS]
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": os.environ.get("HOME", d), "VMSR_M": d,
           "VMSR_LOADAVG": lf, "VMSR_SYSTEMCTL": "true"}
    r = subprocess.run(argv, env=env, capture_output=True, text=True, timeout=600)
    return r.returncode, (r.stdout + r.stderr).replace(d, M)


def launches(out):
    return re.findall(r"^\+(\d+m\d\ds) launch", out, re.M)


def max_young(out):
    return max((int(x) for x in re.findall(r"(\d+)/6 in their first 15 min", out)), default=0)


def main():
    old = sys.argv[1]
    d = tempfile.mkdtemp(prefix="vmsr-f1-")
    rows = [f"# review F1: reviewed script (md5 {md5(old)}) vs fixed script (md5 {md5(NEW)});",
            f"# --dry-run --date 20261108 on {JOBS}; VMSR_M = an empty temp dir; VMSR_SYSTEMCTL=true", ""]
    bad = []
    for name, text, dl, release in CASES:
        ro, oo = run(old, d, text, dl)
        rn, on = run(NEW, d, text, dl)
        same = oo == on
        rows += [f"## {name}: rc old {ro} new {rn}; output {'IDENTICAL' if same else 'differs'}; "
                 f"max young old {max_young(oo)}/6, new {max_young(on)}/6",
                 f"   old launches: {' '.join(launches(oo))}", f"   new launches: {' '.join(launches(on))}"]
        if name.startswith("live load 60"):
            open(os.path.join(HERE, "dry-run-1108-high-load.log"), "w").write(on)
        if rn != 0 or max_young(on) > 6 or (not release and not same) or (release and max_young(oo) <= 6):
            bad.append(name)
    left = sorted(set(os.listdir(d)) - {"loadavg"})
    rows += ["", f"files the dry runs left in VMSR_M besides the harness's loadavg: {left or 'none'}",
             f"result: {'OK' if not bad and not left else f'FAILED {bad} {left}'}"]
    open(os.path.join(HERE, "f1-old-vs-new.txt"), "w").write("\n".join(rows) + "\n")
    print("\n".join(rows))
    return 1 if bad or left else 0


if __name__ == "__main__":
    raise SystemExit(main())
