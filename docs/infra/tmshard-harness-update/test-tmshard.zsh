#!/bin/zsh
# 2026-10-28 dri-tmshard: tests for tm-shard.sh (size, dispatch, state, merge) and its hooks in cloud-pull.sh and
# cloud-overflow.sh (staged as <file>.new-tmshard until the infra item eff-tmshard merges; TMS_SUFFIX= tests the live ones).
# usage: zsh test-tmshard.zsh. Private scratch (mktemp); the VE tool (--plan/--merge) and cloud-dispatch.sh are stubs; the
# "GitHub" remote is an empty local bare repo; no network, no real flag, job dir, log or trial log touched.
M=/home/seyran/code/manage-agents; SFX=${TMS_SUFFIX-.new-tmshard}
export CCLOUD_POOL_FLAG=/nonexistent/CLAUDE_CLOUD_POOL  # 2026-10-28 dri-claudecloud: the real flag never leaks into these tests
export TM_CODEX_VMLOAD_FLAG=/nonexistent/TM_CODEX_VMLOAD  # vm-offload-1108: nor this one (its section sets its own)
export TM_SHARD_RECORDS=/nonexistent  # tmshard-harness-update (tm-shard-actions-120): the live export's run records never leak into these tests
S=$(mktemp -d /tmp/tmshard-test.XXXXXX); [ -n "$KEEP" ] && print "scratch kept: $S" || trap 'rm -rf $S' EXIT
pass=0; fail=0; out=$S/out
ok(){ if eval "$2"; then pass=$((pass+1)); else fail=$((fail+1)); print -- "  FAIL $1"; sed 's/^/    /' $out 2>/dev/null | tail -8; fi; }
J=$S/jobs; mkdir -p $J $S/bin $S/wt; git init -q -b main $S/vm; git -C $S/vm -c user.name=t -c user.email=t@example.com commit -q --allow-empty -m a
SHA=$(git -C $S/vm rev-parse HEAD); S8=${SHA[1,8]}; git init -q --bare $S/gh.git
print -r -- 'CLOUD_MAX_INFLIGHT=4
ACTIONS_MAX_INFLIGHT=8' > $S/conf
export CLOUD_CONF=$S/conf CLOUD_JOBS_DIR=$J VE_EXPORT_SRC=$S/vm TM_SHARD_FLAG=$S/TM_SHARD CLOUD_REMOTE=$S/gh.git CLOUD_TRIAL_LOG=$S/trial.md \
  CLOUD_MSG="zsh $S/bin/msg" MAC_PYTEST_LOG=$S/none.jsonl CLOUD_TRIAL_FLAG=$S/CLOUD_TRIAL ACTIONS_POOL_FLAG=$S/ACTIONS_POOL VS_START="zsh $S/bin/vs" \
  VE_EXPORT_DIR=$S/vm GHA_TESTS_DIR=$S/gha-tests  # dri-advfix8: the live builder test shards never leak into these tests
mkdir -p $S/gha-tests
print -r -- 'print -r -- "msg $*" >> '$S'/msgs' > $S/bin/msg; print -r -- 'print -r -- "vs $*" >> '$S'/vs' > $S/bin/vs
# the VE tool: --plan prints $S/to_run mutants; --merge OUT PART... writes OUT from the parts (exit $S/merge_rc, default 1)
cat > $S/bin/tool <<X
#!/bin/bash
case "\$1" in
  --plan) echo "planning \$*" >> $S/plan-args; echo "{\"base\": \"b\", \"definitions\": 3, \"mutants\": 400, \"to_run\": \$(cat $S/to_run), \"not_run\": 0}";;
  --merge) o=\$2; shift 2; rc=\$(cat $S/merge_rc 2>/dev/null || echo 1); [ "\$rc" = 2 ] && { echo "parts disagree on inputs"; exit 2; }
    cat "\$@" > "\$o"; echo "trust_mutants: 9 KILLED, 1 SURVIVOR, 0 UNKNOWN, 0 INVALID, 0 ALLOWED, 0 NOT RUN in 5 s"; exit \$rc;;
esac
X
chmod +x $S/bin/tool; export TM_SHARD_TOOL=$S/bin/tool
# cloud-dispatch.sh: records its args and writes a job.json as the real one does (status $S/dstatus, default dispatched)
cat > $S/bin/dispatch <<'X'
#!/bin/zsh
print -r -- "dispatch $*" >> $DREC
wt=""; pool=${CLOUD_DISPATCH_POOL:-claude}; while [[ $1 == --* ]]; do case $1 in --worktree) wt=$2; shift 2;; --pool) pool=$2; shift 2;; *) shift;; esac; done
item=$1; sha=$2; shift 2; [ "$1" = -- ] && shift; dest=""; a=("$@"); for ((i=1; i<=$#a; i++)); do [ "${a[i]}" = --json ] && dest=${a[i+1]}; done
case $item in *.s2of*) [ -f $DFAIL2 ] && exit 3;; esac
job=$item-${sha[1,8]}; mkdir -p $CLOUD_JOBS_DIR/$job
python3 -I -c 'import json,sys; json.dump({"job":sys.argv[2],"item":sys.argv[3],"status":sys.argv[4],"pool":sys.argv[5],"dest":sys.argv[6],"vm_head":sys.argv[7],"vm_base":"b"*40,"deadline":int(sys.argv[8]),"waiter":int(sys.argv[9] or 0),"cloud_args":sys.argv[10:],"vm_args":sys.argv[10:],"generated":1,"branch":"claude/cloud-tm-"+sys.argv[2],"exp_head":"e"*40,"worktree":""},open(sys.argv[1],"w"))' \
  $CLOUD_JOBS_DIR/$job/job.json $job $item ${DSTATUS:-dispatched} $pool "${dest:-x}" $sha $(( $(date +%s) + 5400 )) "${CLOUD_WAITER:-0}" "$@"
print -r -- "prompt $job" > $CLOUD_JOBS_DIR/$job/prompt.txt
X
chmod +x $S/bin/dispatch; export TM_SHARD_DISPATCH="zsh $S/bin/dispatch" DREC=$S/drec DFAIL2=$S/dfail2
# 2026-10-31 dri-improve (L151): the sections before "first sweep" pin the old sizing (SPM 26 with no item reading, no
# hard-limit waiver); the "first sweep" section tests the new rules.
export TM_SHARD_ACTIONS_FIRST_SPM=26 TM_SHARD_ACTIONS_HARD=999999 TM_SHARD_ACTIONS_CANCEL=999999
TS=${TMS_TS:-$M/tm-shard.sh}; jv(){ python3 -I -c 'import json,sys; v=json.load(open(sys.argv[1])).get(sys.argv[2]); print(json.dumps(v) if isinstance(v,(list,dict)) else v)' $1 $2; }

print "== size"
ok "the default CONTROL is the measured 600 s (actions 338: 4 parts, ~1,652 s each)" '[ "$(env -u TM_SHARD_CONTROL zsh $TS size actions 338)" = "4 1652 107" ]'
export TM_SHARD_CONTROL=300  # the constants the cases below were written with (default 300 until the 2026-10-28 install)
ok "actions, 338 mutants (sc-5rb): 3 parts" '[ "$(zsh $TS size actions 338 | cut -d" " -f1)" = 3 ]'
ok "  each part estimated within the 1,800-s Actions target" '(( $(zsh $TS size actions 338 | cut -d" " -f2) <= 1800 ))'
ok "codex, 338: 4 parts, each <= 2,700 s" 'set -- $(zsh $TS size codex 338); [ $1 = 4 ] && (( $2 <= 2700 ))'
ok "under TM_SHARD_MIN (40): one part" '[ "$(zsh $TS size actions 39 | cut -d" " -f1)" = 1 ]'
ok "L168: under TM_SHARD_MIN but past the target (pc-1 37 mutants at 659 slot-s, room 4): 4 parts, ~2,747 s" '[ "$(env -u TM_SHARD_CONTROL TM_SHARD_ACTIONS_SPM=659 TM_SHARD_ACTIONS_NMAX=4 zsh $TS size actions 37 4)" = "4 2747 4" ]'
ok "L168: under TM_SHARD_MIN and within the target (1 mutant at 659): one part" '[ "$(TM_SHARD_ACTIONS_SPM=659 zsh $TS size actions 1 8 | cut -d" " -f1)" = 1 ]'
ok "room caps the parts (actions 2000 mutants, room 2)" '[ "$(zsh $TS size actions 2000 2 | cut -d" " -f1)" = 2 ]'
ok "NMAX caps them (actions: 8)" '[ "$(zsh $TS size actions 100000 | cut -d" " -f1)" = 8 ]'
ok "a constant from the environment (TM_SHARD_ACTIONS_TARGET=900): more parts" '(( $(TM_SHARD_ACTIONS_TARGET=900 zsh $TS size actions 338 | cut -d" " -f1) > 3 ))'
zsh $TS size nopool 5 > $out 2>&1; ok "an unknown pool: error" '[ $? != 0 ] && grep -q "unknown pool" $out'

print "== dispatch"
print 338 > $S/to_run
CLOUD_DISPATCH_POOL=actions zsh $TS dispatch --worktree $S/wt it $SHA -- --max-mutants 1000 --json $S/dest/it.json > $out 2>&1; RC=$?
ok "flag TM_SHARD off: exactly cloud-dispatch.sh with the same arguments" '[ $RC = 0 ] && [ "$(cat $S/drec)" = "dispatch --worktree $S/wt it $SHA -- --max-mutants 1000 --json $S/dest/it.json" ] && grep -q "unsharded (flag TM_SHARD off)" $out'
rm -rf $J/*(N) $S/drec; : > $S/TM_SHARD
CLOUD_DISPATCH_POOL=actions zsh $TS dispatch it $SHA -- --max-mutants 1000 > $out 2>&1
ok "no --worktree to plan in: unsharded" 'grep -q "unsharded (no --worktree" $out && [ $(wc -l < $S/drec) = 1 ]'
rm -rf $J/*(N) $S/drec; print 20 > $S/to_run
CLOUD_DISPATCH_POOL=actions zsh $TS dispatch --worktree $S/wt it $SHA -- --max-mutants 1000 > $out 2>&1
ok "a small run (20 mutants): one part, unsharded" 'grep -q "20 mutants to run fit one part" $out && [ $(wc -l < $S/drec) = 1 ] && ! grep -q -- --shard $S/drec'
rm -rf $J/*(N) $S/drec $S/plan-args; print 338 > $S/to_run; P=$J/it-$S8
CLOUD_WAITER=4242 CLOUD_DISPATCH_POOL=actions zsh $TS dispatch --worktree $S/wt it $SHA -- --max-mutants 1000 --test lean/VE/X.lean --jobs 16 --json $S/dest/it.json > $out 2>&1; RC=$?
ok "338 mutants on actions: 3 parts sent, exit 0" '[ $RC = 0 ] && [ $(wc -l < $S/drec) = 3 ] && grep -q "338 mutants to run on actions -> 3 parts" $out'
ok "  --plan got the caller's args without --json/--jobs, run in the worktree" 'grep -q -x "planning --plan --max-mutants 1000 --test lean/VE/X.lean" $S/plan-args'
ok "  each part: item <item>.sKof3, the caller's args + --shard K/3 --json <parent>/part-K.json, no waiter" 'for k in 1 2 3; do grep -q -x -- "dispatch --worktree $S/wt it.s${k}of3 $SHA -- --max-mutants 1000 --test lean/VE/X.lean --jobs 16 --json $S/dest/it.json --shard $k/3 --json $P/part-$k.json" $S/drec || return 1; [ "$(jv $J/it.s${k}of3-$S8/job.json waiter)" = 0 ] || return 1; done'
ok "  each part's job.json names its parent and shard" '[ "$(jv $J/it.s2of3-$S8/job.json parent)" = it-$S8 ] && [ "$(jv $J/it.s2of3-$S8/job.json shard)" = 2/3 ]'
ok "  the parent: the waiter's job name, dispatched, shards listed, the caller's dest and waiter, deadline after the parts'" '[ "$(jv $P/job.json status)" = dispatched ] && [ "$(jv $P/job.json shards)" = "[\"it.s1of3-$S8\", \"it.s2of3-$S8\", \"it.s3of3-$S8\"]" ] && [ "$(jv $P/job.json dest)" = $S/dest/it.json ] && [ "$(jv $P/job.json waiter)" = 4242 ] && (( $(jv $P/job.json deadline) > $(jv $J/it.s3of3-$S8/job.json deadline) ))'
# 2026-11-11 tm-inventory-flag-ma: trust_mutants --only @FILE (gate-train.sh's targeted inventory, one id per line) reaches
# --plan, every part and the parent's VM args as inline ids (a cloud pool or Actions cannot read a VM path)
rm -rf $J/*(N) $S/drec $S/plan-args; print 338 > $S/to_run; P=$J/it-$S8; printf 'M007\nM012\n\nM120\n' > $S/only.txt
CLOUD_DISPATCH_POOL=actions zsh $TS dispatch --worktree $S/wt it $SHA -- --max-mutants 1000 --only @$S/only.txt --json $S/dest/it.json > $out 2>&1; RC=$?
ok "tm-inventory-flag-ma: --only @FILE: --plan gets the ids inline" 'grep -q -x "planning --plan --max-mutants 1000 --only M007,M012,M120" $S/plan-args'
ok "  every part (sharded) gets --only <the ids> inline and no @FILE" 'n=$(wc -l < $S/drec); c=0; for k in {1..$n}; do grep -q -x -- "dispatch --worktree $S/wt it.s${k}of$n $SHA -- --max-mutants 1000 --only M007,M012,M120 --json $S/dest/it.json --shard $k/$n --json $P/part-$k.json" $S/drec && c=$((c+1)); done; [ $RC = 0 ] && (( n > 1 )) && [ $c = $n ] && ! grep -q only.txt $S/drec'
ok "  the parent's vm_args (the VM fallback) carry the ids inline" 'grep -q M007,M012,M120 $P/job.json && ! grep -q only.txt $P/job.json'
rm -rf $J/*(N) $S/drec $S/plan-args; print 20 > $S/to_run
CLOUD_DISPATCH_POOL=actions zsh $TS dispatch --worktree $S/wt it $SHA -- --max-mutants 1000 --only=@$S/only.txt > $out 2>&1; RC=$?
ok "  --only=@FILE on a small run (unsharded): cloud-dispatch.sh gets --only <the ids> inline" '[ $RC = 0 ] && [ "$(cat $S/drec)" = "dispatch --worktree $S/wt it $SHA -- --max-mutants 1000 --only M007,M012,M120" ]'
rm -rf $J/*(N) $S/drec; print 338 > $S/to_run
CLOUD_DISPATCH_POOL=actions zsh $TS dispatch --worktree $S/wt it $SHA -- --only M1,M2 --max-mutants 1000 > $out 2>&1; RC=$?
ok "  inline --only ids pass as given" '[ $RC = 0 ] && grep -q -- "-- --only M1,M2 --max-mutants 1000 --shard 1/" $S/drec'
rm -rf $J/*(N) $S/drec; : > $S/only-empty.txt
CLOUD_DISPATCH_POOL=actions zsh $TS dispatch --worktree $S/wt it $SHA -- --only @$S/missing.txt > $out 2>&1; RC=$?
ok "  an unreadable ids file: exit 2, nothing sent (never a full run)" '[ $RC = 2 ] && [ ! -e $S/drec ] && grep -q "ids file cannot be read" $out'
CLOUD_DISPATCH_POOL=actions zsh $TS dispatch --worktree $S/wt it $SHA -- --only @$S/only-empty.txt > $out 2>&1; RC=$?
ok "  an ids file with no id: exit 2, nothing sent" '[ $RC = 2 ] && [ ! -e $S/drec ] && grep -q "has no mutant id" $out'
rm -rf $J/*(N) $S/drec $S/plan-args
rm -rf $J/*(N) $S/drec; : > $S/dfail2
CLOUD_DISPATCH_POOL=actions zsh $TS dispatch --worktree $S/wt it $SHA -- --max-mutants 1000 > $out 2>&1; RC=$?
ok "a part not sent: the parent fails (exit 3), so the waiter takes the VM path at once" '[ $RC = 3 ] && [ "$(jv $P/job.json status)" = failed ] && grep -q "part 2 of 3 not sent" $out'
rm -rf $J/*(N) $S/drec $S/dfail2
CLOUD_DISPATCH_POOL=actions zsh $TS dispatch --worktree $S/wt it $SHA -- --max-mutants 1000 --shard 1/2 > $out 2>&1
ok "the caller already passed --shard: unsharded" 'grep -q "already passed --shard" $out && [ $(wc -l < $S/drec) = 1 ]'
rm -rf $J/*(N) $S/drec; for i in 1 2 3 4 5 6; do mkdir -p $J/busy$i; print '{"job":"busy'$i'","status":"dispatched","pool":"actions"}' > $J/busy$i/job.json; done
CLOUD_DISPATCH_POOL=actions zsh $TS dispatch --worktree $S/wt it $SHA -- --max-mutants 1000 > $out 2>&1
ok "  6 Actions jobs in flight (cap 8): room 2 -> 2 parts" 'grep -q -- "-> 2 parts" $out && [ $(wc -l < $S/drec) = 2 ]'
print "== dispatch under queue pressure (dri-advfix8: shard-room.py, room = cap - busy - reserve)"
qd(){ rm -f $S/drec; CLOUD_DISPATCH_POOL=${2:-actions} zsh $TS dispatch --worktree $S/wt it $SHA -- --max-mutants 5000 > $out 2>&1; QRC=$?; rm -rf $J/it*(N); }
gt(){ mkdir -p $S/gha-tests/$1; python3 -I -c 'import json,sys,time; n=int(time.time()); json.dump({"status":sys.argv[2],"shards":int(sys.argv[3]),"created":n-int(sys.argv[4]),"deadline":n+int(sys.argv[5])},open(sys.argv[1],"w"))' $S/gha-tests/$1/run.json $2 $3 $4 $5; }
arr(){ local k; for k in $(seq 1 $1); do mkdir -p $J/arr$2$k; python3 -I -c 'import json,sys,time; d={"job":sys.argv[2],"status":"pulled","pool":sys.argv[3],"generated":int(time.time())-600}; d.update({"parent":"x"} if sys.argv[4]=="part" else {}); json.dump(d,open(sys.argv[1],"w"))' $J/arr$2$k/job.json arr$2$k ${3:-actions} ${4:-job}; done; }
rm -rf $J/*(N) $S/gha-tests/*(N); print 2000 > $S/to_run
qd; ok "spare capacity: the latency n (2000 mutants, cap 8: 8 parts), room line logged" 'grep -q -- "-> 8 parts" $out && grep -q "room 8: cap 8 - busy 0 - reserve 0 for 0 arrivals/h" $out'
gt sel1 dispatched 4 300 1800; gt sel0 done 6 300 1800; gt sel2 dispatched 3 300 -60
qd; ok "builder selected-test shards in flight count as busy on Actions (4 live; done or past-deadline runs not), their 3 runs are arrivals: 8 - 4 - 2 = 2 parts" 'grep -q -- "-> 2 parts" $out && grep -q "busy 4 - reserve 2 for 3 arrivals/h" $out'
rm -rf $S/gha-tests/*(N); arr 3 a
qd; ok "3 runs arrived in the last hour (target 1800 s): reserve ceil(3 x 0.5) = 2 -> 6 parts" 'grep -q -- "-> 6 parts" $out && grep -q "reserve 2 for 3 arrivals/h" $out'
rm -rf $J/*(N); arr 5 p actions part
qd; ok "  parts are not arrivals (their parent is)" 'grep -q -- "-> 8 parts" $out'
rm -rf $J/*(N); for i in 1 2 3 4 5 6 7 8; do mkdir -p $J/busy$i; print '{"job":"busy'$i'","status":"dispatched","pool":"actions"}' > $J/busy$i/job.json; done
qd; ok "a full pool (8 of 8 busy): fewer shards, down to one part (unsharded), never refused" '[ $QRC = 0 ] && grep -q "fit one part on actions.*room 0: cap 8 - busy 8" $out && [ $(wc -l < $S/drec) = 1 ]'
rm -rf $J/*(N); print 450 > $S/to_run; arr 4 x codex
qd it codex; ok "codex: reserve 3 of cap 6 would make 3 parts past the ~60-min task limit: waived only to room 4 (450 -> 4 parts, not the VM)" '[ $QRC = 0 ] && grep -q "450 mutants to run on codex -> 4 parts.*reserve waived to room 4" $out'
rm -rf $J/*(N) $S/gha-tests/*(N); print 338 > $S/to_run

rm -rf $J/*(N) $S/drec
CLOUD_DISPATCH_POOL=codex TM_SHARD_CODEX_NMAX=2 zsh $TS dispatch --worktree $S/wt it $SHA -- --max-mutants 1000 > $out 2>&1; RC=$?
ok "codex: parts that would pass its ~60-min task limit are not sent (exit 3, VM path)" '[ $RC = 3 ] && grep -q "tasks die at ~60 min" $out && [ ! -e $S/drec ]'
rm -rf $J/*(N) $S/drec; git -C $S/vm show $SHA:tools/trust_mutants.py > /dev/null 2>&1
TM_SHARD_TOOL= CLOUD_DISPATCH_POOL=actions zsh $TS dispatch --worktree $S/wt it $SHA -- --max-mutants 1000 > $out 2>&1
ok "a commit whose trust_mutants.py has no --shard (before eff-tmshard): unsharded" 'grep -q "has no --shard" $out && [ $(wc -l < $S/drec) = 1 ]'

print "== dispatch on codex (2026-10-28 dri-tmshardon)"
rm -rf $J/*(N) $S/drec; rm -f $S/TM_SHARD; print 338 > $S/to_run
CLOUD_DISPATCH_POOL=codex zsh $TS dispatch --worktree $S/wt it $SHA -- --max-mutants 1000 > $out 2>&1; RC=$?
ok "codex, flag TM_SHARD off: not sent unsharded (exit 3, VM path)" '[ $RC = 3 ] && grep -q "not sent to codex unsharded (flag TM_SHARD off)" $out && [ ! -e $S/drec ]'
: > $S/TM_SHARD; rm -rf $J/*(N) $S/drec
for i in 1 2 3 4 5 6 7 8; do mkdir -p $J/a$i; print '{"job":"a'$i'","status":"dispatched","pool":"actions"}' > $J/a$i/job.json; done
for i in 1 2; do mkdir -p $J/x$i; print '{"job":"x'$i'","status":"dispatched","pool":"codex"}' > $J/x$i/job.json; done
CLOUD_DISPATCH_POOL=codex zsh $TS dispatch --worktree $S/wt it $SHA -- --max-mutants 1000 > $out 2>&1; RC=$?
ok "codex room counts Codex jobs only (8 Actions + 2 Codex in flight, cap 6): 338 -> 4 parts" '[ $RC = 0 ] && grep -q "338 mutants to run on codex -> 4 parts" $out && [ $(wc -l < $S/drec) = 4 ]'
rm -rf $J/*(N) $S/drec; print 20 > $S/to_run
CLOUD_DISPATCH_POOL=codex zsh $TS dispatch --worktree $S/wt it $SHA -- --max-mutants 1000 > $out 2>&1; RC=$?
ok "codex, a run that fits one part (20 mutants): sent unsharded" '[ $RC = 0 ] && grep -q "20 mutants to run fit one part on codex" $out && [ $(wc -l < $S/drec) = 1 ]'
rm -rf $J/*(N) $S/drec; print 338 > $S/to_run
CLOUD_DISPATCH_POOL=codex zsh $TS dispatch --worktree $S/wt it $SHA -- --max-mutants 1000 --rescore p.json > $out 2>&1; RC=$?
ok "codex, --rescore: exit 3, never a whole run on codex" '[ $RC = 3 ] && grep -q "not sent to codex unsharded" $out && [ ! -e $S/drec ]'

print "== measured cost per mutant, --rescore on Actions (2026-10-30 dri-improve, L143)"
cat > $S/bin/spm <<'X'
import os
if os.path.exists(os.environ["SPMV"]):
    print(open(os.environ["SPMV"]).read())
X
export SPMV=$S/spmv TM_SPM=$S/bin/spm TM_SPM_OFF_FLAG=$S/TM-SPM-OFF
tsp(){ rm -rf $J/*(N) $S/drec; (cd $S/wt && CLOUD_DISPATCH_POOL=actions TM_SHARD_DISPATCH="zsh $S/bin/dispatch" DREC=$S/drec DFAIL2=$S/nope zsh $TS dispatch --worktree $S/wt it $SHA -- "$@") > $out 2>&1; }
: > $S/TM_SHARD; print 69 > $S/to_run; rm -f $S/spmv
tsp --max-mutants 1000; ok "no reading: the constant, 69 mutants one part" 'grep -q "fit one part on actions" $out && [ $(grep -c "^dispatch" $S/drec) = 1 ]'
print '216 item' > $S/spmv; tsp --max-mutants 1000
ok "measured 216 slot-s (item): 69 mutants -> 4 parts (heavy NMAX), the reading named" 'grep -q "\-> 4 parts" $out && grep -q "measured 216 slot-s per mutant (item)" $out && [ $(grep -c "^dispatch" $S/drec) = 4 ]'
print '12 pool' > $S/spmv; tsp --max-mutants 1000; ok "a reading below the constant: the constant" 'grep -q "fit one part on actions" $out && ! grep -q measured $out'
print '216 pool' > $S/spmv; : > $S/TM-SPM-OFF; tsp --max-mutants 1000; ok "veto TM-SPM-OFF: the constant" 'grep -q "fit one part on actions" $out'; rm -f $S/TM-SPM-OFF
print 'garbage' > $S/spmv; tsp --max-mutants 1000; ok "an unreadable reading: the constant" 'grep -q "fit one part on actions" $out'
print '216 item' > $S/spmv; print '{}' > $S/wt/prev.json; print 200 > $S/to_run; rm -f $S/plan-args
tsp --max-mutants 1000 --rescore prev.json --json out.json
ok "--rescore on Actions: sharded, every part carries it and its --shard" 'grep -q "\-> 4 parts" $out && [ $(grep -c -- "--rescore prev.json .*--shard" $S/drec) = 4 ]'
ok "  --plan is not given --rescore" '! grep -q rescore $S/plan-args'
tsp --max-mutants 1000 --rescore=prev.json; ok "  --rescore=FILE too" '[ $(grep -c -- "--rescore=prev.json .*--shard" $S/drec) = 4 ]'
print 5 > $S/to_run; tsp --max-mutants 1000 --rescore prev.json; ok "--rescore, too few mutants: one part, unsharded, with its --rescore" 'grep -q "fit one part on actions" $out && grep -q -- "--rescore prev.json" $S/drec'
rm -f $S/spmv
print "== first sweep and the 120-min Actions cancel (2026-10-31 dri-improve, L151)"
unset TM_SHARD_ACTIONS_FIRST_SPM TM_SHARD_ACTIONS_HARD TM_SHARD_ACTIONS_CANCEL; print 69 > $S/to_run
tsp --max-mutants 1000; ok "no reading: first-sweep floor 80 slot-s, 69 mutants -> 2 parts, named" 'grep -q "\-> 2 parts" $out && grep -q "first sweep: 80 slot-s per mutant (pool reading none, floor 80)" $out'
print '120 pool' > $S/spmv; tsp --max-mutants 1000; ok "a pool reading above the floor: used, NMAX 8 not the heavy 4 (69 -> 3 parts)" 'grep -q "\-> 3 parts" $out && grep -q "first sweep: 120" $out'
print '12 pool' > $S/spmv; tsp --max-mutants 1000; ok "a pool reading below the floor: the floor" 'grep -q "\-> 2 parts" $out && grep -q "first sweep: 80 slot-s per mutant (pool reading 12" $out'
print '12 item' > $S/spmv; tsp --max-mutants 1000; ok "the item's own light reading: the constant, one part (no floor)" 'grep -q "fit one part on actions" $out && ! grep -q "first sweep" $out'
print '216 item' > $S/spmv; tsp --max-mutants 1000; ok "the item's own heavy reading: heavy NMAX 4 as before (est <= 5400 s)" 'grep -q "\-> 4 parts" $out && ! grep -q waived $out'
print '216 item' > $S/spmv; print 248 > $S/to_run; tsp --max-mutants 1000
ok "own heavy reading, 248 mutants at 4 parts ~4,148 s: under the hard limit, no waiver" 'grep -q "\-> 4 parts" $out && ! grep -q waived $out'
print 400 > $S/to_run; tsp --max-mutants 1000
ok "own heavy reading over the hard limit (400 x 216 at 4 parts ~6,500 s): NMAX waived only as far as needed, 6 parts ~4,418 s (tm-shard-actions-120: 5 parts ~5,120 s is over the 5,100-s part line)" 'grep -q "\-> 6 parts (~4418 s each" $out && grep -q "reserve and NMAX waived to 6 parts: ~5100 s per part at most" $out && [ $(grep -c "^dispatch" $S/drec) = 6 ]'
rm -f $S/spmv; print 253 > $S/to_run; rm -rf $S/gha-tests/*(N); gt sel1 dispatched 6 300 1800; gt sel2 dispatched 1 300 1800
tsp --max-mutants 1000; ok "pc-3's case: 6+1 runners busy, 253 first-sweep mutants ~6,160 s: cap - busy = 1 is no gain, one part over TM_SHARD_ACTIONS_HARD: not sent (L168; en-s6b ~6,140 s was cancelled)" '[ ! -e $S/drec ] && grep -q "cancels a job at 120 min: not sent (VM path)" $out'
print '216 item' > $S/spmv; tsp --max-mutants 1000; ok "ap-4a's case: 253 x 216 in one part (~14,800 s) with no room: not sent, exit 3 (VM path)" '[ ! -e $S/drec ] && grep -q "cancels a job at 120 min: not sent (VM path)" $out'; rm -f $S/spmv
rm -rf $S/gha-tests/*(N); gt sel1 dispatched 5 300 1800; print 500 > $S/to_run
tsp --max-mutants 1000; ok "busy 5 + 1 arrival: room 2, 500 first-sweep mutants ~6,100 s: reserve waived to cap - busy = 3 parts" 'grep -q "\-> 3 parts" $out && grep -q "waived to 3 parts" $out'
print 2000 > $S/to_run; rm -rf $S/gha-tests/*(N); tsp --max-mutants 1000; ok "the hard NMAX caps a waiver at cap 8 (2000 mutants): 8 parts ~5,800 s are over the 5,100-s part line, not sent on actions (tm-shard-actions-120)" 'grep -q "2000 mutants need ~5800 s per part in 8 parts" $out && grep -q "on actions, which cancels a job at 120 min: not sent" $out && ! grep -qs "\"pool\": \"actions\"" $J/*/job.json(N) /dev/null'
: > $S/TM-SPM-OFF; print 69 > $S/to_run; tsp --max-mutants 1000; ok "veto TM-SPM-OFF: no first-sweep floor (the constant, one part)" 'grep -q "fit one part on actions" $out'; rm -f $S/TM-SPM-OFF
rm -rf $S/gha-tests/*(N); export TM_SHARD_ACTIONS_FIRST_SPM=26 TM_SHARD_ACTIONS_HARD=999999 TM_SHARD_ACTIONS_CANCEL=999999; print 338 > $S/to_run
print "== state and merge"
rm -rf $J/*(N) $S/drec; mkdir -p $S/dest
CLOUD_DISPATCH_POOL=claude zsh $TS dispatch --worktree $S/wt it $SHA -- --max-mutants 1000 --json $S/dest/it.json > $out 2>&1
ok "  (claude pool, 338: 2 parts)" '[ "$(jv $P/job.json shards)" = "[\"it.s1of2-$S8\", \"it.s2of2-$S8\"]" ]'
pst(){ python3 -I -c 'import json,sys; p=sys.argv[1]; d=json.load(open(p)); [d.__setitem__(k, int(v) if v.isdigit() else v) for k,v in (a.split("=",1) for a in sys.argv[2:])]; json.dump(d,open(p,"w"))' "$@"; }
ok "state: no part pulled: wait" '[ "$(zsh $TS state $P/job.json)" = "wait 0 of 2 parts pulled" ]'
pst $J/it.s1of2-$S8/job.json status=pulled tm_s=900; print '{"part": 1}' > $P/part-1.json
ok "  one pulled: wait 1 of 2" '[ "$(zsh $TS state $P/job.json)" = "wait 1 of 2 parts pulled" ]'
pst $J/it.s2of2-$S8/job.json status=part-failed
ok "  a part failed: fail, naming it" '[[ "$(zsh $TS state $P/job.json)" == "fail part it.s2of2-$S8 part-failed: no result" ]]'
pst $J/it.s2of2-$S8/job.json status=dispatched; CLOUD_NOW=$(( $(jv $P/job.json deadline) + 120 )) zsh $TS state $P/job.json > $out
ok "  the parent's deadline passed: fail" 'grep -q "^fail no merged result by the deadline" $out'
pst $J/it.s2of2-$S8/job.json status=pulled tm_s=1200 input_commit=abc; print '{"part": 2}' > $P/part-2.json
ok "  all pulled: merge" '[ "$(zsh $TS state $P/job.json)" = merge ]'
zsh $TS merge $P/job.json > $out 2>&1; RC=$?
ok "merge: the tool's --merge of part-1..N into the dest; tm_rc = its exit, tm_s = the slowest part's; prompt.txt kept for the sample" '[ $RC = 0 ] && [ "$(cat $S/dest/it.json)" = "$(cat $P/part-1.json $P/part-2.json)" ] && [ "$(jv $P/job.json tm_rc)" = 1 ] && [ "$(jv $P/job.json tm_s)" = 1200 ] && [ -f $P/prompt.txt ] && grep -q "OK 2 parts" $out'
rm -f $S/dest/it.json; print 2 > $S/merge_rc; zsh $TS merge $P/job.json > $out 2>&1; RC=$?
ok "  the tool refuses (exit 2): exit 2, said, nothing at the dest" '[ $RC = 2 ] && grep -q "REFUSED (exit 2): parts disagree on inputs" $out && [ ! -e $S/dest/it.json ]'
rm -f $S/merge_rc $P/part-2.json; zsh $TS merge $P/job.json > $out 2>&1
ok "  a part record missing: exit 2" '[ $? = 2 ] && grep -q "part record .* missing" $out'

print "== cloud-pull.sh$SFX: parents and parts"
CP=$M/cloud-pull.sh$SFX; pull(){ zsh $CP "$@" > $out 2>&1; }
rm -rf $J/*(N) $S/msgs $S/vs $S/trial.md $S/dest/*(N)
CLOUD_WAITER=$$ CLOUD_DISPATCH_POOL=claude zsh $TS dispatch --worktree $S/wt it $SHA -- --max-mutants 1000 --json $S/dest/it.json > /dev/null 2>&1
for k in 1 2; do pst $J/it.s${k}of2-$S8/job.json status=pulled tm_s=$((k * 500)); print "{\"part\": $k}" > $P/part-$k.json; done
pull
ok "all parts pulled: the parent is merged into its dest, status pulled, a trial-log row, the merged record is sampled" '[ "$(cat $S/dest/it.json)" = "$(cat $P/part-1.json $P/part-2.json)" ] && [ "$(jv $P/job.json status)" = pulled ] && grep -q "^| it-$S8 | .* | match (merged parts) |" $S/trial.md && grep -q "it-$S8: verdict check: sample" $out && grep -q "vs $P/job.json" $S/vs && cmp -s $P/cloud-verdicts.json $S/dest/it.json'
ok "  the parent is never handled as a job of its own (no ls-remote of a branch it does not have)" '! grep -q "it-$S8: waiting" $out'
rm -rf $J/*(N) $S/vs $S/trial.md $S/dest/*(N)
CLOUD_WAITER=$$ CLOUD_DISPATCH_POOL=claude zsh $TS dispatch --worktree $S/wt it $SHA -- --max-mutants 1000 --json $S/dest/it.json > /dev/null 2>&1
pst $J/it.s1of2-$S8/job.json status=pulled; pst $J/it.s2of2-$S8/job.json deadline=1
pull
ok "a part past its deadline: part-failed (never a VM run of a part), then its parent falls back to its live waiter" '[ "$(jv $J/it.s2of2-$S8/job.json status)" = part-failed ] && [ "$(jv $P/job.json status)" = fallback-caller ] && grep -q "part of it-$S8, which falls back" $out && grep -q "it-$S8: .*its waiter (pid $$) runs it on the VM" $out && [ ! -e $S/vs ]'
ok "  trial rows: the part's \"shard part: no result\" and the parent's VM fallback" 'grep -q "| shard part: no result |" $S/trial.md && grep -q "^| it-$S8 | .* | VM fallback (waiter) |" $S/trial.md'
rm -rf $J/*(N) $S/dest/*(N)
CLOUD_DISPATCH_POOL=claude zsh $TS dispatch --worktree $S/wt it $SHA -- --max-mutants 1000 --json $S/dest/it.json > /dev/null 2>&1
for k in 1 2; do pst $J/it.s${k}of2-$S8/job.json status=pulled; print "{}" > $P/part-$k.json; done; print 2 > $S/merge_rc
pull; rm -f $S/merge_rc
ok "a refused merge: the parent's fallback (no waiter, its worktree unknown: fallback-needed), nothing at the dest" '[ "$(jv $P/job.json status)" = fallback-needed ] && grep -q "merge of the parts refused" $out && [ ! -e $S/dest/it.json ]'

print "== cloud-overflow.sh$SFX: the flag picks tm-shard.sh; parents are not pool jobs"
CO=$M/cloud-overflow.sh$SFX; rm -rf $J/*(N); : > $S/ACTIONS_POOL
for i in 1 2 3 4 5 6 7; do mkdir -p $J/p$i; print '{"job":"p'$i'","status":"dispatched","pool":"actions","shards":["x"]}' > $J/p$i/job.json; done
mkdir -p $J/a1; print '{"job":"a1","status":"dispatched","pool":"actions"}' > $J/a1/job.json
zsh $CO pool > $out 2>&1; ok "7 dispatched parents + 1 part on actions: 1 in flight, room" '[ $? = 0 ] && grep -q "1 in flight" $out'
ok "the dispatcher is tm-shard.sh dispatch while TM_SHARD exists (and no CLOUD_DISPATCH override), else cloud-dispatch.sh" 'grep -q "dsp=\"zsh \$M/tm-shard.sh dispatch\"" $CO && grep -q "\${=dsp} --worktree" $CO'
print "== eff-tm-partial (2026-10-31): Actions parts get --budget (flag TM_PART_DEADLINE); a partial part is no result"
export TM_PART_DEADLINE_FLAG=$S/TM_PART_DEADLINE; : > $S/TM_SHARD; rm -f $S/TM_PART_DEADLINE $S/merge_rc; print 338 > $S/to_run
mkdir -p $S/vm/tools; print -r -- 'parser.add_argument("--budget", type=float)  # --shard' > $S/vm/tools/trust_mutants.py
git -C $S/vm add -A; git -C $S/vm -c user.name=t -c user.email=t@example.com commit -q -m budget; SHB=$(git -C $S/vm rev-parse HEAD); B8=${SHB[1,8]}
pd(){ rm -rf $J/*(N) $S/drec; CLOUD_DISPATCH_POOL=${POOL:-actions} zsh $TS dispatch --worktree $S/wt it ${2:-$SHB} -- --max-mutants 1000 $=1 > $out 2>&1; PRC=$?; }
budgeted(){ grep -c -- "^dispatch --worktree $S/wt it.s[0-9]of[0-9] [0-9a-f]* -- --max-mutants 1000 ${1}--budget ${2:-6300} --shard [0-9]/[0-9] --json " $S/drec; }
pd; ok "P1 flag off: no part gets --budget (as before)" '[ $PRC = 0 ] && [ $(grep -c ^dispatch $S/drec) = 3 ] && ! grep -q -- --budget $S/drec'
: > $S/TM_PART_DEADLINE
pd; ok "P2 flag on, Actions, a commit whose tool has --budget: each of the 3 parts gets --budget 6300 before --shard; the line says so" '[ $PRC = 0 ] && [ $(budgeted) = 3 ] && grep -q "3 parts .*each part --budget 6300 s" $out'
TM_PART_BUDGET=5000 pd; ok "P3 TM_PART_BUDGET sets the seconds" '[ $(budgeted "" 5000) = 3 ]'
pd "--budget 99"; ok "P4 the caller's own --budget: tm-shard's --budget 6300 beside it (tm-shard-actions-120; cloud-tm-job.sh takes the earliest)" '[ $PRC = 0 ] && [ $(budgeted "--budget 99 ") = 3 ]'
pd "--deadline 99"; ok "P5 the caller's own --deadline: tm-shard's --budget 6300 beside it (tm-shard-actions-120; cloud-tm-job.sh takes the earliest)" '[ $PRC = 0 ] && [ $(budgeted "--deadline 99 ") = 3 ]'
pd "" $SHA; ok "P6 a commit whose trust_mutants.py has no --budget: none (the tool would refuse it)" '[ $(grep -c ^dispatch $S/drec) = 3 ] && ! grep -q -- --budget $S/drec'
POOL=claude pd; ok "P7 not Actions (claude): none" '[ $(grep -c ^dispatch $S/drec) -ge 2 ] && ! grep -q -- --budget $S/drec'
rm -f $S/TM_PART_DEADLINE
rm -rf $J/*(N); P=$J/it-$S8; CLOUD_DISPATCH_POOL=claude zsh $TS dispatch --worktree $S/wt it $SHA -- --max-mutants 1000 --json $S/dest/it.json > /dev/null 2>&1
for k in 1 2; do pst $J/it.s${k}of2-$S8/job.json status=pulled; print "{\"part\": $k}" > $P/part-$k.json; done
print '{"part": 2, "partial": {"deadline": 1, "unjudged": ["M002", "M004"]}}' > $P/part-2.json
ok "P8 state: a pulled part whose record is partial is no result: fail, naming it and its unjudged count" '[ "$(zsh $TS state $P/job.json)" = "fail part it.s2of2-$S8 partial (2 unjudged): no result" ]'
pst $J/it.s2of2-$S8/job.json status=pulled-local
ok "P9   pulled-local and partial: fail too" '[ "$(zsh $TS state $P/job.json)" = "fail part it.s2of2-$S8 partial (2 unjudged): no result" ]'
print '{"part": 2, "partial": "x"}' > $P/part-2.json
ok "P10  a partial key of another type: fail all the same (0 unjudged read is not a whole record)" '[[ "$(zsh $TS state $P/job.json)" == "fail part it.s2of2-$S8 partial"* ]]'
print '{"part": 2}' > $P/part-2.json
ok "P11  the part whole again: merge" '[ "$(zsh $TS state $P/job.json)" = merge ]'

print "== shard-room.py: a sharded gate leg counts only its shards with no result (2026-11-02 shard-room-busy-stale)"
# TMS_SHARD_ROOM=<copy> tests an uninstalled shard-room.py
SR=${TMS_SHARD_ROOM:-$M/shard-room.py}; A=$S/gha-arm
# ar <job> <status> <shards, - = none> <deadline in s from now> <extra json> <returned k...>
ar(){ local d=$A/$1 st=$2 n=$3 dl=$4 x=$5 k; shift 5; mkdir -p $d; for k in "$@"; do mkdir -p $d/s$k; done
  python3 -I -c 'import json,sys,time; d={"status":sys.argv[2],"deadline":int(time.time())+int(sys.argv[4]),"created":0,**json.loads(sys.argv[5])}; d.update({"shards":int(sys.argv[3])} if sys.argv[3]!="-" else {}); json.dump(d,open(sys.argv[1],"w"))' $d/run.json $st $n $dl "${x:-{\}}"; }
rm_(){ GHA_ARM_DIR=$A python3 -I $SR actions 20 $S/no-jobs $S/no-tests > $out 2>&1; cat $out; }
ar none dispatched 4 3600 ''; ok "SR1  no shard back: 4 busy, room 16" '[ "$(rm_)" = "16 4 0 0" ]'
rm -rf $A; ar last dispatched 6 3600 '' 1 2 3 4 5; ok "SR2  a parent waiting for its last shard (5 of 6 back): 1 busy" '[ "$(rm_)" = "19 1 0 0" ]'
rm -rf $A; ar wait dispatched 4 3600 '{"mode":"shadow","mac_record":"/m/c.mac.json"}' 1 2 3 4; ok "SR3  all back, the parent in its Mac wait (still dispatched, before its deadline): 0 busy" '[ "$(rm_)" = "20 0 0 0" ]'
rm -rf $A; ar arm dispatched - 3600 ''; ok "SR4  an unsharded leg (gha-arm-gate.sh, no shards key): 1 busy" '[ "$(rm_)" = "19 1 0 0" ]'
rm -rf $A; ar lean dispatched 1 3600 '{"phase":"lean"}'; ok "SR5  the Lean build job of a --lean-once run (shards 1): 1 busy" '[ "$(rm_)" = "19 1 0 0" ]'
ar a dispatched 3 3600 '' 2; ar b dispatched 2 -60 ''; ar c done 5 3600 ''; ok "SR6  sums over runs (2 of a + the build job); past-deadline and done runs stay 0" '[ "$(rm_)" = "17 3 0 0" ]'
rm -rf $A; ar new dispatched 2 3600 '{"created":'$(( $(date +%s) - 60 ))'}' 1 2; ok "SR7  all back still counts as an arrival of the last hour (reserve unchanged)" '[ "$(rm_)" = "19 0 1 1" ]'

print "== tm-spm.py: own readings last 96 h, a cancelled whole job is a lower bound (2026-11-02 dri-improve, L168)"
SP=$M/tm-spm.py; [ -e $M/tm-spm.py$SFX ] && SP=$M/tm-spm.py$SFX
J2=$S/spmj; mkdir -p $J2; X2=$S/spmx; git init -q -b main $X2; NOW=$(date +%s); L2=$J2/cloud-jobs.log; : > $L2
mj(){ mkdir -p $J2/$1; print -r -- "{\"job\":\"$1\",\"item\":\"$2\",\"pool\":\"actions\",\"status\":\"$3\",\"tm_s\":\"$4\",\"generated\":$(( NOW - $5 ))${6:+,$6}}" > $J2/$1/job.json; }
ts(){ date -u -d @$(( NOW - $1 )) +%FT%H:%M:%SZ; }
res(){ local d=$X2/cloud-results/$1; mkdir -p $d; print -r -- "run_result=$2" > $d/gha.txt; printf 'step\tstart\tseconds\nbranch_lake_build\t0\t905\n' > $d/timings.tsv
  git -C $X2 add -A; git -C $X2 -c user.name=t -c user.email=t@example.com commit -q -m $1; git -C $X2 update-ref refs/cloud/$1 HEAD; }
spm(){ CLOUD_NOW=$NOW TM_SPM_EXPORT=$X2 TM_SHARD_CONTROL=600 python3 -I $SP $J2 $1; }
mj a-aaaaaaaa a pulled 6199 $(( 50 * 3600 )); print -r -- "$(ts 100) cloud-pull: cloud-tm-verify a-aaaaaaaa: OK 34 mutants {'KILLED': 34}" >> $L2
ok "an own reading 50 h old still counts (pc-1's 659 aged out at 24 h)" '[ "$(spm a)" = "659 item" ]'
mj b-bbbbbbbb b pulled 6199 $(( 120 * 3600 )); print -r -- "$(ts 100) cloud-pull: cloud-tm-verify b-bbbbbbbb: OK 34 mutants {'KILLED': 34}" >> $L2
ok "an own reading 120 h old does not, and another item's 50-h reading is no pool reading (48 h)" '[ -z "$(spm b)" ]'
mj c-cccccccc c fallback-caller "" 3600; print -r -- "$(ts 3610) tm-shard: c: unsharded (37 mutants to run fit one part on actions (~1840 s))" >> $L2; res c-cccccccc cancelled
ok "a cancelled whole job: (7200 - 905 setup - 600) * 4 / 37" '[ "$(spm c)" = "616 item" ]'
mj d-dddddddd d fallback-caller "" 3600; print -r -- "$(ts 3610) tm-shard: d: unsharded (37 mutants to run fit one part on actions (~1840 s))" >> $L2; res d-dddddddd success
ok "a whole job refused for another reason (run_result=success): no bound" '[ -z "$(spm d)" ]'
mj e-eeeeeeee e fallback-caller "" 3600; res e-eeeeeeee cancelled
ok "a cancelled whole job with no unsharded line near it: no bound" '[ -z "$(spm e)" ]'
mj c-x-ffffffff c-x fallback-caller "" 3600; print -r -- "$(ts 3610) tm-shard: c-x: unsharded (3 mutants to run fit one part on actions (~1 s))" >> $L2; res c-x-ffffffff cancelled
ok "item c-x's job is not read as c's (the bound stays c's own)" '[ "$(spm c)" = "616 item" ]'
mj g-11111111 g dispatched "" 3600 '"shards":["g.s1of2-11111111"]'; res g-11111111 cancelled
ok "a parent (shards) is no job of its own" '[ -z "$(spm g)" ]'
mj h.s1of2-22222222 h.s1of2 part-failed "" 3600 '"parent":"h-22222222"'; print -r -- "$(ts 3610) tm-shard: h-22222222: 40 mutants to run on actions -> 2 parts (~1 s each)" >> $L2; res h.s1of2-22222222 cancelled
ok "a cancelled part still reads as before, now within 96 h too" '[ "$(spm h)" = "1139 item" -o "$(spm h)" = "1000 item" ]'

print "== a --test path under lean/, and a no-count names its reason (2026-11-03 tm-test-path-lean-rel)"
# the VE tool's --plan as trust_mutants behaves on the 16 logged no-counts (reviews/tm-plan-no-count-20261103.md): a --test
# that is no file is refused (en-s6b: $wt/VE/X.lean, made absolute by cloud-overflow.sh); $S/plan_mode picks the others
cat > $S/bin/tool3 <<X
#!/bin/bash
[ "\$1" = --plan ] || exit 9
echo "planning \$*" >> $S/plan-args
case "\$(cat $S/plan_mode 2>/dev/null)" in
  decl) echo "VE/A.lean: declarations.txt was not compiled from this source; rerun tools/lean_statements.py" >&2
    echo "lean/declarations.txt was not compiled from lean/VE/A.lean; rerun tools/lean_statements.py" >&2; exit 2;;
  argp) printf 'usage: trust_mutants.py [-h] [--base BASE]\n                        [--resume PREV.json]\ntrust_mutants.py: error: unrecognized arguments: lean/VE/B.lean\n' >&2; exit 2;;
  slow) exit 124;;
  crash) echo "Traceback (most recent call last):" >&2; exit 1;;
esac
while [ \$# -gt 0 ]; do t=""; case \$1 in --test) t=\$2; shift;; --test=*) t=\${1#*=};; esac; shift
  [ -z "\$t" ] && continue; case \$t in /*) p=\$t;; lean/*) p=$S/wt/\$t;; *) p=$S/wt/lean/\$t;; esac
  case \$p in *.lean) [ -f "\$p" ] && continue;; esac; echo "--test: not a Lean file: [PosixPath('\$p')]" >&2; exit 2; done
echo "{\"base\": \"b\", \"definitions\": 3, \"mutants\": 400, \"to_run\": \$(cat $S/to_run), \"not_run\": 0}"
X
chmod +x $S/bin/tool3; mkdir -p $S/wt/lean/VE $S/wt/tests; : > $S/wt/lean/VE/Y.lean; : > $S/wt/tests/test_a.py
tl(){ rm -f $S/plan-args; TM_SHARD_TOOL=$S/bin/tool3 tsp "$@"; cp $J/cloud-jobs.log $S/tlog 2>/dev/null || : > $S/tlog; }
rm -f $S/spmv $S/plan_mode; rm -rf $S/gha-tests/*(N); : > $S/TM_SHARD; print 338 > $S/to_run
tl --max-mutants 1000 --test $S/wt/VE/Y.lean
ok "en-s6b's case: --test \$wt/VE/Y.lean (no such file; lean/VE/Y.lean is): read as \$wt/lean/VE/Y.lean, --plan counts, sharded" 'grep -q "it: --test $S/wt/VE/Y.lean read as $S/wt/lean/VE/Y.lean (trust_mutants'"'"' lean/ form)" $out && grep -q "338 mutants to run on actions -> 3 parts" $out && grep -q -x "planning --plan --max-mutants 1000 --test $S/wt/lean/VE/Y.lean" $S/plan-args'
ok "  every part carries the lean/ form" '[ $(grep -c -- "--test $S/wt/lean/VE/Y.lean .*--shard" $S/drec) = 3 ] && ! grep -q -- "--test $S/wt/VE/Y.lean" $S/drec'
tl --max-mutants 1000 --test VE/Y.lean; ok "  a relative VE/Y.lean: the same" 'grep -q "read as $S/wt/lean/VE/Y.lean" $out && grep -q "\-> 3 parts" $out'
tl --max-mutants 1000 --test=$S/wt/VE/Y.lean; ok "  --test=PATH: the same" '[ $(grep -c -- "--test=$S/wt/lean/VE/Y.lean .*--shard" $S/drec) = 3 ]'
tl --max-mutants 1000 --test lean/VE/Y.lean; ok "  already lean/VE/Y.lean: kept as given, sharded" '! grep -q "read as" $out && grep -q "\-> 3 parts" $out && grep -q -x "planning --plan --max-mutants 1000 --test lean/VE/Y.lean" $S/plan-args'
tl --max-mutants 1000 --test $S/wt/tests/test_a.py
ok "qt-a4/jt-3: a --test that is a file but no Lean file: kept, a no-count that names it, unsharded (one dispatch, the waiter's VM path after it)" '! grep -q "read as" $out && grep -q "unsharded (trust_mutants --plan gave no count (exit 2: trust_mutants refuses its inputs, so the whole run will too: --test: not a Lean file: \[PosixPath(.$S/wt/tests/test_a.py.)\]))" $out && [ $(grep -c "^dispatch" $S/drec) = 1 ] && ! grep -q -- --shard $S/drec'
tl --max-mutants 1000 --test $S/wt/VE/Nope.lean; ok "no file in either form: kept, a no-count that names it" '! grep -q "read as" $out && grep -q "gave no count (exit 2: .*not a Lean file: \[PosixPath(.$S/wt/VE/Nope.lean.)\])" $out'
print decl > $S/plan_mode; tl --max-mutants 1000
ok "a stale lean/declarations.txt (11 of 16): the first message and how many more, unsharded" 'grep -q "unsharded (trust_mutants --plan gave no count (exit 2: trust_mutants refuses its inputs, so the whole run will too: VE/A.lean: declarations.txt was not compiled from this source; rerun tools/lean_statements.py (+1 more)))" $out && [ $(grep -c "^dispatch" $S/drec) = 1 ]'
ok "  --plan's stderr is still in cloud-jobs.log" 'grep -q "^lean/declarations.txt was not compiled from lean/VE/A.lean" $S/tlog'
print argp > $S/plan_mode; tl --max-mutants 1000 --test a.lean b.lean
ok "jt-3 01:46Z: an argument it does not take: argparse's error line, not its usage" 'grep -q "exit 2: trust_mutants refuses its inputs, so the whole run will too: trust_mutants.py: error: unrecognized arguments: lean/VE/B.lean)" $out && ! grep -q "gave no count.*usage:" $out'
print slow > $S/plan_mode; tl --max-mutants 1000; ok "a --plan timeout: named, unsharded as before" 'grep -q "unsharded (trust_mutants --plan gave no count (exit 124: timed out after 300 s))" $out && [ $(grep -c "^dispatch" $S/drec) = 1 ]'
print crash > $S/plan_mode; tl --max-mutants 1000; ok "a --plan crash: its exit and message, unsharded" 'grep -q "gave no count (exit 1: Traceback (most recent call last):)" $out && ! grep -q "refuses its inputs" $out'
print decl > $S/plan_mode; rm -rf $J/*(N) $S/drec
(cd $S/wt && CLOUD_DISPATCH_POOL=codex TM_SHARD_TOOL=$S/bin/tool3 zsh $TS dispatch --worktree $S/wt it $SHA -- --max-mutants 1000) > $out 2>&1; RC=$?
ok "on codex a no-count names its reason and takes the VM path (exit 3, nothing sent)" '[ $RC = 3 ] && [ ! -e $S/drec ] && grep -q "not sent to codex unsharded (trust_mutants --plan gave no count (exit 2: .*declarations.txt.*(+1 more))): VM path" $out'
rm -f $S/plan_mode
print "== fit room (actions-select-fit-room; flag TM_FIT_ROOM; real cloud-overflow.sh offer, stub picker and pace)"
# Actions cap 8 on this conf; busy N = N Actions parts in flight; a sweep over the cancel line at that room is refused
OVF=${TMO_OVERFLOW:-$M/cloud-overflow.sh}; FF=$S/TM_FIT_ROOM; print -r -- 'import sys; sys.exit("hold: main test")' > $S/bin/pace-held.py; : > $S/bin/pace-ok.py
print -r -- 'CLOUD_MAX_INFLIGHT=4
ACTIONS_MAX_INFLIGHT=8
CCLOUD_MAX_INFLIGHT=30
CODEX_MAX_INFLIGHT=6
CCLOUD_DEADLINE_MIN=90' > $S/conf
mkpool(){ : > $S/CCP; : > $S/CXP; : > $S/TM_SHARD; print -r -- "10:00Z codexWeek=${1:-40}" > $S/uw.log; }
busy(){ rm -rf $J/*(N); local i; for i in {1..$1}; do mkdir -p $J/b$i; print -r -- '{"pool":"actions","status":"dispatched"}' > $J/b$i/job.json; done; }  # $1 Actions parts in flight
fr(){ rm -f $S/drec $S/slept; (cd $S/wt && TM_FIT_ROOM_FLAG=$FF TM_SPM_OFF_FLAG=/nonexistent TM_SPM=$S/bin/spm.py TM_SHARD_ACTIONS_HARD=5400 TM_SHARD_ACTIONS_CANCEL=6600 TM_SHARD_ACTIONS_FIRST_SPM=80 env -u TM_SHARD_CONTROL \
    CCLOUD_POOL_FLAG=$S/CCP CODEX_POOL_FLAG=$S/CXP USAGE_WATCH_LOG=$S/uw.log CCLOUD_PACE=${FPACE:-$S/bin/pace-ok.py} CCLOUD_PICK=${FPICK:-true} TM_FIT_OVERFLOW="zsh $OVF" TM_QUEUE_SLEEP=${FSLEEP:-"zsh $S/bin/qsleep"} \
    CODEX_OFF_FLAG=/nonexistent CLOUD_DISPATCH_POOL=actions TM_SHARD_TOOL=$S/bin/tool zsh $TS dispatch --worktree $S/wt it $SHA -- --max-mutants 1000) > $out 2>&1; RC=$?; }
print -r -- 'print("250 item")' > $S/bin/spm.py
print -r -- 'print -r -- "slept $1" >> '$S'/slept; [ -f '$S'/free-on-wake ] && rm -rf '$J'/b*(N); exit 0' > $S/bin/qsleep
rm -f $S/plan_mode; rm -rf $S/gha-tests/*(N); print 168 > $S/to_run; mkpool; : > $FF
busy 8; fr
ok "ap-3db's case (168 mutants at 250, Actions full): refused for actions, claude-cloud takes the parts" '[ $RC = 0 ] && grep -q "TM_FIT_ROOM: actions refused it .*; claude-cloud takes it" $out && python3 -I -c "import json,sys; d=json.load(open(sys.argv[1])); sys.exit(0 if d[\"pool\"]==\"claude-cloud\" and d[\"status\"]==\"dispatched\" and len(d[\"shards\"])==6 else 1)" $J/it-$S8/job.json'
ok "  its parts go to claude-cloud with no Actions budget; the sizing is Actions' SPM, not the constant 12" 'grep -q "to run on claude-cloud -> 6 parts (~2850 s each.*sized at 250 slot-s" $out && [ $(grep -c "^dispatch" $S/drec) = 6 ] && ! grep -q -- "--budget" $S/drec'
ok "  no \"not sent (VM path)\" line: the guard counts real VM paths only" '! grep -q "not sent (VM path)" $out'
print 100 > $S/to_run; FPICK=false; busy 8; fr; unset FPICK; print 168 > $S/to_run
ok "  a sweep Codex can run: parts on codex, the claude-cloud refusal on the same line" '[ $RC = 0 ] && grep -q "claude-cloud: claude-cloud off (the picker gives no account[^;]*; codex takes it" $out && [ "$(jv $J/it-$S8/job.json pool)" = codex ]'
FPICK=false; mkpool 90; print 168 > $S/to_run; rm -rf $J/*(N); mkdir -p $J/b1; print -r -- '{"pool":"actions","status":"dispatched"}' > $J/b1/job.json
print -r -- 'print("1000 item")' > $S/bin/spm.py; print 1000 > $S/to_run; TM_QUEUE_MIN=20 fr; unset FPICK
ok "all pools refuse and no room would fit it: VM path, exit 3, nothing sent, one line naming every reason" '[ $RC = 3 ] && [ ! -e $S/drec ] && [ ! -e $S/slept ] && [ $(grep -c "not sent (VM path)" $out) = 1 ] && grep -q "not sent (VM path); TM_FIT_ROOM: claude-cloud: claude-cloud off (the picker[^;]*; codex: codex off (Codex week 90% >= 47%); queue: no, no room fits it" $out'
print -r -- 'print("250 item")' > $S/bin/spm.py; print 168 > $S/to_run
FPACE=$S/bin/pace-held.py; mkpool 90; busy 8; : > $S/free-on-wake; fr; unset FPACE
ok "queue then retry: pace holds claude-cloud, Codex at its cap, Actions room forecast: it sleeps once, then Actions takes it" '[ $RC = 0 ] && grep -q "claude-cloud held (hold: main test)" $out && grep -q "Actions room forecast in ~[0-9]* min (.*ESTIMATE): queued, one retry at" $out && [ $(wc -l < $S/slept) = 1 ] && grep -q "the retry after ~[0-9]* min: actions has room now" $out && [ "$(jv $J/it-$S8/job.json pool)" = actions ]'
ok "  the retry sent the parts on Actions with their budget rule unchanged (no flag here: none)" '(( $(grep -c "^dispatch" $S/drec) >= 2 )) && ! grep -q "not sent (VM path)" $out'
FPACE=$S/bin/pace-held.py; mkpool 90; busy 8; rm -f $S/free-on-wake; fr; unset FPACE
ok "queue, and the retry finds no room: one retry only, then the VM path with the reasons" '[ $RC = 3 ] && [ $(wc -l < $S/slept) = 1 ] && [ $(grep -c "not sent (VM path)" $out) = 1 ] && grep -q "not sent (VM path); TM_FIT_ROOM: the retry after ~[0-9]* min found no room; claude-cloud: claude-cloud held" $out'
FPACE=$S/bin/pace-held.py; mkpool 90; busy 8; TM_QUEUE_MIN=1 fr; unset FPACE
ok "the forecast past TM_QUEUE_MIN: no queue, the VM path says why" '[ $RC = 3 ] && [ ! -e $S/slept ] && grep -q "queue: no, Actions room not forecast within 1 min" $out'
rm -f $FF; busy 8; fr
ok "flag off: exactly today's line and exit, no offer" '[ $RC = 3 ] && [ ! -e $S/drec ] && grep -q "on actions, which cancels a job at 120 min: not sent (VM path)$" $out && ! grep -q TM_FIT_ROOM $out'
: > $FF; busy 8; TM_FIT_SRC=first fr
ok "the actions-first ask neither offers nor queues, and does not count as a VM path" '[ $RC = 3 ] && [ ! -e $S/drec ] && [ ! -e $S/slept ] && grep -q "not sent on actions (actions first has no other pool" $out && ! grep -q "not sent (VM path)" $out'
busy 8; print -r -- 'print("1000 item")' > $S/bin/spm.py; print 145 > $S/to_run; mkpool; fr
ok "qt-a4's case (145 at 1000): over claude-cloud's 4,050-s line at NMAX 6, its reason names the line" 'grep -q "claude-cloud: ~[0-9]* s per part in 6 parts at 1000 slot-s per mutant > its 4050 s line" $out'
print -r -- 'print("250 item")' > $S/bin/spm.py; print 168 > $S/to_run; mkpool; print -r -- 'CLOUD_MAX_INFLIGHT=4
ACTIONS_MAX_INFLIGHT=8
CCLOUD_MAX_INFLIGHT=3
CODEX_MAX_INFLIGHT=6
CCLOUD_DEADLINE_MIN=90' > $S/conf; busy 8; fr
ok "claude-cloud's cap stands: 3 free of cap 3 gives at most 3 parts (~4,600 s > its line): refused, not squeezed past the cap" '! grep -q "claude-cloud takes it" $out && grep -q "claude-cloud: ~[0-9]* s per part in 3 parts" $out'
print -r -- 'CLOUD_MAX_INFLIGHT=4
ACTIONS_MAX_INFLIGHT=8' > $S/conf; rm -f $FF $S/free-on-wake; rm -rf $J/*(N)
print "== ccloud heavy sizing (ccloud-heavy-sizing: cloud-overflow.sh sends a sweep straight to claude-cloud; Actions' reading sizes it)"
print -r -- 'CLOUD_MAX_INFLIGHT=4
ACTIONS_MAX_INFLIGHT=8
CCLOUD_MAX_INFLIGHT=8
CCLOUD_DEADLINE_MIN=90' > $S/conf; rm -rf $S/gha-tests/*(N); : > $S/TM_SHARD; SO=$S/TM-SPM-OFF; rm -f $SO
ccs(){ rm -rf $J/*(N) $S/drec; local i; for ((i = 1; i <= ${KARR:-0}; i++)); do mkdir -p $J/a$i; print -r -- '{"pool":"claude-cloud","status":"pulled","generated":'$(date +%s)'}' > $J/a$i/job.json; done
  print -r -- "print(\"$1\")" > $S/bin/spm.py; print $2 > $S/to_run
  (cd $S/wt && TM_SPM_OFF_FLAG=$SO TM_SPM=$S/bin/spm.py TM_SHARD_ACTIONS_FIRST_SPM=80 env -u TM_SHARD_CONTROL CLOUD_DISPATCH_POOL=claude-cloud TM_SHARD_TOOL=$S/bin/tool \
    zsh $TS dispatch --worktree $S/wt it $SHA -- --max-mutants 1000) > $out 2>&1; RC=$?; }
pe(){ grep -o 'claude-cloud -> [0-9]* parts (~[0-9]* s each' $out | grep -o '[0-9]* s each' | cut -d' ' -f1; }
ccs "259 item" 120
ok "a heavy item (259 slot-s/mutant, 120 mutants): 6 parts (NMAX 6 kept), each ~2,395 s, under the 4,050-s line" '[ $RC = 0 ] && grep -q "to run on claude-cloud -> 6 parts (~2395 s each" $out && (( $(pe) <= 4050 )) && [ $(grep -c "^dispatch" $S/drec) = 6 ] && grep -q "measured 259 slot-s per mutant (item), Actions. reading, used for claude-cloud (NMAX 6 kept)" $out'
: > $SO; ccs "259 item" 120; rm -f $SO
ok "  the same sweep under TM-SPM-OFF: the constant 12, one part, as before this change" '[ $RC = 0 ] && grep -q "120 mutants to run fit one part on claude-cloud (~1460 s" $out && [ $(grep -c "^dispatch" $S/drec) = 1 ]'
ccs "259 item" 400
ok "a heavy item past the line at NMAX 6 (400 mutants, ~5,438 s per part): refused, exit 3, nothing sent, one line" '[ $RC = 3 ] && [ ! -e $S/drec ] && [ $(grep -c "not sent (VM path)" $out) = 1 ] && grep -q "400 mutants need ~5438 s per part in 6 parts at 259 slot-s per mutant .* on claude-cloud, over its 4050 s line (cap 8 - busy 0): not sent (VM path)" $out'
KARR=6 ccs "259 item" 230
ok "the reserve (6 arrivals: room 5, ~4,078 s) is waived only to room 6 (~3,625 s)" '[ $RC = 0 ] && grep -q "room 5: cap 8 - busy 0 - reserve 3 for 6 arrivals/h; reserve waived to room 6: its parts must end within ~4050 s" $out && grep -q "claude-cloud -> 6 parts (~3625 s each" $out'
mkdir -p $S/hold; for i in 1 2 3 4; do mkdir -p $S/hold/k$i; print -r -- '{"pool":"claude-cloud","status":"dispatched"}' > $S/hold/k$i/job.json; done
rm -rf $J/*(N) $S/drec; cp -r $S/hold/k* $J/; print -r -- 'print("259 item")' > $S/bin/spm.py; print 230 > $S/to_run
(cd $S/wt && TM_SPM_OFF_FLAG=$SO TM_SPM=$S/bin/spm.py env -u TM_SHARD_CONTROL CLOUD_DISPATCH_POOL=claude-cloud TM_SHARD_TOOL=$S/bin/tool zsh $TS dispatch --worktree $S/wt it $SHA -- --max-mutants 1000) > $out 2>&1; RC=$?
ok "the cap stands: 4 of 8 busy gives 4 parts (~4,337 s > the line): refused, not squeezed past the cap" '[ $RC = 3 ] && [ ! -e $S/drec ] && grep -q "in 4 parts at 259 slot-s .*over its 4050 s line (cap 8 - busy 4)" $out'
ccs "8 item" 338
ok "a light item (8, 338 mutants): its present split, 2 parts ~1,607 s at the constant 12" '[ $RC = 0 ] && grep -q "338 mutants to run on claude-cloud -> 2 parts (~1607 s each" $out && ! grep -q "used for claude-cloud" $out'
ccs "20 item" 338
ok "  an item read at 20 (under Actions' 26, so Actions keeps its constant too): the same 2 parts" '[ $RC = 0 ] && grep -q "claude-cloud -> 2 parts (~1607 s each" $out'
: > $SO; ccs "8 item" 338; rm -f $SO
ok "  and the same split as under TM-SPM-OFF" '[ $RC = 0 ] && grep -q "claude-cloud -> 2 parts (~1607 s each" $out'
ccs "30 pool" 338
ok "a first sweep (no own reading): Actions' first-sweep SPM, max(pool 30, floor 80) = 80: 6 parts ~2,240 s" '[ $RC = 0 ] && grep -q "first sweep: 80 slot-s per mutant (pool reading 30, floor 80), Actions. reading, used for claude-cloud" $out && grep -q "claude-cloud -> 6 parts (~2240 s each" $out'
print -r -- 'CLOUD_MAX_INFLIGHT=4
ACTIONS_MAX_INFLIGHT=8' > $S/conf; rm -rf $J/*(N) $S/hold
print "== codex before the VM (vm-offload-1108: flag TM_CODEX_VMLOAD; claude-cloud refuses for its line; fake 5-min load and pools; real cloud-overflow.sh offer)"
print -r -- 'CLOUD_MAX_INFLIGHT=4
ACTIONS_MAX_INFLIGHT=8
CCLOUD_MAX_INFLIGHT=8
CODEX_MAX_INFLIGHT=6
CCLOUD_DEADLINE_MIN=90' > $S/conf; rm -rf $S/gha-tests/*(N); : > $S/TM_SHARD; CXF=$S/TM_CODEX_VMLOAD; : > $S/pace-ok.py
cxs(){ rm -rf $J/*(N) $S/drec; local i; for ((i = 1; i <= ${KBUSY:-7}; i++)); do mkdir -p $J/k$i; print -r -- '{"pool":"claude-cloud","status":"dispatched"}' > $J/k$i/job.json; done  # claude-cloud: 7 of 8 busy
  print -r -- "print(\"$1\")" > $S/bin/spm.py; print $2 > $S/to_run; : > $S/CCP; : > $S/CXP; [ -n "$CXOFF" ] && rm -f $S/CXP; print -r -- "10:00Z codexWeek=${CXW:-40}" > $S/uw.log
  for ((i = 1; i <= ${CXBUSY:-0}; i++)); do mkdir -p $J/x$i; print -r -- '{"pool":"codex","status":"dispatched"}' > $J/x$i/job.json; done  # Codex parts in flight
  print -r -- "${L1:-99.00} ${L5:-70.50} ${L15:-60.00} 1/1 1" > $S/loadavg
  (cd $S/wt && TM_CODEX_VMLOAD_FLAG=${CXFLAG:-$CXF} TM_LOADAVG=$S/loadavg TM_SPM_OFF_FLAG=/nonexistent TM_SPM=$S/bin/spm.py TM_SHARD_ACTIONS_FIRST_SPM=80 env -u TM_SHARD_CONTROL \
    CCLOUD_POOL_FLAG=$S/CCP CODEX_POOL_FLAG=$S/CXP USAGE_WATCH_LOG=$S/uw.log CCLOUD_PACE=$S/pace-ok.py CCLOUD_PICK=true CODEX_OFF_FLAG=/nonexistent \
    TM_FIT_OVERFLOW="zsh ${TMO_OVERFLOW:-$M/cloud-overflow.sh}" CLOUD_DISPATCH_POOL=claude-cloud TM_SHARD_TOOL=$S/bin/tool \
    zsh $TS dispatch --worktree $S/wt it $SHA -- --max-mutants 1000) > $out 2>&1; RC=$?; }
: > $CXF; cxs "100 item" 150
ok "load 70.5 > 64, Codex has room: claude-cloud refuses (1 free, ~4,850 s > its 4,050-s line), Codex takes the parts, no VM path" '[ $RC = 0 ] && grep -q "on claude-cloud, over its 4050 s line (cap 8 - busy 7); VM 5-min load 70.50 > 64 (TM_CODEX_VMLOAD): codex takes it" $out && ! grep -q "not sent (VM path)" $out && [ "$(jv $J/it-$S8/job.json pool)" = codex ]'
ok "  the parts go out on codex, each within its 3,300-s line, sized at the item reading (100), the claude-cloud cap untouched" '(( $(grep -c "^dispatch" $S/drec) >= 2 )) && grep -q "to run on codex -> [0-9]* parts (~[0-9]* s each.*TM_FIT_ROOM: sized at 100 slot-s per mutant" $out && (( $(grep -o "codex -> [0-9]* parts (~[0-9]* s each" $out | grep -o "~[0-9]*" | tr -d "~") <= 3300 )) && python3 -I -c "import json,glob,sys; sys.exit(0 if all(json.load(open(f))[\"pool\"]==\"codex\" for f in glob.glob(sys.argv[1]+\"/it.s*/job.json\")) else 1)" $J'
L5=64.00 cxs "100 item" 150
ok "load exactly 64 (not over): the VM path as before, the line says Codex was not offered and why" '[ $RC = 3 ] && [ ! -e $S/drec ] && [ $(grep -c "not sent (VM path)" $out) = 1 ] && grep -q "(cap 8 - busy 7): not sent (VM path); codex not offered: VM 5-min load 64.00 <= 64 (TM_CODEX_VMLOAD)" $out'
L1=120.00 L5=40.00 cxs "100 item" 150
ok "  the 5-min load is read, not the 1-min (1-min 120, 5-min 40): not offered" '[ $RC = 3 ] && grep -q "codex not offered: VM 5-min load 40.00 <= 64" $out'
CXW=90 cxs "100 item" 150
ok "Codex at its week cap (90%, before the 16:36Z reset): the VM path, unchanged order, Codex's own refusal named" '[ $RC = 3 ] && [ ! -e $S/drec ] && grep -q "not sent (VM path); VM 5-min load 70.50 > 64 (TM_CODEX_VMLOAD): codex: codex off (Codex week 90% >= 47%)" $out'
CXOFF=1 cxs "100 item" 150
ok "the Codex pool off (no CODEX_CLOUD_POOL): the VM path with that reason" '[ $RC = 3 ] && grep -q "codex: codex off (no CODEX_CLOUD_POOL)" $out'
CXBUSY=6 cxs "100 item" 150
ok "Codex at its cap (6 of 6 in flight): the VM path, the cap kept" '[ $RC = 3 ] && [ ! -e $S/drec ] && grep -q "codex: 6 codex jobs in flight (cap 6)" $out'
cxs "259 item" 400
ok "a sweep too heavy for Codex too (400 at 259): the VM path, Codex's 3,300-s line named, nothing sent" '[ $RC = 3 ] && [ ! -e $S/drec ] && [ $(grep -c "not sent (VM path)" $out) = 1 ] && grep -q "codex: ~[0-9]* s per part in 6 parts at 259 slot-s per mutant > its 3300 s line" $out'
CXFLAG=/nonexistent/flag cxs "100 item" 150
ok "flag off: exactly the line and exit before this change (no codex clause)" '[ $RC = 3 ] && [ ! -e $S/drec ] && grep -q "on claude-cloud, over its 4050 s line (cap 8 - busy 7): not sent (VM path)$" $out && ! grep -q TM_CODEX_VMLOAD $out'
KBUSY=0 cxs "100 item" 150
ok "claude-cloud has room (0 busy): it takes the sweep as before; Codex is not asked" '[ $RC = 0 ] && grep -q "to run on claude-cloud -> [0-9]* parts" $out && ! grep -q TM_CODEX_VMLOAD $out && [ "$(jv $J/it-$S8/job.json pool)" = claude-cloud ]'
print -r -- 'CLOUD_MAX_INFLIGHT=4
ACTIONS_MAX_INFLIGHT=8' > $S/conf; rm -rf $J/*(N); rm -f $CXF
print "tmshard: $pass passed, $fail failed"; [ $fail = 0 ]
