#!/bin/zsh
# The independent judge of defs-carried-oos-measure-1119: one fresh `claude -p` session per packet (model
# claude-opus-5-5, no fallback model), each on the account its own pick-claude-account.sh call returns. The session
# starts in an empty temporary directory with no tools (--tools "") and no customisations (--safe-mode), so it sees only
# the packet: the flag list, the source passages and the carrier surfaces. Its reply is saved unedited.
#
# usage: zsh docs/infra/defs-carried-oos-measure-1119/judge.sh <judge dir> <packet name>...
#   reads  <judge dir>/<packet>.prompt.txt
#   writes <judge dir>/<packet>.raw.json   (the CLI's JSON result, unedited)
#          <judge dir>/<packet>.reply.txt  (its `result` text, unedited)
#          <judge dir>/<packet>.meta.json  (account class, models used, CW from delegate-cw.py; no account name or path)
set -u
MA=${MA:-$HOME/code/manage-agents}
CLAUDE=${CLAUDE_BIN:-$HOME/.local/bin/claude}
dir=${1:A}; shift
main_dir=$(zsh $MA/accounts.sh 2>/dev/null | awk '$1 == "main" {print $2; exit}')
for p in "$@"; do
  prompt=$dir/$p.prompt.txt
  [[ -r $prompt ]] || { print -u2 "no packet $prompt"; exit 2; }
  acct=$(PICK_SHORT=1 zsh $MA/pick-claude-account.sh) || { print -u2 "no account for $p"; exit 3; }
  cls=5x; [[ $acct == $main_dir ]] && cls=main
  wd=$(mktemp -d /tmp/defs-oos-judge-XXXXXX)
  t0=$(date +%s)
  ( cd $wd && CLAUDE_CONFIG_DIR=$acct $CLAUDE -p --model claude-opus-5-5 --tools "" --safe-mode \
      --output-format json < $prompt > $dir/$p.raw.json 2> $wd/stderr.txt )
  rc=$?
  t1=$(date +%s)
  sid=$(python3 -I -c 'import json,sys; print(json.load(open(sys.argv[1])).get("session_id",""))' $dir/$p.raw.json 2>/dev/null)
  tr=( $acct/projects/*/$sid.jsonl(N) )
  cw=""; (( ${#tr} )) && cw=$(python3 -I $MA/tools-local/delegate-cw.py $tr[1] | sed 's/, account .*//')
  python3 -I - $dir/$p.raw.json $dir/$p.reply.txt $dir/$p.meta.json "$cls" "$rc" "$((t1 - t0))" "$cw" <<'EOF'
import json, sys
raw, reply, meta, cls, rc, secs, cw = sys.argv[1:8]
try:
    d = json.load(open(raw))
except ValueError:
    d = {}
open(reply, 'w').write(d.get('result') or '')
json.dump({'account_class': cls, 'exit': int(rc), 'wall_seconds': int(secs), 'session_id': d.get('session_id'),
           'models': sorted((d.get('modelUsage') or {}).keys()), 'num_turns': d.get('num_turns'),
           'is_error': d.get('is_error'), 'duration_ms': d.get('duration_ms'), 'usage': d.get('usage'),
           'total_cost_usd': d.get('total_cost_usd'), 'cw': cw or 'transcript not found'},
          open(meta, 'w'), indent=1)
EOF
  print "$p: exit $rc, $((t1 - t0)) s, class $cls, $cw"
  (( rc )) && cp $wd/stderr.txt $dir/$p.stderr.txt
  [[ $wd == /tmp/defs-oos-judge-* ]] && rm -rf -- $wd
done
