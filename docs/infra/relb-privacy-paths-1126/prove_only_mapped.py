#!/usr/bin/env python3
"""Prove the mechanical commit changed only mapped tokens (value-free; values come from the host like the map).

python3 -I prove_only_mapped.py --repo <checkout> <base> [<head>]   (head default: the working tree)
Reads `git diff --word-diff=porcelain` (words = runs of non-space) over the whole change: every removed word must
hold a private value and become exactly its mapped form (the map applied to the removed word, rule by rule, with the
public repo URL kept); every added word must pair with a removed one. Renames must map the old path to the new.
Prints counts per rule and the failures, masked (first 2 characters + *** + length).
"""
import importlib.util, os, subprocess, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("ap", os.path.join(HERE, "apply_privacy_map.py"))
ap = importlib.util.module_from_spec(spec); spec.loader.exec_module(ap)


def mask(v):
    return f"{v[:2]}***({len(v)})"


def main(argv):
    repo, refs = None, []
    it = iter(argv)
    for a in it:
        if a == "--repo": repo = next(it)
        else: refs.append(a)
    rules, public = ap.build_rules(ap.private_values())
    rng = refs[:2]
    diff = subprocess.run(["git", "-C", repo, "diff", "-M100%", "--word-diff=porcelain", "--word-diff-regex=[^[:space:]]+",
                           "-U0", *rng], capture_output=True, check=True).stdout.decode("utf-8", "surrogateescape")
    counts, bad, words, files = Counter(), [], 0, set()
    minus, plus, cur = [], [], None

    def flush():
        nonlocal minus, plus
        if not minus and not plus:
            return
        if len(minus) != len(plus):
            bad.append(f"{cur}: {len(minus)} removed / {len(plus)} added words (masked: {[mask(m) for m in minus[:3]]})")
        for m, p in zip(minus, plus):
            c = Counter()
            if ap.transform(m, rules, public, c) != p or not c:
                bad.append(f"{cur}: {mask(m)} -> {mask(p)} is not its mapped form")
            counts.update(c)
        minus, plus = [], []
    for line in diff.splitlines():
        if line.startswith("diff --git"):
            flush(); cur = line.split(" b/", 1)[-1]; files.add(cur); continue
        if line.startswith(("---", "+++", "@@", "index ", "similarity", "rename ", "new file", "deleted file")):
            if line.startswith("@@"):
                flush()
            continue
        if line.startswith("-"):
            minus.append(line[1:]); words += 1
        elif line.startswith("+"):
            plus.append(line[1:])
        else:
            flush()
    flush()
    ren = subprocess.run(["git", "-C", repo, "diff", "-M100%", "--name-status", "--diff-filter=R", *rng],
                         capture_output=True, text=True, check=True).stdout.splitlines()
    for r in ren:
        _s, old, new = r.split("\t")
        c = Counter()
        if ap.transform(old, rules, public, c) != new:
            bad.append(f"rename {mask(old)} -> {mask(new)} is not mapped")
        counts.update({f"path {k}": v for k, v in c.items()})
    # file level: every changed file's new bytes equal the map applied to its old bytes. A word-level failure in a
    # file that passes here is git's word alignment pairing words across lines, not an unmapped change.
    base = rng[0]
    renmap = {r.split("\t")[2]: r.split("\t")[1] for r in ren}
    file_bad, aligned = [], 0
    for f in sorted(files):
        old_path = renmap.get(f, f)
        o = subprocess.run(["git", "-C", repo, "show", f"{base}:{old_path}"], capture_output=True)
        if "--cached" in rng:
            n = subprocess.run(["git", "-C", repo, "show", f":{f}"], capture_output=True)
        elif len(rng) > 1:
            n = subprocess.run(["git", "-C", repo, "show", f"{rng[1]}:{f}"], capture_output=True)
        else:
            n = subprocess.CompletedProcess([], 0, open(os.path.join(repo, f), "rb").read(), b"")
        if o.returncode or n.returncode:
            file_bad.append(f"{f}: added or deleted, not a mapped change"); continue
        ot = o.stdout.decode("utf-8", "surrogateescape")
        if ap.transform(ot, rules, public, Counter()).encode("utf-8", "surrogateescape") != n.stdout:
            file_bad.append(f"{f}: new bytes are not the map of the old bytes")
    word_files = {b.split(":", 1)[0] for b in bad if not b.startswith("rename ")}
    file_bad_names = {b.split(":", 1)[0] for b in file_bad}
    aligned = len(word_files - file_bad_names)
    bad = [b for b in bad if b.startswith("rename ") or b.split(":", 1)[0] in file_bad_names] + file_bad
    print(f"files {len(files)}; removed words {words}; renames {len(ren)}; file-level map check: {len(files) - len(file_bad)} "
          f"of {len(files)} equal; word-alignment artifacts in files that pass: {aligned}; failures {len(bad)}")
    for k in sorted(counts):
        print(f"  {k}\t{counts[k]}")
    for b in bad[:40]:
        print("FAIL", b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
