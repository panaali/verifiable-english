"""digest-main-line seeded bugs: each mutant is a /tmp copy of the staged waiter; the staged file is never edited.
Run: python3 -I docs/infra/digest-main-line/seeded-run.py  (prints one line per mutant and writes seeded-bugs.json beside it)"""
import json, os, subprocess, tempfile
M = "/home/seyran/code/manage-agents"
IW = f"{M}/inbox-wait.sh.new-dml"
T = f"{M}/tools-local/test_digest_main_line.py"
seeds = [  # (id, old, new, test)
 ("S1-gap-sign-flipped", "gap {w[0] - pl:+.1f} pt", "gap {pl - w[0]:+.1f} pt", "DigestMainLine.test_2_gap_sign_above_and_below_the_line"),
 ("S2-header-below-digest", '[ -n "$d" ] && { dml; print -r -- "$d"; }', '[ -n "$d" ] && { print -r -- "$d"; dml; }', "DigestMainLine.test_4_body_byte_identical_below_header_keepalive"),
 ("S3-header-without-digest", '[ -n "$d" ] && { dml; print -r -- "$d"; }', 'dml; [ -n "$d" ] && print -r -- "$d"', "DigestMainLine.test_4b_no_digest_no_header"),
 ("S4-missing-log-reads-zero", 'except OSError as e: why.append(f"usage-watch.log unreadable: {type(e).__name__}")', 'except OSError as e: w = (0, "?")', "DigestMainLine.test_3_missing_log_question_line_and_digest_unchanged"),
 ("S5-first-main-line-not-last", "for r in reversed(rows):", "for r in rows:", "DigestMainLine.test_1_header_has_week_line_gap_and_sources"),
 ("S6-line-real-clock-not-picker-clock", '"now": endgame.now()', '"now": datetime.datetime.now(datetime.timezone.utc)', "DigestMainLine.test_2b_line_follows_the_picker_clock"),
 ("S7-expired-header-drops-line", '|| h="main week ? (header failed: no reading within 30 s)"', '|| h=""', "DigestMainLine.test_3e_header_deadline_expired_still_sends_digest"),
]
src = open(IW).read(); out = []
for sid, old, new, test in seeds:
    assert src.count(old) == 1, sid
    d = tempfile.mkdtemp(prefix=f"dml-{sid}-"); p = f"{d}/inbox-wait.sh"
    open(p, "w").write(src.replace(old, new))
    r = subprocess.run(["python3", "-I", T, test], env=dict(os.environ, IW_SCRIPT=p), capture_output=True, text=True, timeout=300)
    res = "CAUGHT" if r.returncode != 0 else "SURVIVED"
    print(sid, test, res, r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "")
    out.append({"id": sid, "language": "zsh + Python (embedded in zsh)", "file": IW, "old": old, "new": new,
                "test": f"tools-local/test_digest_main_line.py::{test}", "result": res})
json.dump({"item": "digest-main-line", "command": "python3 -I docs/infra/digest-main-line/seeded-run.py (mutants in /tmp copies; staged file untouched)",
           "mutants": out}, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "seeded-bugs.json"), "w"), indent=1)
