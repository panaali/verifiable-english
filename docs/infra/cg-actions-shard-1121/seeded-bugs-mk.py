import sys
M = "/home/seyran/code/manage-agents"
cg = open(f"{M}/chain-gate.sh.new-cgshard").read()
hp = open(f"{M}/gha/cancel-leg-runs.py.new-cgshard").read()
seeds = {
 "s1-pass-on-exit1": (cg, '(f"gha-arm-shard.sh exit {lrc}", lrc != "0")', '(f"gha-arm-shard.sh exit {lrc}", lrc not in ("0", "1"))'),
 "s2-any-exit4-is-deadline": (cg, "grep -vxE 's[0-9]+: no result by the deadline'", "grep -vxE '.*'"),
 "s3-cancel-keeps-runs": (cg, 'if [ "$stop" = cancel ]; then ghrc "FIX_EARLY"; rm -f', 'if [ "$stop" = cancel ]; then rm -f'),
 "s4-ignore-suspended": (cg, '[ -f $M/ACTIONS_SUSPENDED ] && { print -r -- "ACTIONS_SUSPENDED"; return 1; }', ':'),
 "s5-no-hard-limit": (cg, "(( $(date +%s) - t0 >= hard )) && { stop=hard; break; }", ":"),
 "h1-cancel-completed": (hp, 'f[1] != "running" or ', ''),
 "h2-403-is-ok": (hp, 'if st == "202":', 'if st in ("202", "403"):'),
}
for n, (src, a, b) in seeds.items():
    assert src.count(a) == 1, (n, src.count(a))
    ext = "py" if n.startswith("h") else "sh"
    open(f"/tmp/cgshard-seed/{n}.{ext}", "w").write(src.replace(a, b))
print("ok", len(seeds))
