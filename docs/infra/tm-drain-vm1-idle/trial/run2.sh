#!/bin/zsh
# tm-drain-vm1-idle MEASURED trial: the staged tm-nightly.sh (copy in home/) with TM_NIGHTLY_POOLS=remote+idle, isolated:
# its own home/test-skip (a copy of the 20261116T0600Z record to resume, as the live 1607Z run did), its own worktrees
# (~/code/ve-tmidle-trial, -l1), no remote pool (stub exit 4: nothing leaves VM1), default reserve 8, default caps.
# It waits (up to 10 h) for VM1's 5-min load to leave >= 4 whole cores under nproc - 8, then runs --once; again if the
# gate closed before part 1 (no local part ran).
T=/tmp/tmidle/trial; end=$(( $(date +%s) + 36000 )); n=0
while (( $(date +%s) < end )); do
  l=$(cut -d' ' -f2 /proc/loadavg); (( ${l%%.*} < 19 )) || { sleep 60; continue; }
  n=$(( n + 1 )); print -r -- "$(date -u +%FT%TZ) attempt $n at 5-min load $l"
  env -u TM_NIGHTLY_POOLS TM_NIGHTLY_HOME=$T/home TEST_SKIP_DIR=$T/home/test-skip TM_NIGHTLY_REPO=$HOME/code/verifiable-english \
    TM_NIGHTLY_WT=$HOME/code/ve-tmidle-trial TM_NIGHTLY_NO_SIDE=1 TM_NIGHTLY_BACKLOG=$T/backlog.jsonl TM_NIGHTLY_MPJ=$T/none.jsonl \
    TM_TARGETED_ONLY_FLAG=$T/noflag TM_NIGHTLY_PLAN_JSON='{"mutants": 7038}' TM_NIGHTLY_MACPYTEST="python3 -I $T/stub/noremote.py" \
    TM_NIGHTLY_POOLS=remote+idle TM_NIGHTLY_BUILD_TIMEOUT=3600 TM_NIGHTLY_CONC=1 TM_NIGHTLY_POLL=5 TM_NIGHTLY_STAMP=$(date -u +%Y%m%dT%H%MZ) \
    zsh $T/home/tm-nightly.sh --once; print -r -- "tm-nightly.sh --once exit $?"
  [ $(grep -c "vm1-idle trust_mutants exit" $T/home/test-skip/nightly.log) -ge 2 ] && break
  sleep 120; done
grep -h 'vm1-idle' $T/home/test-skip/nightly.log | cut -c1-300
