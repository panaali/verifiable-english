#!/usr/bin/env bash
# sc-admit-cpu: build the throwaway bench package and time each case (docs/rd-9/sc-admit-cpu/cpu.md).
# Usage: run_bench.sh <worktree> <bench-dir> [<case> ...]. Writes nothing in the worktree; prints the machine, the load
# and, per case, `check` once then three runs of each timed mode as `<case> <mode> run<k>: <user CPU> s | <bench line>`.
set -euo pipefail
WT=$1; B=$2; shift 2
CASES=${*:-NSDbig6 wideGuard767 wideGuard3071}
MODES=${MODES:-parse s2 admit}
mkdir -p "$B/docs"
cat > "$B/lakefile.toml" <<EOF
name = "bench"
[[require]]
name = "veReference"
path = "$WT/lean"
[[lean_exe]]
name = "bench"
root = "Bench"
EOF
cp "$WT/lean/lean-toolchain" "$B/"
cp "$WT/docs/rd-9/sc-admit-cpu/admit_bench.lean" "$B/Bench.lean"
python3 -I "$WT/docs/rd-9/sc-admit-cpu/admit_docs.py" "$B/docs" $(printf '%s\n' $CASES | grep '^R' || true)
(cd "$B" && PATH=~/.elan/bin:$PATH lake build bench 2>&1 | tail -1)
echo "commit $(git -C "$WT" rev-parse --short HEAD); lean/ tree $(git -C "$WT" rev-parse --short HEAD:lean)"
echo "machine: $(lscpu | sed -n 's/^Model name: *//p'), $(nproc) vCPU, $(uname -sr)"
for c in $CASES; do
  echo "load: $(cut -d' ' -f1-3 /proc/loadavg)"
  (cd "$B" && ./.lake/build/bin/bench check "docs/$c.json" 2>/dev/null | grep -v '^ve-stage')
  for m in $MODES; do
    for k in 1 2 3; do
      line=$(cd "$B" && /usr/bin/time -f '%U' -o "$B/time.txt" ./.lake/build/bin/bench "$m" "docs/$c.json" 2>/dev/null |
        grep -v '^ve-stage')
      echo "$c $m run$k: $(cat "$B/time.txt") s | $line"
    done
  done
done
echo "load: $(cut -d' ' -f1-3 /proc/loadavg)"
