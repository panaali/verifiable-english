import json, subprocess, sys, re, os
root = "/home/seyran/code/ve-ps-2a"
ms = json.load(open(sys.argv[1])); target = sys.argv[2] if len(sys.argv) > 2 else "VE.Presupposition.Examples"
only = set(sys.argv[3].split(",")) if len(sys.argv) > 3 else None
env = dict(os.environ, PATH=os.path.expanduser("~/.elan/bin") + ":" + os.environ["PATH"])
out = []
for m in ms:
    if only and m["id"] not in only: continue
    f = os.path.join(root, m.get("file", "lean/VE/Presupposition/Wire.lean"))
    s = open(f).read()
    if s.count(m["find"]) != 1:
        print(m["id"], "FIND-COUNT", s.count(m["find"])); continue
    open(f, "w").write(s.replace(m["find"], m["replace"]))
    try:
        r = subprocess.run(["lake", "build", target], cwd=root + "/lean", capture_output=True, text=True, env=env, timeout=3000)
    finally:
        open(f, "w").write(s)
    errs = sorted(set(re.findall(r"error: (VE/[\w/]+\.lean:\d+)", r.stdout + r.stderr)))
    errs = [e.split("/")[-1] for e in errs]
    print(m["id"], "KILLED" if r.returncode else "SURVIVED", errs[:6], flush=True)
    m["test"] = errs; out.append(m)
json.dump(out, open(sys.argv[1] + ".out", "w"), indent=1, ensure_ascii=False)
