# eff-branch-lean-cache: a branch's Actions lake build starts from that item's previous run

- **Status:** BUILT, harness only. The new code runs only when the flag `BRANCH_LEAN_CACHE` is on. That flag is still off.
  Turning it on and measuring the saving are the job of the existing row `gha-wf2-flag-on`, which is ready.
- **VE files changed:** this report only. The VE workflow is unchanged: `ve-job.yml` v2 already packs a branch build
  under its own lean tree and uploads it, and a restore of another tree is already a seed (`seed-pinned`).
- **manage-agents files changed:** `lean-branch-cache.sh`, `gha-select.sh` and
  `test-harness/branchcache/test-branchcache.zsh`. Each has a backup `.bak-20261030-eff-branch-lean-cache`. Each was
  edited as `.new`, checked with `zsh -n` and then moved into place.

## Row and note

Row `eff-branch-lean-cache`: "Actions: start a branch's lake build from that item's previous run (branch_lake_build 4-11
min on every sweep and selected run)". Note: "each restores main's asset, none reuses the same item's last build".

| Row or note item | Delivered by | Evidence (test-branchcache.zsh) |
|---|---|---|
| reuse the same item's last build | `lean-branch-cache.sh record <rec> <tree> <item>` stores the item in the list entry. `gha-select.sh`'s record hook passes its `$item`. | B "record keeps the item in the entry"; C "the record hook lists shard 0's upload under its item" |
| start the lake build from it | `lean-branch-cache.sh pick <tree> <item>` returns the exact build of `<tree>` first (`exact`). If there is none, it returns the item's newest listed build (`seed`, with that build's tree). Quarantined builds are skipped. | B "no build of this tree, one of its item: pick prints it as a seed", "the item's newest build is the seed", "a quarantined build is never a seed", "an exact build wins over a newer seed of the item" |
| only when it is a better start than main's asset | `gha-select.sh` pins the seed only when it has fewer files under `lean/` that differ from this tree than main's picked asset has (`git diff --name-only` of the two trees). A tie, or a seed tree that is not in the VM repo, keeps main's asset. The main-asset pick now also prints that asset's `lean_tree` (4th line). | C "the item's previous build is nearer than main's asset: it seeds", "a tie keeps main's asset", "main's asset nearer than the item's build: main's kept", "an item build whose tree is not here: main's kept", "main's asset of an unknown tree: the item's build seeds", "main's asset pick prints its lean tree as the 4th line" |
| the next run of the same tree is exact | A seeded run still asks shard 0 to pack (`bpack=1`). The new build is uploaded and listed under its tree and item. | C "... it seeds, shard 0 still packs"; A "a seed restore (another tree) is packed under the new tree" (unchanged, passes) |
| other items' builds | Never used as a seed: only the item's own builds are. | B "no item given, or another item: no seed"; C "another item's build never seeds" |

### Scope: selected runs only, not sweeps or gates

The row title also names "sweep" runs. Sweeps, gates and trust_mutants are dispatched by `cloud-dispatch.sh` and
`gha-arm-shard.sh`, and they restore only main's assets. That rule comes from the gha-wf2 security review, recorded in
the row `gha-wf2-gate-nopin`: a branch build comes from the branch's own `uv sync` and `lake build`, so only
selected-test runs may pin one. This item keeps that rule. The seed path is in `gha-select.sh` only, behind the same
flag and the same `pool = actions` test as gha-wf2's exact pin. C "the Claude cloud pool: no seed" and "flag off: no
seed" check both conditions.

### Why a seed of another tree is safe for a selected run

It is the same mechanism as main's seed assets, which are also built from other trees. `ve-cache.sh` restores the pinned
asset after checking its sha256, its member names and its seal (platform and `lean --version`), and reports
`seed-pinned`. The job's `lake build` then always runs, and Lake's traces rebuild whatever differs. No exact-tree claim
is made: `cmd-job.sh` skips packing only after an exact restore.

## Saving

Not measured: the flag is off. The row's note gives 241-688 s for `branch_lake_build` (timings.tsv, Oct 30). A seed of
the item's previous commit usually differs in the few files the item touched since its last run. Main's asset differs
in everything the branch changed. The saving is UNVERIFIED until `gha-wf2-flag-on` measures pinned against unpinned
runs. That row should also count runs where `say` logged "seeded from <item>'s previous build".

## Tests

- `zsh test-harness/branchcache/test-branchcache.zsh` (installed files): 54 passed, 0 failed (it was 38/0 before; 16
  tests added).
- `zsh test-harness/maclast/test-maclast.zsh`: 29 passed, 0 failed (it stubs gha-select.sh; run as a neighbour check).

## Seeded bugs (each on a temporary copy, run through test-branchcache.zsh, then discarded)

| # | File | Bug | Failing test |
|---|---|---|---|
| S1 | lean-branch-cache.sh (pick) | any item's build is a seed | B "no item given, or another item: no seed" |
| S2 | gha-select.sh (pin block) | `ns < nm` changed to `ns <= nm`, so a tie seeds | C "a tie keeps main's asset (shard 0 packs)" |
| S3 | gha-select.sh (pin block) | a seeded run does not pack | C "the item's previous build is nearer than main's asset: it seeds, shard 0 still packs" (and 1 more) |
| S4 | lean-branch-cache.sh (record) | the item is dropped from the entry | B "record keeps the item in the entry" (and 7 more) |
| S5 | lean-branch-cache.sh (pick) | the item's oldest build is the seed | B "the item's newest build is the seed" |

## DELTA

None. VE behaviour, verdicts and outputs are unchanged, and no trust change is involved.
