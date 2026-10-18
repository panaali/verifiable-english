#!/usr/bin/env bash
# usage: docs/speed/abcache/timed.sh LOG -- COMMAND...
# Runs COMMAND (its output to LOG.out) and appends to LOG: the start and end (UTC), the exit code, the wall seconds,
# and the VM's 1/5/15-minute load every 60 s while it runs (REPORT.md section 2).
log=$1; shift; [ "$1" = -- ] && shift
echo "start $(date -u +%FT%TZ) load $(cut -d' ' -f1-3 /proc/loadavg) cmd $*" >> "$log"
start=$(date +%s)
"$@" >> "$log.out" 2>&1 &
pid=$!
while kill -0 "$pid" 2>/dev/null; do
  echo "load $(date -u +%FT%TZ) $(cut -d' ' -f1-3 /proc/loadavg)" >> "$log"
  sleep 60 & wait $! 2>/dev/null
  kill -0 "$pid" 2>/dev/null || break
done
wait "$pid"; rc=$?
echo "end $(date -u +%FT%TZ) load $(cut -d' ' -f1-3 /proc/loadavg) rc $rc seconds $(( $(date +%s) - start ))" >> "$log"
exit $rc
