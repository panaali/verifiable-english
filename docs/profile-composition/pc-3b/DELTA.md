# pc-3b DELTA: G1 with G4 (profile-composition PC-3, the rest)

Feature item pc-3b (plan and spec at 3dfadd302 on `design/profile-composition`: plan PC-3, spec 1.6). Base: main at
ea108ea4e.

No user-visible delta, so there is no table. `composed_superpose_all` is a theorem no route reads: no service mode,
schema, diagnostic or answer changes (`git diff --stat` touches no file under `ve/`, `rust/`, `lean/VE/Service/` or
`lean/VE/Compose/Dispatch.lean`). The trusted base does not grow: `uv run python tools/trust_map.py --check` exits 0
with K +0, S +0, D +0, G +0, trusted +0 against the base.
