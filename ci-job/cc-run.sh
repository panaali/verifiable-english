#!/bin/bash
# Claude cloud runner for one VE job (2026-10-28 dri-claudecloud, reviews/claude-cloud-pool-20261028.md; flag CLAUDE_CLOUD_POOL).
# The same job commit as the GitHub Actions pool (gha-job.sh: ONE commit on the job's exported head adding only
# ci-job/job.json, ci-job/job.sh, the workflow file and this file), pushed as cc-job/<job> (ve-job.yml runs on ci-job/** only).
# A ve-runner cloud session (ccloud-start.sh: one short Haiku prompt) fetches cc-job/<job>, copies this file to /tmp and
# starts it under setsid; this script does what ve-job.yml's run and publish jobs do:
#   checks the commit's shape (parent = job.json "head", no merge, only those files), adds a detached worktree at head
#   (/tmp/cc-wt; the session's own checkout is untouched), records the machine (cc.txt: nproc, memory, lean, uv), runs
#   bash job.sh run <worktree> <out> <job.json "argv"...>   (the cloud runner's contract, as on Actions)
#   then commits ONLY cloud-results/<job>/ on top of head and pushes it to <result branch> (claude/cc-result-<job>; never
#   --force, never another branch; one retry after 20 s). Ends by writing /tmp/cc-out/END: "PUBLISHED <sha>" or "FAILED <why>".
# usage: cc-run.sh <job> <job commit> <result branch>      (run from the session's VE checkout, which has the job commit)
# Tests only: CC_RUN_TMP (default /tmp), CC_RUN_NOPUSH=1 (commit, no push); the drop-root seams below.
# As root (the cloud session's uid 0) the job runs as an unprivileged user: see "drop root".
set -u
JOB=$1; JC=$2; RB=$3; R=$PWD; T=${CC_RUN_TMP:-/tmp}; O=$T/cc-out; WT=$T/cc-wt; C=$T/cc-job
export PATH=/usr/local/bin:/opt/lean/bin:$HOME/.local/bin:$PATH
mkdir -p "$O" "$C"; t0=$(date +%s)
end(){ echo "$1" > "$O/END.tmp" && mv "$O/END.tmp" "$O/END"; echo "cc-run: $1"; exit 0; }
[[ $JOB =~ ^[A-Za-z0-9._-]+$ && $JC =~ ^[0-9a-f]{40}$ && $RB == claude/cc-result-$JOB ]] || end "FAILED usage"
# --- the job commit's shape (as ve-job.yml's "job commit" step)
git -C "$R" cat-file -e "$JC^{commit}" 2>/dev/null || end "FAILED job commit $JC not fetched"
git -C "$R" show "$JC:ci-job/job.json" > "$C/job.json" && git -C "$R" show "$JC:ci-job/job.sh" > "$C/job.sh" || end "FAILED no ci-job files"
head=$(python3 -I -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["job"]==sys.argv[2]; print(d["head"])' "$C/job.json" "$JOB") || end "FAILED job.json is not $JOB"
[ "$(git -C "$R" rev-parse "$JC~1")" = "$head" ] && ! git -C "$R" rev-parse -q --verify "$JC^2" > /dev/null || end "FAILED the job commit's parent is not $head"
extra=$(git -C "$R" diff --name-only "$JC~1" "$JC" | grep -v -x -E 'ci-job/job\.json|ci-job/job\.sh|ci-job/cc-run\.sh|\.github/workflows/ve-job\.yml' || true)
[ -z "$extra" ] || end "FAILED the job commit changes other files: $extra"
# --- worktree at head, machine facts
rm -rf "$WT"; git -C "$R" worktree prune 2>/dev/null
git -C "$R" worktree add -q --detach "$WT" "$head" 2>> "$O/cc-run.log" || end "FAILED worktree at $head"
{ echo "job=$JOB job_commit=$JC session=${CLAUDE_CODE_REMOTE_SESSION_ID:-?} nproc=$(nproc)"; free -m | awk '/Mem:/{print "mem_total_mb="$2" mem_avail_mb="$7}'
  df -h "$T" | awk 'NR==2{print "tmp_free="$4}'; lean --version 2>&1 | head -1; uv --version 2>&1; } > "$O/cc.txt"
printf 'step\trc\tseconds\nsetup\t0\t%s\n' "$(( $(date +%s) - t0 ))" > "$O/cc-setup.tsv"
# --- drop root (2026-10-31 dri-ccloud-env-lean-share, backlog ccloud-env-lean-share, reviews/ccloud-tests-20261031.md): the
# cloud session runs as uid 0 and root passes every permission check (os.access(W_OK) true on a read-only shared file:
# tests/test_lean_share.py:102 failed in 2 of 2 cloud runs; pytest-of-root, HOME=/root). Actions' runner and the VM run as a
# normal user, so as root the job runs as user ccrun (created if missing). The full history is fetched as root first (root's
# git setup). ccrun owns the session checkout's git dir (the worktree's index, fetches and `git branch -f main` write there),
# the worktree, $O and $C. What root's exported variables and PATH name under root's home (the proxy's CA bundle, uv,
# ~/.local/bin, ...), plus ~/.gitconfig, ~/.ccr, uv's config, cache and pythons, is copied to the same place under its home
# and the variables are rewritten to match. A setup that fails ends FAILED (the caller takes its next path, never a false
# red). The git dir and the worktree go back to their owner before the publish. Tests only: CC_RUN_EUID, CC_RUN_USER,
# CC_RUN_UHOME, CC_RUN_AS (the command that runs "$@" as user $1).
U=""; envs=(); ccid=${CC_RUN_EUID:-$(id -u)}; t1=$(date +%s)
asuser(){ python3 -I -c 'import os, pwd, sys
p = pwd.getpwnam(sys.argv[1]); os.initgroups(p.pw_name, p.pw_gid); os.setgid(p.pw_gid); os.setuid(p.pw_uid)
os.execvp(sys.argv[2], sys.argv[2:])' "$@"; }
if [ "$ccid" = 0 ]; then U=${CC_RUN_USER:-ccrun}; H0=${HOME:-/root}
  [ -n "$H0" ] && [ "$H0" != / ] || end "FAILED drop root: root's HOME is '$H0'"
  git -C "$R" fetch -q --unshallow --tags origin 2>> "$O/cc-run.log" || git -C "$R" fetch -q --tags origin 2>> "$O/cc-run.log"
  id -u "$U" > /dev/null 2>&1 || useradd -m -U -s /bin/bash "$U" 2>> "$O/cc-run.log" || end "FAILED drop root: useradd $U"
  UG=$(id -g "$U") && UH=${CC_RUN_UHOME:-$(getent passwd "$U" | cut -d: -f6)} && [ -n "$UH" ] && [ "$UH" != / ] && mkdir -p "$UH" \
    || end "FAILED drop root: no home for $U"
  dup(){ local d=$UH/${1#"$H0"/}; [[ $1 == "$H0"/* ]] && [ -e "$1" ] && [ ! -e "$d" ] || return 0
    mkdir -p "$(dirname "$d")" && cp -a "$1" "$d" && echo "drop root: copied $1" >> "$O/cc-run.log"; }
  rew(){ local p parts out=(); IFS=: read -r -a parts <<< "$1"
    for p in "${parts[@]}"; do case $p in "$H0"|"$H0"/*) dup "$p"; out+=("$UH${p#"$H0"}");; *) out+=("$p");; esac; done
    local IFS=:; printf '%s' "${out[*]}"; }
  for f in .gitconfig .ccr .config/uv .cache/uv .local/share/uv .local/bin; do dup "$H0/$f"; done
  [ -f "$H0/.gitconfig" ] && [ -f "$UH/.gitconfig" ] && sed -i "s#$H0/#$UH/#g" "$UH/.gitconfig"
  for n in $(compgen -e); do case $n in HOME|USER|LOGNAME|PWD|OLDPWD|_|MAIL) continue;; esac
    v=${!n}; [[ $v == *"$H0"* ]] && envs+=("$n=$(rew "$v")"); done
  envs+=("HOME=$UH" "USER=$U" "LOGNAME=$U")
  gd=$(cd "$R" && cd "$(git rev-parse --git-common-dir)" && pwd) && own=$(stat -c %u:%g "$gd") || end "FAILED drop root: no git dir"
  for d in "$R" "$T"; do while [ "$d" != / ] && [ "$d" != . ]; do case $(stat -c %A "$d") in *[xt]) ;; *) chmod o+x "$d";; esac; d=$(dirname "$d"); done; done
  chown -R "$U:$UG" "$UH" "$gd" "$WT" "$O" "$C" 2>> "$O/cc-run.log" || end "FAILED drop root: chown to $U"
  RUNAS=(${CC_RUN_AS:-asuser} "$U" env "${envs[@]}")
  miss=$("${RUNAS[@]}" bash -c 'for t in lean lake zstd uv git python3; do command -v $t > /dev/null || printf "%s " $t; done
    for d in "$@"; do [ -w "$d" ] || printf "write:%s " "$d"; done' _ "$WT" "$O" "$gd") || end "FAILED drop root: cannot run as $U"
  [ -z "$miss" ] || end "FAILED drop root: $U lacks ${miss% }"
  echo "run_as=$U uid=$(id -u "$U") home=$UH umask=$(umask) root_home=$H0 rewritten=$(( ${#envs[@]} - 3 ))" >> "$O/cc.txt"
else echo "run_as=$(id -un) uid=$ccid home=$HOME umask=$(umask)" >> "$O/cc.txt"; fi
printf 'drop_root\t0\t%s\n' "$(( $(date +%s) - t1 ))" >> "$O/cc-setup.tsv"
# --- run (same contract as the Actions workflow's job step)
mapfile -t argv < <(python3 -I -c 'import json, sys; print("\n".join(json.load(open(sys.argv[1]))["argv"]))' "$C/job.json")
if [ -n "$U" ]; then "${RUNAS[@]}" bash "$C/job.sh" run "$WT" "$O" "${argv[@]}" >> "$O/cc-run.log" 2>&1; jrc=$?
  chown -R "$own" "$gd" "$WT" 2>> "$O/cc-run.log"  # the publish below runs git as root (git refuses a dir root does not own)
else bash "$C/job.sh" run "$WT" "$O" "${argv[@]}" >> "$O/cc-run.log" 2>&1; jrc=$?; fi
echo "job_rc=$jrc job_s=$(( $(date +%s) - t0 ))" >> "$O/cc.txt"
# --- publish (as ve-job.yml's publish job): only cloud-results/<job>/ on top of head
cd "$WT" || end "FAILED no worktree"
D=cloud-results/$JOB; rm -rf "$D"; mkdir -p "$D"
for f in "$O"/*; do [ -f "$f" ] || continue; case $f in */END|*/END.tmp) continue;; *.log) tail -n 200 "$f" > "$D/$(basename "$f").tail";; *) cp "$f" "$D/";; esac; done
git add -- "$D" && git -c user.name="VE claude-cloud runner" -c user.email=noreply@anthropic.com commit -q -m "cc-job $JOB: result" -- "$D" || end "FAILED result commit"
rc=$(git rev-parse HEAD)
[ -n "${CC_RUN_NOPUSH:-}" ] && end "PUBLISHED $rc (not pushed: test)"
git push -q origin "HEAD:refs/heads/$RB" 2>> "$O/cc-run.log" || { sleep 20; git push -q origin "HEAD:refs/heads/$RB" 2>> "$O/cc-run.log"; } || end "FAILED push of $RB (see $O/cc-run.log)"
end "PUBLISHED $rc job_rc=$jrc"
