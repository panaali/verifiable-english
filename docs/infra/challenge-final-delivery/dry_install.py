"""Dry install of REPORT.md section 5 (reviews/challenge-final-delivery-dri-note-20261117.md item 3; review F2).

Copies manage-agents/tools-local's decider-ready-alert.py* files and both test files into a temp tools-local (with backlog.py,
backlog-svc.sh and the two state files of manage-agents beside it: links and copies, nothing in manage-agents is written), runs
the cd/cp/mv/rm lines of the first code block of REPORT.md section 5 there, then runs
  1. test_decider_ready_alert.py with no DRA_SCRIPT (its staged() must pick the installed decider-ready-alert.py),
  2. the same with DRA_SCRIPT = the installed path (the decider's check),
  3. test_p1_ready_alert.py with no P1RUA_ALERT (same picker).
Usage: python3 -I docs/infra/challenge-final-delivery/dry_install.py [REPORT.md] [manage-agents dir]. Exit 0 when all pass."""
import glob, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "REPORT.md")
MA = sys.argv[2] if len(sys.argv) > 2 else "/home/seyran/code/manage-agents"


def main():
    block = re.search(r"## 5\..*?```\n(.*?)```", open(REPORT).read(), re.S).group(1)
    root = tempfile.mkdtemp(prefix="cfd-dry-install-")
    tl = os.path.join(root, "tools-local")
    os.makedirs(tl)
    for f in glob.glob(os.path.join(MA, "tools-local", "decider-ready-alert.py*")) + [
            os.path.join(MA, "tools-local", t) for t in ("test_decider_ready_alert.py", "test_p1_ready_alert.py")]:
        shutil.copy2(f, tl)
    for f in ("backlog.py", "backlog-svc.sh"):
        os.symlink(os.path.join(MA, f), os.path.join(root, f))
    for f in ("decider-ready-alert.sent", "p1-unstartable-alert.sent"):
        if os.path.isfile(os.path.join(MA, f)):
            shutil.copy2(os.path.join(MA, f), root)
    J = lambda x: os.path.join(tl, os.path.basename(x))
    for line in block.splitlines():
        w = line.split()
        if not w or w[0] == "cd" or w[0].startswith("#"):
            continue
        if w[0] == "cp":
            shutil.copy2(J(w[-2]), J(w[-1]))
        elif w[0] == "mv":
            os.replace(J(w[-2]), J(w[-1]))
        elif w[0] == "rm":
            for x in w[1:]:
                if not x.startswith("-"):
                    os.remove(J(x))
        else:
            sys.exit(f"dry install: unknown install line {line!r}")
        print("ran:", line)
    live = os.path.join(tl, "decider-ready-alert.py")
    print("tools-local after the install:", sorted(os.listdir(tl)))
    env = {k: v for k, v in os.environ.items() if k not in ("DRA_SCRIPT", "P1RUA_ALERT", "P1RUA_BACKLOG", "BACKLOG_SVC_SH")}
    for k in ("DRA_SCRIPT", "P1RUA_ALERT"):
        os.environ.pop(k, None)
    import runpy
    picked = runpy.run_path(os.path.join(tl, "test_decider_ready_alert.py"), run_name="dry")["SCRIPT"]
    print("staged() picks:", os.path.relpath(picked, root))
    rc = 0 if picked == live else 1
    for name, extra, test in (("picker", {}, "test_decider_ready_alert.py"),
                              ("DRA_SCRIPT=<installed path>", {"DRA_SCRIPT": live}, "test_decider_ready_alert.py"),
                              ("p1 picker", {}, "test_p1_ready_alert.py")):
        p = subprocess.run([sys.executable, "-I", os.path.join(tl, test)], env=dict(env, **extra), capture_output=True,
                           text=True, cwd=root)
        tail = [l for l in (p.stdout + p.stderr).splitlines() if re.match(r"(Ran |OK|FAILED|FAIL:|ERROR:|alert: )", l)]
        print(f"== {name}: {test} rc={p.returncode}", *tail, sep="\n  ")
        rc |= p.returncode
    shutil.rmtree(root)
    print("dry install:", "PASS" if rc == 0 else "FAIL")
    return rc


if __name__ == "__main__":
    sys.exit(main())
