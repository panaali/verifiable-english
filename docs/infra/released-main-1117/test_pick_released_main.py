"""released-main-1117 (reviews/dri-decisions-20261117-released-main.md item 2; orchestrator BATCH 20261117T032312Z item 2):
a released row (BACKLOG links.released) whose links.avoid names main may take main, ONE row at a time, while main week <= the
PICK_MAIN_PACE line - 4 and the main week rise over 300 min of usage-watch.log < 5, path rows first (a live Nov 23 path waiting
marker: ryield refuses the row everywhere), in rank order (pick_critical.py (vi): rank, then FEATURE-QUEUE.tsv rank). The one
holder marker pick-main-released lists every live pid of the row: a second session of the row joins, the marker is stale only when
no listed pid lives, a give-back takes back only its own grants. Every other gate (main worker cap and taper, week caps, pace
line, other avoid entries, other "main" in PICK_AVOID) stays.
usage: python3 -I tools-local/test_pick_released_main.py
  PICK_SCRIPT = picker under test (default: installed), PCF_SCRIPT = pick_critical.py under test (default: installed).
Fails on the picker installed before released-main-1117 (main stays held out for every released row there)."""
import json, os, shutil, subprocess, sys, tempfile, time, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import test_endgame as te  # fake clock, accounts.sh field helper

PICK = os.environ.get("PICK_SCRIPT", te.PICK)
PCF = os.environ.get("PCF_SCRIPT", os.path.join(HERE, "pick_critical.py"))
LIVE = "/home/seyran/code/manage-agents/"
REL = "reviews/dri-ruling-targets-20261116.md"
PINS = ("# pins\n"
        "path-x\t2099-01-01T00:00Z\ttargets ruling 4.1 (1): Nov 23 path row\n")
ROWS = [{"id": "rel-a", "status": "in-flight", "links": {"avoid": "main", "released": REL}},
        {"id": "rel-b", "status": "in-flight", "links": {"avoid": "main", "released": REL}},
        {"id": "rel-c", "status": "ready", "links": {"avoid": "main", "released": REL}},
        {"id": "rel-d", "status": "ready", "links": {"avoid": "main saeedi.danial", "released": REL}},
        {"id": "plain-avoid", "status": "in-flight", "links": {"avoid": "main"}},
        {"id": "path-x", "status": "in-flight"}]
QUEUE = ("# rank\tid\tbranch\ttask\n"
         "9\trel-a\tfeature/rel-a\t-\n"
         "5\trel-b\tfeature/rel-b\t-\n")
PACE = "2026-10-01T00:00Z 60 2026-12-31T00:00Z 60\n"  # a flat PICK_MAIN_PACE line at 60: the bound is week <= 56


def log(rise):  # SYNTHETIC usage-watch.log main lines over 4 h 40 min, week 45 -> 45 + rise (the 5x lines are ignored)
    out, w = [], 45
    for i, t in enumerate(("15:00Z", "16:00Z", "17:00Z", "18:00Z", "19:00Z", "19:40Z")):
        out.append(f"{t} main 5h=-1 week={w + (rise if i == 5 else min(rise, i))} allowed")
        out.append(f"{t} saeedi.danial 5h=10 week=60 allowed")
    return "\n".join(out) + "\n"


def dead_pid():
    p = subprocess.Popen(["true"])
    p.wait()
    return p.pid


def main_line(week, f=10):  # a known main 5-h (10 < 40: worker cap 3, no stand-in guard)
    return f"main /x/claude-main {f} {week} allowed {te.field(3)} {te.field(50)}"


FIVEX = f"saeedi.danial /x/claude-saeedi.danial 10 60 allowed {te.field(4)} {te.field(50)}"


class Base(unittest.TestCase):
    def setUp(self):
        self.h = tempfile.mkdtemp(prefix="prm-")
        self.m = f"{self.h}/code/manage-agents"
        os.makedirs(f"{self.m}/tools-local")
        shutil.copy(te.EG, f"{self.m}/tools-local/endgame.py")
        shutil.copy(PCF, f"{self.m}/tools-local/pick_critical.py")
        open(f"{self.h}/load", "w").write("1.0 1.0 1.0 1/1 1\n")
        open(f"{self.m}/msg.sh", "w").write('print -r -- "$1|$2|$3" >> ${0:h}/msgs.log\n')
        open(f"{self.m}/PORTFOLIO-PINS.tsv", "w").write(PINS)
        open(f"{self.m}/FEATURE-QUEUE.tsv", "w").write(QUEUE)
        open(f"{self.m}/BACKLOG.jsonl", "w").write("".join(json.dumps(r) + "\n" for r in ROWS))
        open(f"{self.h}/flag-PICK_MAIN_PACE", "w").write(PACE)
        src = open(PICK).read()
        for name in ("PICK_BOOST", "PICK_MAIN_PACE", "CCLOUD_MAIN_88", "PICK_LONG_ROOM", "PICK_PREFER", "PICK_EXCLUDE", "ROLE_BUDGET", "URGENT-ITEMS"):
            src = src.replace(LIVE + name, f"{self.h}/flag-{name}")
        self.p = f"{self.h}/pick.sh"
        open(self.p, "w").write(src)
        self.marker = f"{self.m}/pick-main-released"

    def tearDown(self):
        shutil.rmtree(self.h, ignore_errors=True)

    def env(self, lines, rise=0, busy="", **extra):
        acc = f"{self.h}/accounts.sh"
        open(acc, "w").write("cat <<'E'\n" + "\n".join(lines) + "\nE\n")
        ul = f"{self.h}/usage-watch.log"
        if rise is None:
            ul = f"{self.h}/none"
        else:
            open(ul, "w").write("header line dropped by the reader\n" + log(rise))
            os.utime(ul, (te.NOW.timestamp() - 60, te.NOW.timestamp() - 60))
        e = {k: v for k, v in os.environ.items() if not k.startswith(("PICK_", "PCF_", "CODEX_"))}
        e.update(HOME=self.h, PCF_M=self.m, PICK_ACCOUNTS_SH=acc, PICK_LOADAVG=f"{self.h}/load", PICK_BUSY=busy,
                 PICK_NOWAIT="1", PICK_SHORT="1", ENDGAME_NOW=str(te.NOW.timestamp()), PICK_USAGE_LOG=ul)
        e.update(extra)
        return e

    def pick(self, lines, rise=0, busy="", **extra):  # (account or None, stderr)
        r = subprocess.run(["zsh", self.p], env=self.env(lines, rise, busy, **extra), capture_output=True, text=True, timeout=120)
        return (r.stdout.strip() if r.returncode == 0 else None), r.stderr

    def holder(self):
        return open(self.marker).read().split() if os.path.exists(self.marker) else None

    def put(self, d, row, content, age=0):
        os.makedirs(f"{self.m}/{d}", exist_ok=True)
        p = f"{self.m}/{d}/{row}"
        open(p, "w").write(content)
        t = time.time() - age
        os.utime(p, (t, t))

    # a caller (its own zsh process) that picks and stays alive until release(); returns (Popen, its pick)
    def hold(self, name, lines, **extra):
        g, f = f"{self.h}/{name}.g", f"{self.h}/{name}.f"
        os.mkfifo(g)
        os.mkfifo(f)
        open(f"{self.h}/{name}.sh", "w").write(f'a=$(zsh {self.p} 2>/dev/null); print -r -- "$a" > {g}; read x < {f}\n')
        pr = subprocess.Popen(["zsh", f"{self.h}/{name}.sh"], env=self.env(lines, **extra), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.addCleanup(lambda: pr.poll() is None and (pr.kill(), pr.wait()))  # a failed assertion never leaves a caller blocked on its fifo
        with open(g) as fh:
            return pr, fh.read().strip()

    def release(self, name, pr):
        with open(f"{self.h}/{name}.f", "w") as fh:
            fh.write("go\n")
        self.assertEqual(pr.wait(timeout=120), 0)


AV = "held out (PICK_AVOID: row links.avoid main; released-row main rule: "


class ReleasedMain(Base):
    # (1) released row, week 47 <= 60 - 4, rise 0 < 5, no path waiter: main is eligible, and the caller holds the marker
    def test_1_granted(self):
        got, err = self.pick([main_line(47)], PICK_ITEM="rel-a")
        self.assertEqual(got, "/x/claude-main", err)
        self.assertEqual(self.holder(), ["rel-a", str(os.getpid())])

    def test_1_boundary_pace_minus_4_and_rise_4_granted(self):
        self.assertEqual(self.pick([main_line(56)], rise=4, PICK_ITEM="rel-a")[0], "/x/claude-main")

    def test_1_continue_round_is_its_row(self):
        self.assertEqual(self.pick([main_line(47)], PICK_ITEM="rel-a-c031500")[0], "/x/claude-main")
        self.assertEqual(self.holder(), ["rel-a", str(os.getpid())])

    # (2) week = pace - 3: avoided, told why; no PICK_MAIN_PACE line: avoided
    def test_2_pace_minus_3_avoided(self):
        got, err = self.pick([main_line(57)], PICK_ITEM="rel-a")
        self.assertIsNone(got)
        self.assertIn("main: " + AV + "week 57 > PICK_MAIN_PACE line 60.0 - 4)", err)
        os.remove(f"{self.h}/flag-PICK_MAIN_PACE")
        got, err = self.pick([main_line(47)], PICK_ITEM="rel-a")
        self.assertIsNone(got)
        self.assertIn(AV + "no PICK_MAIN_PACE line)", err)
        self.assertIsNone(self.holder())

    # (3) rise = 5 over 300 min: avoided; no fresh log: avoided
    def test_3_rise_5_avoided(self):
        got, err = self.pick([main_line(47)], rise=5, PICK_ITEM="rel-a")
        self.assertIsNone(got)
        self.assertIn(AV + "week +5 pt in 5 h >= 5)", err)
        got, err = self.pick([main_line(47)], rise=None, PICK_ITEM="rel-a")
        self.assertIsNone(got)
        self.assertIn(AV + "week trend unknown)", err)
        self.assertIsNone(self.holder())

    # (4) a live Nov 23 path waiting marker: the released row yields on every account; once it is gone, main is granted
    def test_4_path_waiter_refuses(self):
        for d, content in (("pick-waiting", "2026-11-17T03:00Z path-x-build\n"), ("pick-waiting-main", "1 2026-11-17T03:00Z path-x\n")):
            with self.subTest(d=d):
                self.put(d, "path-x", content)
                got, err = self.pick([main_line(47), FIVEX], PICK_ITEM="rel-a")
                self.assertIsNone(got)
                self.assertIn("PICK_WHY: yield: Nov 23 path row path-x waiting", err)
                self.assertIsNone(self.holder())
                os.remove(f"{self.m}/{d}/path-x")
        self.assertEqual(self.pick([main_line(47)], PICK_ITEM="rel-a")[0], "/x/claude-main")

    # (5) a second released row while a live holder (this process) has main: avoided, told why; the holder keeps main
    def test_5_second_released_row_avoided(self):
        self.assertEqual(self.pick([main_line(47)], PICK_ITEM="rel-a")[0], "/x/claude-main")
        got, err = self.pick([main_line(47)], PICK_ITEM="rel-c")
        self.assertIsNone(got)
        self.assertIn(AV + "main held by released row rel-a (pid %d))" % os.getpid(), err)
        self.assertEqual(self.holder(), ["rel-a", str(os.getpid())])
        # it may still take another account
        self.assertEqual(self.pick([main_line(47), FIVEX], PICK_ITEM="rel-c")[0], "/x/claude-saeedi.danial")

    # (6) the same row's second session joins; the marker stays until its last pid exits; a give-back takes back only its own
    def test_6_same_row_second_session_joins(self):
        p1, a1 = self.hold("s1", [main_line(47)], PICK_ITEM="rel-a")
        p2, a2 = self.hold("s2", [main_line(47)], PICK_ITEM="rel-a-c031500")
        self.assertEqual((a1, a2), ("/x/claude-main", "/x/claude-main"))
        self.assertEqual(self.holder(), ["rel-a", str(p1.pid), str(p2.pid)])
        # a session of the row admitted by the rule but refused by the worker cap gives back only its own grant
        got, err = self.pick([main_line(47)], busy="/x/claude-main=3", PICK_ITEM="rel-a")
        self.assertIsNone(got)
        self.assertIn("main worker cap 3/3", err)
        self.assertEqual(self.holder(), ["rel-a", str(p1.pid), str(p2.pid)])
        self.release("s1", p1)
        got, err = self.pick([main_line(47)], PICK_ITEM="rel-c")
        self.assertIsNone(got)
        self.assertIn("main held by released row rel-a (pid %d)" % p2.pid, err)
        self.release("s2", p2)
        # the marker is free now, but the cap-refused session of rel-a (FEATURE-QUEUE.tsv 9) still waits: it ranks first
        got, err = self.pick([main_line(47)], PICK_ITEM="rel-c")
        self.assertIsNone(got)
        self.assertIn("main kept for better-ranked released row rel-a", err)
        os.remove(f"{self.m}/pick-waiting-relmain/rel-a")
        self.assertEqual(self.pick([main_line(47)], PICK_ITEM="rel-c")[0], "/x/claude-main")
        self.assertEqual(self.holder(), ["rel-c", str(os.getpid())])

    def test_6_same_holder_counts_grants(self):
        self.assertEqual(self.pick([main_line(47)], PICK_ITEM="rel-a")[0], "/x/claude-main")
        self.assertEqual(self.pick([main_line(47)], PICK_ITEM="rel-a")[0], "/x/claude-main")
        self.assertEqual(self.holder(), ["rel-a", "%d:2" % os.getpid()])
        self.assertIsNone(self.pick([main_line(47)], busy="/x/claude-main=3", PICK_ITEM="rel-a")[0])
        self.assertEqual(self.holder(), ["rel-a", "%d:2" % os.getpid()])

    # (7) a marker whose pids are all dead (or that has none): cleared, the new row holds it
    def test_7_dead_pid_marker_cleared(self):
        open(self.marker, "w").write(f"rel-c {dead_pid()} {dead_pid()}:2 junk\n")
        self.assertEqual(self.pick([main_line(47)], PICK_ITEM="rel-a")[0], "/x/claude-main")
        self.assertEqual(self.holder(), ["rel-a", str(os.getpid())])
        open(self.marker, "w").write("garbage\n")
        self.assertEqual(self.pick([main_line(47)], PICK_ITEM="rel-c")[0], "/x/claude-main")
        self.assertEqual(self.holder(), ["rel-c", str(os.getpid())])

    # (8) the main worker cap full: still refused (the rule admitted it, the cap refuses it), the marker given back, the row
    # waits for main (pick-waiting-relmain/) until any pick of it succeeds
    def test_8_cap_full_refused(self):
        got, err = self.pick([main_line(47)], busy="/x/claude-main=3", PICK_ITEM="rel-a")
        self.assertIsNone(got)
        self.assertIn("main: main worker cap 3/3", err)
        self.assertIsNone(self.holder())
        self.assertTrue(os.path.exists(f"{self.m}/pick-waiting-relmain/rel-a"))
        # unknown 5-h: the taper halves the cap to 2
        got, err = self.pick([main_line(47, -1).replace(te.field(3), "?")], busy="/x/claude-main=2", PICK_ITEM="rel-a")
        self.assertIsNone(got)
        self.assertIn("main worker cap 2/2", err)
        self.assertEqual(self.pick([main_line(47)], busy="/x/claude-main=2", PICK_ITEM="rel-a")[0], "/x/claude-main")
        self.assertFalse(os.path.exists(f"{self.m}/pick-waiting-relmain/rel-a"))

    # (9) a row with links.avoid main but no links.released: unchanged (held out by PICK_AVOID), while the released row in the
    # same pick is granted; a coordinator caller of a released row and any other "main" in PICK_AVOID stay held out too
    def test_9_non_released_unchanged(self):
        for extra in ({"PICK_ITEM": "plain-avoid"}, {"PICK_ITEM": "rel-a", "PICK_COORD": "1"},
                      {"PICK_ITEM": "rel-a", "PICK_AVOID": "main", "PICK_AVOID_RCX": "main"}, {"PICK_ITEM": "rel-a", "PICK_AVOID": "claude-main"}):
            with self.subTest(**extra):
                got, err = self.pick([main_line(47)], **extra)
                self.assertIsNone(got)
                self.assertIn("main: held out (PICK_AVOID) (5-h 10%, week 47%)", err)
                self.assertNotIn("released-row", err)
                self.assertIsNone(self.holder())
        self.assertEqual(self.pick([main_line(47)], PICK_ITEM="rel-a")[0], "/x/claude-main")

    # the row's other avoid entries stay
    def test_other_avoid_entries_stay(self):
        got, err = self.pick([main_line(57), FIVEX], PICK_ITEM="rel-d")
        self.assertIsNone(got)
        self.assertIn("saeedi.danial: held out (PICK_AVOID)", err)
        self.assertIn("main: " + AV + "week 57", err)
        self.assertEqual(self.pick([main_line(47), FIVEX], PICK_ITEM="rel-d")[0], "/x/claude-main")

    # rank order: a live waiter of a better rank (rel-b: FEATURE-QUEUE.tsv 5 < rel-a 9) takes the free marker first
    def test_rank_order(self):
        self.put("pick-waiting-relmain", "rel-b", "2026-11-17T03:00Z rel-b\n")
        got, err = self.pick([main_line(47)], PICK_ITEM="rel-a")
        self.assertIsNone(got)
        self.assertIn(AV + "main kept for better-ranked released row rel-b (waiting", err)
        self.assertTrue(os.path.exists(f"{self.m}/pick-waiting-relmain/rel-a"))  # refused because main is taken: it waits too
        self.assertEqual(self.pick([main_line(47)], PICK_ITEM="rel-b")[0], "/x/claude-main")  # rel-a's wait does not hold rel-b
        self.assertFalse(os.path.exists(f"{self.m}/pick-waiting-relmain/rel-b"))
        self.assertEqual(self.holder(), ["rel-b", str(os.getpid())])

    def test_rank_order_stale_or_unreleased_waiter_ignored(self):
        self.put("pick-waiting-relmain", "rel-b", "2026-11-17T02:00Z rel-b\n", age=900)
        self.put("pick-waiting-relmain", "plain-avoid", "2026-11-17T03:00Z plain-avoid\n")
        self.assertEqual(self.pick([main_line(47)], PICK_ITEM="rel-a")[0], "/x/claude-main")

    def test_rank_order_pick_critical_rank_first(self):  # a queued row ranks after a tm-* row (pick_critical rank 2) unqueued
        rows = ROWS + [{"id": "tm-rel", "status": "ready", "links": {"avoid": "main", "released": REL}}]
        open(f"{self.m}/BACKLOG.jsonl", "w").write("".join(json.dumps(r) + "\n" for r in rows))
        self.put("pick-waiting-relmain", "tm-rel", "2026-11-17T03:00Z tm-rel\n")
        got, err = self.pick([main_line(47)], PICK_ITEM="rel-b")
        self.assertIsNone(got)
        self.assertIn("main kept for better-ranked released row tm-rel", err)


if __name__ == "__main__":
    unittest.main(verbosity=1)
