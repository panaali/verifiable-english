"""Pin the three manage-agents files of row vm-stop-recovery-pacing: writes new-files.diff (full text, as additions)
and md5.txt next to this file.
usage: python3 -I docs/infra/vm-stop-recovery-pacing/pin_files.py [--check] [<manage-agents dir>]
  --check: write nothing; exit 1 when the saved new-files.diff or md5.txt no longer match the files."""
import hashlib, os, sys

FILES = ["tools-local/vm-stop-recover.sh", "tools-local/vm-stop-recover-jobs-20261108.txt",
         "tools-local/test_vm_stop_recover.py"]
HERE = os.path.dirname(os.path.abspath(__file__))


def render(m):
    diff, md5 = [], []
    for rel in FILES:
        data = open(os.path.join(m, rel), "rb").read()
        lines = data.decode().splitlines()
        diff += ["--- /dev/null", f"+++ {rel}", f"@@ -0,0 +1,{len(lines)} @@", *("+" + x for x in lines)]
        md5.append(f"{hashlib.md5(data).hexdigest()}  {rel}")
    return "\n".join(diff) + "\n", "\n".join(md5) + "\n"


def main(argv):
    check = "--check" in argv
    rest = [a for a in argv if a != "--check"]
    diff, md5 = render(rest[0] if rest else "/home/seyran/code/manage-agents")
    paths = {"new-files.diff": diff, "md5.txt": md5}
    if check:
        stale = [n for n, t in paths.items() if open(os.path.join(HERE, n)).read() != t]
        print(f"stale: {stale}" if stale else "new-files.diff and md5.txt match the files")
        return 1 if stale else 0
    for n, t in paths.items():
        open(os.path.join(HERE, n), "w").write(t)
    print(md5, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
