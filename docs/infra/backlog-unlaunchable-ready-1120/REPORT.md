# backlog-unlaunchable-ready-1120: refuse "ready" when nobody starts the row; list unlaunched ready rows in the hourly digest

INSTALLED (2026-11-20 12:10Z, backups `<file>.bak-20261120T1210Z-bkunl`; see "Install record" below). No DELTA row (control
plane only). No VE product change: the VE branch carries one commit, the saved record under
docs/infra/backlog-unlaunchable-ready-1120/ (the pre-review gate's [commits] check needs one). No flag, trial or new service.
Row: backlog-unlaunchable-ready-1120 (orchestrator BATCH 2026-11-20T08:59:59Z, inbox/dri/done/20261120T085959Z-orchestrator-1582945.md).

SIZE: 245 product, 306 tests, 0 other hand-written lines (product: backlog.py +219/-25, infra_feed.py +3/-3, backlog.sh +2,
tools-local/coord_diet.py +21/-1; tests: tools-local/test_backlog_unlaunchable.py 299 new, tools-local/test_infra_feed.py +7/-2).

## Where things are (found first)

- Rows are written by `backlog.sh` -> `backlog.py main()` (add / update / update-status) and by `backlog.py seed()` (svc-backlog,
  backlog-svc.sh, every 10 min; its "unblock" step turns a blocked row ready by itself).
- The orchestrator's hourly digest is `tools-local/coord_diet.py digest-take`, which inbox-wait.sh calls (hourly, keepalive,
  with a wake). coord-diet-loop.sh does not write the digest; it is unchanged.
- Launchers' own selection code: infra_feed.py `item_reason` (FEED_KINDS + backlog.FEED_OWNER; a planner design row only with
  a launch link), backlog.py `queue_gap` (the seed's feature feed: kind feature, links.task an existing prompts/task-<x>.txt,
  a paths source, not the lead's, no links.launch/delegate), prompts/dri-task-featureplan.txt (the daily planner reads
  `--kind feature,follow-up,design`; it starts no design row: dri-lp0847), tools-local/decider-ready-alert.py (owner
  "DRI decider"), src_delegates (rows owned "delegate <name>", seeded ready, started by hand).

## What was built (staged as `<file>.new-bkunl`; installed files untouched, sha256 checked before and after)

1. **One table, read by both sides.** `backlog.py START_TABLE` + `start_rule(r)`: first matching row wins.

   | kinds | owner (fullmatch, case-insensitive) | when | launcher | needs |
   |---|---|---|---|---|
   | feature | anything not starting "lead" | links.task, no links.launch/delegate | feature feed (seed queue gap) | paths |
   | feature, follow-up | `feature planner…` | | feature planner (daily) | |
   | infra, efficiency, trial, design | FEED_OWNER: '', infra feed, orchestrator, orchestrator (infra), dri, acting dri | | infra feed | |
   | design | `feature planner…` | links.launch | infra feed | |
   | any | contains "decider" | | DRI decider (by hand) | |
   | any | `dri-…`, `research wave…`, `scope…`, or containing the word "delegate" | | named delegate (by hand) | |

   Also: origin queue = feature feed; origin chain = its infra-item.sh chain. Not launched and never refused: kinds decision
   and lead-question, origins limits and flag (NOW.md already skips these). Readers: `launcher()` (launchable, NOW.md "Ready
   with no launcher"), `ready_refusal()` (new), `queue_gap` (now selects with `start_rule(r)[0] == "feature feed"`), infra_feed.py
   `item_reason` (now `bl.start_rule`). The feature feed's task-file test moved out of queue_gap into `feed_task()`, which
   queue_gap and ready_refusal both call (skip reasons in NOW.md unchanged).
2. **Refusal.** `ready_refusal(r)`: a one-line reason when START_TABLE names no launcher for the row, or the launcher needs a
   paths source and `feed_task()` fails (links.task missing or not prompts/task-<x>.txt, or no "Paths:" line and no
   links.paths / SPRINT-ITEMS.tsv paths). Applied to:
   - `add --status ready`, `update --status ready`, `update-status <id> ready`: `refused: <cmd> <id>: status ready, but <reason>`
     on stderr, exit 1, BACKLOG.jsonl not written;
   - an `update` that makes a launchable ready row unlaunchable (e.g. `--owner "infra planner"`), refused the same way;
   - the seed's unblock step: the row stays blocked, its state becomes `blockers merged; not set ready: <reason>` (written
     once, one stderr line in the svc-backlog log; idempotent).
   Rows already ready are not rewritten (a note update on one passes). `backlog.sh lint` lists them, plus the blocked rows the
   seed held, and exits 1 when there are any.
3. **Digest.** `backlog.sh unlaunched [--min-age 60]`: one line per ready row whose ready_t (else status_t, else created) is
   at least 60 min old and that has no live launch. A live launch is a running chain, delegate or ve-<x>-<n>.scope named by
   links.job, links.delegate, the launch spec or the id; a row in FEATURE-QUEUE.tsv; or feed-state/<id>.launched. Format:
   `id, age, owner: why`, where why is the refusal reason when there is one, else launchable()'s reason, else
   `<launcher>: not started (state: …)`. `coord_diet.py digest-take` prints `== ready > 60 min with no live launch: N (…)` and
   up to 40 `- ` lines (then "… N more") after the routine notices and before the backup line. It fails open to a "no reading"
   line, and the budget, drain and notice header lines keep their places (test_coord_budget asserts them).

## Live backlog: what lint refuses today (staged backlog.py, read-only; BACKLOG.jsonl sha256 unchanged)

`python3 -I backlog.py.new-bkunl lint` -> exit 1, 7 rows (live-lint-20261120.txt):

```
defs-repair-safety-framework-1119  ready feature   feature planner  feature feed: no paths source: prompts/task-defs-repair-safety-framework-1119.txt has no 'Paths:' line (nor links.paths, SPRINT-ITEMS.tsv)
defs-carried-oos-measure-1119      ready infra     infra planner    owner 'infra planner' has no launcher for kind infra (…)
fm-move-5h-room                    ready infra     operations seat  owner 'operations seat' has no launcher for kind infra (…)
srccov-safety-framework-1119       ready infra     feature planner  owner 'feature planner' has no launcher for kind infra (…)
usage-watch-reset-fresh            ready infra     operations seat  owner 'operations seat' has no launcher for kind infra (…)
exp-g1-vocab-readings              ready follow-up -                no owner (follow-up rows are not fed)
eff-20261104-1-inventories-read    ready follow-up -                no owner (follow-up rows are not fed)
```

All three defect classes from the BATCH show up (a: srccov-safety-framework-1119; b: defs-repair-safety-framework-1119;
c: defs-carried-oos-measure-1119). `unlaunched` lists 15 rows today (live-unlaunched-20261120.txt), including the 7 above,
two decider rows not started (gcp-credit-watch-1119 11.8 d, train-legs-time-1120 6.3 h), a FEED_OWNER design row with no
launch link (record-void-fix-b-rechallenge 3.8 d) and four delegate/template rows.

## Tests (run directly: `python3 -I tools-local/<test>.py`)

- `BL_SCRIPT=backlog.py.new-bkunl IF_PY=infra_feed.py.new-bkunl CD_SCRIPT=tools-local/coord_diet.py.new-bkunl python3 -I
  tools-local/test_backlog_unlaunchable.py` -> `Ran 11 tests … OK` (test-staged.log). Toy BACKLOG files under a temp dir only.
  It covers: each refused pair (11 cases) through add, update-status and update; row unchanged (byte-compare); one stderr line;
  the update that breaks a launcher; a row already ready is not rewritten and lint lists it; each allowed pair (16 cases) through
  all three commands; decision and lead-question rows; other statuses never refused; the seed holding a blocked row (and being
  idempotent) while unblocking a launchable one; infra_feed item_reason reading the same table; the unlaunched lines (age,
  job running, delegate running, FEATURE-QUEUE.tsv); the digest block.
- **On the installed code** (`python3 -I tools-local/test_backlog_unlaunchable.py`): `FAILED (failures=25, errors=19)`
  (test-installed-summary.txt).
- Affected suites (the 23 tools-local tests that load backlog.py, infra_feed.py or coord_diet.py), run in a scratch copy with
  the staged files (affected-suites-staged.log) and with the installed files (affected-suites-installed-baseline.log). Results
  are the same, except test_infra_feed `test_launcher_classes` (updated, below) and two scratch-only artefacts that I re-ran in
  place: test_backlog_now with `BL_SCRIPT=backlog.py.new-bkunl` OK 34/34; test_coord_budget OK 24/24 once its data dir was
  copied in.
- Pre-existing failures, the same on installed and staged code and not touched here: test_infra_feed HostWidth x2 and
  RemoteLoad x3 (also fail in the live dir on the installed code), and test_infra_urgent_adv1658
  `test_plain_row_env_unchanged` (same).
- `test_infra_feed.py` `test_launcher_classes` asserted the defect: an infra row owned by "feature planner" was
  `(True, "feature planner")`. Changed to expect "has no launcher". The `dri-backlog` owner now gets `(True, "named delegate (by
  hand)")`, and an "infra planner" row was added to keep a has-no-launcher case (staged as test_infra_feed.py.new-bkunl).

## Seeded bugs (Python only; the only language changed). Each planted in a /tmp copy, run, removed (seeded-bugs.txt)

| # | file | bug | failing test(s) |
|---|---|---|---|
| M1 | backlog.py | CLI refuses only broken updates, not explicit ready writes | test_add_status_ready_refused_for_each_pair, test_update_status_and_update_refused_row_unchanged |
| M2 | backlog.py | START_TABLE feature-planner rule also covers infra (defect a back) | 5 tests, incl. test_item_reason_names_the_missing_launcher, test_blocked_row_turning_ready_by_itself_is_refused |
| M3 | backlog.py | feature-feed task with no Paths line accepted (defect b back) | test_add_status_ready_refused_for_each_pair, test_update_status_and_update_refused_row_unchanged, test_blocked_row_turning_ready_by_itself_is_refused |
| M4 | backlog.py | seed unblocks without the check | test_blocked_row_turning_ready_by_itself_is_refused |
| M5 | backlog.py | digest counts FEATURE-QUEUE.tsv rows as not launched | test_lines_id_age_owner_why, test_digest_lists_them |
| M6 | tools-local/coord_diet.py | digest without the unlaunched block | test_digest_lists_them |
| M7 | infra_feed.py | owner test back to "starts it, not this feed" for an unlaunchable pair | test_item_reason_names_the_missing_launcher |

## Install (waits for the decider's read)

```
cd /home/seyran/code/manage-agents
zsh -n backlog.sh.new-bkunl && python3 -m py_compile backlog.py.new-bkunl infra_feed.py.new-bkunl tools-local/coord_diet.py.new-bkunl tools-local/test_infra_feed.py.new-bkunl
T=$(date -u +%Y%m%dT%H%MZ)
for f in backlog.py infra_feed.py backlog.sh tools-local/coord_diet.py tools-local/test_infra_feed.py; do cp -p $f $f.bak-$T-bkunl && mv $f.new-bkunl $f; done
python3 -I tools-local/test_backlog_unlaunchable.py && python3 -I tools-local/test_backlog_queue_gap.py && python3 -I tools-local/test_backlog_now.py
```

Scope restart: none needed. svc-backlog (backlog-svc.sh), svc-infra-feed (infra-feed.sh) and inbox-wait.sh start a fresh
`python3 -I <script>` every pass, so the next pass reads the new files. Rollback: `mv <f>.bak-$T-bkunl <f>` for the same five.

## Install record (after the decider's read)

- The five files were installed at 12:10Z with the backup + mv commands above (backups
  `<file>.bak-20261120T1210Z-bkunl`, all five differ from the installed files; sha256 of both sets in the VE record).
- On the installed code: `python3 -I tools-local/test_backlog_unlaunchable.py` -> `Ran 11 tests … OK` (test-after-install.log);
  `python3 -I backlog.py lint` -> exit 1, the same 7 rows as before install (live-lint-after-install.txt).
- Pre-review gate sent the item back for [commits] (0 commits ahead on the VE branch). Fixed by committing the saved record
  to docs/infra/backlog-unlaunchable-ready-1120/ on infra/backlog-unlaunchable-ready-1120: this REPORT, the five
  backup-vs-installed diffs, the new test file (as .txt), the test logs (staged, installed-before, after-install), live lint
  and unlaunched lists, seeded-bugs.txt and sha256.txt. Documentation only; no VE product code, no generated file.

## Notes for the DRI

- Conservative choices taken (refuse rather than accept), not asked:
  - "operations seat", "eff pass", "DRI (<topic>)" and other free-text owners have no launcher. Two operations-seat rows are
    ready today and appear in lint.
  - Follow-up rows with no owner are refused, matching the existing launcher text "not fed". A feature-planner-owned
    follow-up passes.
  - A feature row with links.task is the feature feed's whatever its owner, so it needs a paths source even if the owner is
    the decider.
- Not refused, because current practice relies on them: infra-feed rows with no task file yet (decider-ready-alert's "ready
  with no task file" covers them), FEED_OWNER design rows with no launch link, and delegate/decider/template rows.
- `unlaunched` lists every ready row as the task asks, including templates (dri-srccov-shard-TEMPLATE) and decision rows. That
  is about 15 lines today; the digest shows up to 40.
- The digest prints only when there are pending routine notices (unchanged rule). An hour with no notices shows no unlaunched
  block either; `zsh backlog.sh unlaunched` answers at any time.
- The seed's other ready writes (src_delegates "written, not launched yet", src_requests, queue rows) follow their source's
  evidence and are not gated. lint lists any of them that START_TABLE does not cover.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no Lean, no relayed answer).
2. Every deliverable built, no rule broken: PASS. Refusal for all four write paths, the one table, lint, the digest line and the
   tests are all present; install staged per INSTALL READ (test_backlog_unlaunchable.py, all 11).
3. Tests can fail: PASS. They fail on the installed code (25 failures, 19 errors), and the 7 seeded bugs are each caught.
4. Python/Lean/Rust agree, valid inputs pass: PASS for the Python side. 16 allowed pairs are accepted
   (test_each_allowed_pair_is_accepted_by_every_command), and the existing suites match the baseline.
5. R8 binding: N.A.
6. Gate evidence matches final HEAD: PASS. The VE commit is documentation only (docs/infra/backlog-unlaunchable-ready-1120/);
   the chain gates that final HEAD.
7. No unsigned item left: PASS. No DELTA row (control plane only, as the task states).
8. User-visible change in DELTA: N.A. (control plane only, no DELTA row by the task).
9. Test selection: N.A. for VE (docs-only record, no product or test change). The manage-agents suites that load the changed files were listed and run (23).
10. Lean statements: N.A.
11. Budgets/limits fail closed: PASS. Status ready is refused when the launcher is unknown or the task-file test fails. The
    digest fails open to a "no reading" line, as its neighbours do (test_digest_lists_them).
12. No CPU/memory regression: PASS. One extra subprocess per digest (its systemctl call is capped at 60 s, the whole call at
    120 s), and one regex table scan per row.
13. Test-removed trailer: N.A. (no test removed or renamed; test_launcher_classes was edited in place).
14. Both directions, cited evidence: PASS. Refused and allowed pairs are both tested; live lint output is saved.
15. FIX classes: PASS. The table's single owner is cited; no copy of FEED_OWNER or of the queue-gap rule is left.
