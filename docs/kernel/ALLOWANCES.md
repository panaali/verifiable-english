# Kernel allowances

The kernel's size is the `kernel_lines` of [closure-baseline.json](closure-baseline.json), measured by
`python3 tools/kernel_closure.py` ([the kernel boundary](../spec/kernel-boundary.md), sections 2 and 6).
It may fall freely. It may rise only with a line in the table below, added in the same change that
raises it and signed by the architect seat (`manage-agents/fable-team/architect/HANDOFF.md`).
`tests/test_kernel_closure.py` reads the figure after the words "signed total:".

signed total: 9,565 lines

| Date | Change | Door | Lines | Total after | Signed |
|---|---|---|---:|---:|---|
| 2026-11-11 | First measurement on main `97b3c7999a`: the paths certificate, route, norms and softNorms | none | 9,565 | 9,565 | architect seat, round 1 |

Pre-signed, to be entered by the change that uses it:

| Change | Door | At most |
|---|---|---:|
| KB-1: `lean/VE/Kernel/Carry.lean` as in the specification's section 3 (it is counted only once a kernel path's fold uses it) | C | 80 |
