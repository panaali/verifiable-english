"""Evidence: which historical sync merges on main conflicted only in files tools/regen_generated.py owns.

    uv run python docs/merge-tooling/survey.py docs/merge-tooling/sync-merge-survey.json

Every merge commit of `main` whose subject is "Merge ve-integration into ..." (or main into a branch) is
re-merged in memory (`git merge-tree --write-tree --name-only`, which changes no ref or file), and its
conflicted paths are split by `regen_generated.owner`. Recorded once (2026-10-10); the tests read the saved
file, never a live run."""
import json, subprocess, sys
sys.path.insert(0, "tools")
import regen_generated as R
log = subprocess.run(["git", "log", "--merges", "--format=%H %P %s", "main"], capture_output=True, text=True).stdout
rows = []
for line in log.splitlines():
    sha, p1, p2, *subject = line.split(" ")
    subject = " ".join(subject)
    if not any(subject.startswith(f"Merge {s} into") for s in ("ve-integration", "branch 've-integration'", "main")):
        continue
    done = subprocess.run(["git", "merge-tree", "--write-tree", "--name-only", "--no-messages", p1, p2],
                          capture_output=True, text=True)
    files = done.stdout.split("\n")[1:] if done.returncode == 1 else []
    files = sorted({f for f in files if f})
    generated = [f for f in files if R.owner(f)]
    rows.append({"merge": sha[:10], "subject": subject, "conflicts": files,
                 "generated": generated, "other": [f for f in files if not R.owner(f)]})
summary = {"sync_merges": len(rows), "clean": sum(not r["conflicts"] for r in rows),
           "only_generated": sum(bool(r["conflicts"]) and not r["other"] for r in rows),
           "with_other": sum(bool(r["other"]) for r in rows)}
json.dump({"summary": summary, "merges": rows}, open(sys.argv[1], "w"), indent=1)
print(summary)
for r in rows:
    if r["conflicts"] and not r["other"]:
        print(r["merge"], r["subject"], r["generated"])
