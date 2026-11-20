#!/bin/zsh
# usage: cone.sh <scratch-lean-dir> <cpu-list>: one timed lake build of the 51 --test targets after the Dispatch edit
cd $1 || exit 2
s=$(date +%s)
PATH=$HOME/.elan/bin:$PATH /usr/bin/time -f 'TIME wall=%e user=%U sys=%S' taskset -c $2 lake build $(cat /tmp/tmbto/targets.txt) 2>&1 | grep -E 'TIME|error|Build completed|^✖' | tail -5
print "WALL $(( $(date +%s) - s )) s on cpus $2"
