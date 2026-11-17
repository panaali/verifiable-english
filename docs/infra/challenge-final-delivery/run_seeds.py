"""Seeded bugs for challenge-final-delivery fix round 1. Each seed: one find/replace in a temp copy of the scratch script (or of
the test file for the picker seeds), then the suite; the scratch files are never edited (sha256 checked before and after).
Usage: python3 -I run_seeds.py <out.json> [<dir holding tools-local/, backlog-svc.sh and the two state files>]."""
import hashlib, json, os, re, shutil, subprocess, sys

W = sys.argv[2] if len(sys.argv) > 2 else "/tmp/cfd-work"   # run of record: scratch copies whose sha256 = the staged files
SCRIPT = f"{W}/tools-local/decider-ready-alert.py.new-challew"
TEST = f"{W}/tools-local/test_decider_ready_alert.py"
SEEDS = [
    ("S1", "script", "the 30-min wait is 29 min", "now - st.st_mtime < CF_AFTER", "now - st.st_mtime < CF_AFTER - 60"),
    ("S2", "script", "no once-only dedup for challenge finals",
     "cf = [x for x in challenge_finals(rows, now) if x[1] not in sent]", "cf = list(challenge_finals(rows, now))"),
    ("S3", "script", "Astra challenges go to the decider, not the orchestrator",
     'return "orchestrator" if ASTRA.search', 'return "dri" if ASTRA.search'),
    ("S4", "script", "a final older than the in-flight stamp still counts",
     "if t is None or st.st_mtime <= t:", "if t is None:"),
    ("S5", "script", "closed rows (done/merged/dropped) count (replaces the first round's S5, which recorded the required "
     "behaviour of review F1 as a bug)", 'if r.get("status") in closed:', 'if False:'),
    ("S6", "script", "a failed send to one addressee still records its finals", "cf = [x for x in cf if x[4] in ok]", "cf = cf"),
    ("S7", "script", "any suffix after a row id claims the final",
     'CF_SUFFIX = re.compile(r"(stopped-)?\\d{4,8}(T\\d{4,6}Z?)?")', 'CF_SUFFIX = re.compile(r".*")'),
    ("S8", "script", "the dri- prefix is not stripped", '[stem] + ([stem[4:]] if stem.startswith("dri-") else [])', "[stem]"),
    ("S9", "script", "F1: the run start (backlog.py row_run_t) is not a stamp: only status_t",
     "ts.append(bl.row_run_t(dict(r, links=L)))", "pass"),
    ("S10", "script", "F1: the earliest stamp wins, not the latest", "return max(ts) if ts else None",
     "return min(ts) if ts else None"),
    ("S11", "script", "F1: status_t counts whatever status backlog.sh wrote",
     '(r.get("status_cli") or r.get("status")) == "in-flight"', "True"),
    ("S12", "script", "F1: a dri-<x> delegate row is not its own delegate", 'L["delegate"] = r["id"]', "pass"),
    ("S13", "script", "F1: only status in-flight rows count (the first build's rule)",
     'if r.get("status") in closed:', 'if r.get("status") != "in-flight":'),
    ("S14", "script", "DRI note 1: a state line that is not UTF-8 stops the pass",
     "except UnicodeDecodeError:\n            w = None", "except KeyError:\n            w = None"),
    ("S15", "script", "DRI note 1: lines skipped from the state file are not named",
     'print(f"decider-ready-alert: state {os.path.basename(path)}: line(s)', 'None and print(f"'),
    ("S16", "script", "the CLOSED fallback drifts from backlog.py CLOSED",
     'CF_CLOSED_FALLBACK = ("merged", "done", "dropped")', 'CF_CLOSED_FALLBACK = ("merged", "done")'),
    ("S17", "script", "F4: astra matched in the row id only", "ASTRA.search(f\"{r.get('id', '')} {name}\")",
     "ASTRA.search(f\"{r.get('id', '')}\")"),
    ("S18", "script", "F4: astra matched in the file name only", "ASTRA.search(f\"{r.get('id', '')} {name}\")",
     "ASTRA.search(f\"{name}\")"),
    ("S19", "script", "F4: a row two links claim is named twice", " and r not in out:", ":"),
    ("S20", "test", "F2: the picker ignores mtimes (a stale staged copy is tested after the install)",
     "new = [x for x in new if x[0] > t0]", "new = new"),
    ("S21", "test", "F2: the picker prefers any staged copy by a fixed tag list (the first build's rule)",
     "    return max(new)[1] if new else live",
     "    return next((live + t for t in ('.new-nta', '.new-challew') if os.path.exists(live + t)), live)"),
]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    before = {p: sha(p) for p in (SCRIPT, TEST)}
    d = "/tmp/cfd-seeds/m"
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(f"{d}/tools-local")
    os.symlink("/home/seyran/code/manage-agents/backlog.py", f"{d}/backlog.py")
    for f in ("decider-ready-alert.sent", "p1-unstartable-alert.sent", "backlog-svc.sh"):
        os.symlink(f"{W}/{f}", f"{d}/{f}")
    out = []
    for sid, where, bug, find, repl in SEEDS:
        s, t = open(SCRIPT).read(), open(TEST).read()
        src = s if where == "script" else t
        n = src.count(find)
        if n != 1:
            out.append({"id": sid, "bug": bug, "error": f"find matched {n} times"})
            continue
        src = src.replace(find, repl)
        if where == "script":
            s = src
        else:
            t = src
        ms, mt = f"{d}/tools-local/decider-ready-alert.py.new-seed", f"{d}/tools-local/test_decider_ready_alert.py"
        open(ms, "w").write(s)
        open(mt, "w").write(t)
        p = subprocess.run([sys.executable, "-I", mt], env=dict(os.environ, DRA_SCRIPT=ms), capture_output=True, text=True,
                           cwd=d)
        failing = sorted(set(re.findall(r"^(?:FAIL|ERROR): (\w+)", p.stderr, re.M)))
        out.append({"id": sid, "where": "manage-agents/tools-local/" + ("decider-ready-alert.py.new-challew" if where == "script"
                                                                         else "test_decider_ready_alert.py"),
                    "bug": bug, "find": find, "replace": repl, "rc": p.returncode, "failing_tests": failing,
                    "caught": p.returncode != 0 and bool(failing)})
        print(sid, p.returncode, failing)
    after = {p: sha(p) for p in (SCRIPT, TEST)}
    assert before == after, "a scratch file changed"
    json.dump({"item": "challenge-final-delivery", "round": "fix round 1",
               "note": "Python only, in manage-agents/tools-local (no Lean, Rust or Python of this VE repo changed). Each seed is"
                       " a temp copy of the staged script (or, S20-S21, of the test file) with one find/replace, run as"
                       " DRA_SCRIPT=<copy> python3 -I <test copy>; the staged files were never edited (sha256 before = after:"
                       f" {sorted(after.values())}).",
               "mutants": out}, open(sys.argv[1], "w"), indent=1)


if __name__ == "__main__":
    main()
