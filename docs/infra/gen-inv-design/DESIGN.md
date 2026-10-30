# Generated inventories out of branches (gen-inv-design)

**Status:** design only, 2026-10-28. No script or product file changes here. Item gen-inv-design (waste audit
2026-10-28 row 4; PIPELINE-LIMITS L82, L85, L87, L110; backlog req:20261028-0031).

**Recommendation:** use design (a), train-only writing, for the files derived from the compiled tree: the Lean
inventories, the audit manifests, the axiom record, the checker pins and the assurance doc. Use (b), per-unit files,
only for the signed ledgers: the trust allowances, the trust-classes side table and the decoder pins. The train cannot
write those, because each change carries a decision. With (a), the L82 stale-lock class cannot happen on a published
candidate. First item: **gi-1**, which takes both audit manifests out of every build: the `VE.Audit` import, the
`ResponseShape.*` glob of `lean/lakefile.toml`, and the dump's own build (about 150 lines). (a) needs it, and it is
worth doing on its own.

Labels: **measured** means read from a log or from git with the command or window given; **estimated** means derived
from measured numbers by the arithmetic shown; **assumed** means not yet measured, and the item that measures it is
named.

## 1. The files, sorted by what produces them

| Class | Files | Produced from | Today's writer | Merge strategy today |
|---|---|---|---|---|
| D1 Lean inventories | `lean/declarations.txt`, `lean/statements.txt`, `lean/predicates.txt` | the compiled environment of the whole tree (`tools/lean_statements.py`) | builder (`regen --write`), the train's branchregen and specregen, verify-fix | `ve-generated`, then regenerated |
| D2 Audit manifests and record | `lean/VE/Audit.lean`, `lean/ResponseShape/Audit.lean`, `lean/axioms.txt` | D1 plus `#print axioms` (`lean/audit.py --write`) | the same | the same |
| D3 Checker pins | `lean/checkers.lock` (`ve_service`: 354 digests, `rust_jsonl`: 18) | the built `ve_service` and the Rust release binary of the tree | builder (`checker-pins`), the train's branchregen (since L82, Oct 27), `regen_merge` | json ledger (union) |
| D4 Assurance doc | `docs/spec/assurance-manifest.md` | `ve/assurance-manifest.json` and the tree | builder, branchregen | regenerated |
| L1 Trust budget and allowances | `docs/trust-baseline.json` (budget: 3 numbers; 191 allowances) | budget: a measurement of main; allowances: signed decisions | builder (`trust_map.py --allow`); the budget's `--write` never runs (L85) | json ledger |
| L2 Trust classes | `tools/trust-classes.json` (15,552 lines) | a hand-written side table, one entry per module or pattern | builder | json ledger |
| L3 Decoder pins | `ve/assurance-manifest.json` | hand-reviewed pins | builder | json ledger, decoder total recomputed |

D1-D4 are functions of the tree, so a machine can always rewrite them, and only the merged tree gives the right
answer. L1-L3 record decisions: each change carries a signature or a review, so no machine can produce them, and a
merge must keep both sides' decisions. The two designs in the task fit these two classes differently (sections 4-6).

## 2. Measured costs

| What | Number | Source |
|---|---|---|
| Train candidate FAILs from Oct 19 that were generated files | 15 of 19 | waste audit row 4 (measured there) |
| Candidate FAILs, Oct 20 ~09Z to Oct 28 15Z | 12. Of these, 2 were stale D1/D2 (me-9, df-1ab: Mac "Trust counts: exit 1", audit=1); 6 were an unpinned `ve_service` (D3: ap-1f, sc-1b twice, arch-20261026-2, ap-1bc, ap-1be); 4 had other causes (tests, coverage) | `merge-train.log` from line 20000; causes from `cand-<label>-x86.final.md` ("Lean build ve_service <d> is not pinned") |
| ap-1be's unpinned FAIL came after the Oct 27 L82 fix (it falls later in the log) | 1 | the "probe 0 does not pin" hole that L82 leaves open |
| Branch regens (branchregen, plus 13 speculative) | 70 runs, 78,452 s = **21.8 h** of VM time; median 1,101 s, range 272-2,154 s | `merge-train.log`, every "branch regen of" line (Oct 20 10Z to Oct 28) |
| Items regenerated more than once | 16 of 47 (10 twice, 5 three times, 1 four times) | the same lines, counted per label |
| Publications in the same window | 71 | "published" lines from line 20000 |
| Time per regen entry, train (Oct 27 17Z to Oct 28 15Z, 3,036 rows; review F4) | `lake-build` (28 runs): median 573 s, p90 806 s, max 1,013 s (ve-sc-5rb, 07:14Z Oct 28). `lean-statements` (14): median 95 s, p90 119 s. `lean-audit-manifests` (14): median 136 s, p90 169 s. `checker-pins` (14): under 1 s | `.git/ve-regen-log.jsonl` (the per-entry timing log of `tools/regen_generated.py`), rows of mode `write`, joined to `merge-train.log`: a row is the train's when its `head` is the left-hand commit of a "branch regen of" line (14 regens in these rows, each with two `lake-build` rows, the write and the pin step) |
| The same, builders | `lake-build` (59): median 0.9 s, p90 647 s, max **1,251 s** (ve-qt-a3c, 08:04Z Oct 28, phase `bootstrap`). `lean-statements` (49): median 102 s, p90 186 s. `lean-audit-manifests` (44): median 153 s, p90 247 s. `checker-pins` (71): under 1 s (max 69 s) | the same rows, every row that joins no such line: full `--write` runs in item worktrees, fix agents' included. The long unjoined rows checked have 26-27 entries at their head; the train's run names 4 |
| Non-merge commits on main touching D1-D3 | 333 of 1,166 (29%); 67 of them are the train's "Regenerate the Lean inventories" commits, so **266 were builder, fix or sync commits** | `git log --full-history --no-merges 9f81d1c1..c8b1f4f3` (Oct 19 to this branch's base) |
| Commits on L1-L3 in the same range | trust-classes 158, trust-baseline 80, assurance-manifest.json 75 (none by the train) | the same command |
| Presync conflict files that were generated or registry files | 75 of 108 | waste audit row 4 |
| Builder CW spent on inventory and manifest bookkeeping | 6% | waste audit row 4 |
| Python files that name an inventory path | declarations.txt 24 (10 tests), statements.txt 31 (14), predicates.txt 12 (5), axioms.txt 11 (7), VE/Audit.lean 13 (8), checkers.lock 43 (12), trust-baseline.json 14 (8) | `git grep -l -F <path> -- '*.py'` on c8b1f4f3 |

Most of a branch regen's 18 minutes is not the inventory dump, which takes about 4 minutes (95 s + 142 s at the
median). The rest is the `lake build` of a tree that main moved under the branch, at the VM's load. A design that
regenerates exactly once per published tree, on that tree, removes the repeats (16 items, 23 extra runs). It also
removes the FAILs, which happen because the tree that was regenerated is not the tree that is gated.

## 3. How these files are checked today (unchanged by either design unless stated)

- **gate.py** (`tools/gate.py`): after `lake build`, the "Trust counts" stage runs `trust_map.py --files`, whose
  `scan_tree` fails when a module's source hash is not the one in `declarations.txt` (stale D1). In full mode, "Lean
  audit" runs `lean/audit.py` (D2 against D1 and `#print axioms`). The Rust stage fails on an unpinned release binary
  (D3). Freshness tests in the suite check the rest, e.g. `test_lean_audit_record.py::test_committed_manifests_are_the_generated_ones`
  and the `fresh:` tests of each registry entry.
- **x86 essentials** (`manage-agents/x86-essentials.py`): `lean_build`, then `lean_pins` ("Lean build ve_service <d>
  is not pinned"), then the Rust pin. No trust counts and no audit (gi-1 added the audit; section 9), so it is the leg
  where D3 fails and D1/D2 pass.
- **merge train**: `branchregen` (L87) rewrites D1/D2/D4 and, since L82, D3's `ve_service` on the branch after its
  merge of main, when the probe (`trust_map.scan_tree` stale modules) is above 0. `specregen` (L110) does the same on
  a detached merge with the candidate ahead. `candregen` probes the candidate only. `mkcand` uses
  `git merge-tree` in `$R`, which has no `.gitattributes`, so D1/L2 conflict and the item leaves the queue (L110: 12 of
  12 queue leaves were Lean pairs).
- **review-ready.py**: clean tree, a passing gate of HEAD, seeded bugs, DELTA rulings. It checks nothing about
  generated files.
- **R16 / DELTA trust counts**: the builder runs `trust_map.py --check`. That measures HEAD from the committed D1
  (fresh because the builder regenerated it) and the base with `measure_rev`, which extracts the merge base's committed
  tree. It then records growth with `--allow` into L1.

## 4. Design (a): branches never commit D1-D4; the train writes them on the exact candidate

### Mechanism

1. `tools/regen_generated.py` owns the list. A new entry field, `writer="train"`, is set on `lean-statements`,
   `lean-audit-manifests`, `checker-pins` (both keys) and `assurance-doc`. It is the only list of train-only files, and
   every other tool reads it from there.
2. **A local inventory overlay.** On a branch, the writers of those entries write to
   `lean/.lake/ve-inventory/` (git-ignored, beside the build it describes), not to the committed path. One accessor,
   `inventory_path(name)` in `tools/lean_statements.py`, returns the overlay copy when its module hashes match the tree.
   A missing or stale overlay is an error that names the stale modules: the accessor never falls back to the committed
   copy, which would silently describe another tree (DRI condition 1(b); review F5). Only a run that asks for the
   committed copy gets it: candidate mode and `--committed`, an explicit switch, not a fallback. `trust_map`, `audit.py`,
   `regen_generated`, `lean_service` (pins) and the tests read through it. The train writes the committed path with
   `--write --committed`.
3. **The committed copy stays on main**, written only by the train, so `measure_rev(base)` and reviewers' `git show`
   of main still work, and main's freshness check is today's check.
4. **Both audit manifests leave every build** (item gi-1). On a branch the committed manifests are main's, so a branch
   that renames or deletes a theorem or module would fail wherever a tool compiles a manifest it may no longer write.
   Four routes compile or hash them today (measured on c8b1f4f3), and gi-1 closes each:
   - `lean/VE.lean` imports `VE.Audit` (the `VE` library's root): the import is dropped.
   - `lean/lakefile.toml`'s `ResponseShape` library (`globs = ["ResponseShape.*"]`, a default target) builds
     `ResponseShape.Audit`, which nothing imports (its olean is in the build). A Lake glob cannot exclude a module, so
     the manifest moves out of the glob, to `lean/ResponseShapeAudit.lean` (module `ResponseShapeAudit`, in no
     `lean_lib`; layer 5 in `tools/layer_policy.py`, like `VE.Audit`). `audit.MANIFESTS`, the
     `lean-audit-manifests` registry entry, `.gitattributes` and the three tests that name the path
     (`test_lean_audit_record.py`, `test_regen_generated.py`, `test_merge_tooling_evidence.py`) follow. Listing the
     library's modules instead would need a lakefile edit for every new ResponseShape module.
   - `lean_statements.dump_all` runs `lake build` on every tree module by name and imports each module outside `VE`
     alone, so it compiles both manifests. It leaves out the modules of `audit.MANIFESTS`: they declare nothing, and
     their `module` hashes already come from the generated text, not from the file.
   - `trust_map.scan_tree` hashes every source against `declarations.txt`. From gi-2a it reads each manifest through
     `inventory_path`, as `audit.py` does.

   One list says where the manifests are: `audit.MANIFESTS`. `RUN_ONLY` in `tools/check_lean_imports.py` gains one
   entry per manifest, derived from that list (run by `lean/audit.py`). Its existing check fails when a `RUN_ONLY`
   module is built by default by any route, import or glob, so a third manifest, or a new import or glob that reaches
   one, fails `test_every_lean_source_is_built_by_the_default_build`. `lean/audit.py` already runs both manifests
   itself (`lake env lean`, in parallel parts), so no audit changes. The gate's "Lean audit" stage runs it as before.
5. **Runner-local pins.** A branch's own `ve_service` and Rust builds are pinned in the overlay
   (`lean/.lake/ve-inventory/checkers.local.json`). Every pin reader accepts the union of the committed and local
   pins, unless `VE_PINS_STRICT=1`. There are eleven today (review F8): `lean_service` (`BUILD_LOCK`), the Rust backend
   `ve/backends/rust_jsonl.py` (`BUILD_LOCK`, which refuses an unpinned Rust binary), `rust_build.pinned_digests`
   (gate.py's and x86 essentials' Rust check), x86 essentials' own `ve_service` read, `regen_generated` (`_lock`, read
   by `_Service.problem`, so a branch would keep reporting "not pinned" against main's lock), `lean_output_diff`
   (`LOCK`, line 313), `lean_first_cache.pinned_checkers`, `gate_collection.build_rust`, `lean_share.pinned`,
   `answer_cutoff.pinned` and `research/defeasible/baseline.py`. `answer_cutoff.pinned` also reads a commit's lock with
   `git show`, which on a branch holds main's pins, so gi-2b states what a branch's build gets there. gi-2b reduces
   them to one reader, and a guard test fails on any other read of a `checkers.lock` key. `tools/lean_first_oracle.py`
   (hashes the whole file) and `tools/test_map_recorder.py` (records that it was read) read no key. The `checker-pins`
   entry splits into `service-pins` and `rust-pins`, so each pin key has its own check and its own place in a run.
   `VE_REGEN_NO_RUST`, which today skips the Rust pin in both the write and the check, goes. The Mac runner already
   keeps runner-local pins (assume-unchanged, `mac-gate-job.sh`).

### Actors

| Actor | Does |
|---|---|
| Builder | Runs `regen_generated.py --write` as today. Train-only entries land in the overlay, so `git status` shows nothing for them, and the builder commits none of them. Runs `trust_map.py --check` as today: it reads HEAD from the overlay and the base from main's committed copy. No inventory merges and no inventory commits. The 266 builder, fix and sync commits of section 2 go to zero. |
| gate.py | New stage "Lean inventories" after `lean_build`: writes the overlay from this build (the `lean_dump_cache` replays unchanged inputs). Trust counts and Lean audit read it. **Candidate mode** (`--candidate`, set by the train and by main's daily run): `VE_PINS_STRICT=1`, and `regen_generated.py --check --only <train entries>` against the **committed** files, so a stale committed copy fails exactly as today. Each entry is checked after the stage that builds its input: the Lean entries and `service-pins` after `lean_build`, and `rust-pins` after the Rust build (today `tools/gate.py:776-786` builds Rust after the Lean stages). **Branch mode** (default): the committed train-only files must be unchanged since the merge base (`git diff --quiet $(merge-base) HEAD -- <paths>`), and every check runs on the overlay. |
| review-ready.py | New row [inventory]: FAIL when `main...HEAD` changes a train-only path. It prints `lean_statements.py --diff <main's statements.txt> <overlay>` into the review packet, so the statement gate still sees every changed theorem statement. |
| merge train: branchregen, specregen | Retired for the train-only entries (the flags stay as the veto). A branch never carries them, so there is nothing to refresh on it. |
| merge train: mkcand | `git merge-tree` cannot conflict on D1-D4: the branch side equals the merge base, so git takes the base side. After the tree `t`, a new **candidate prep** step runs on every candidate, in the warm `ve-cand-regen` worktree outside the queue lock. It builds both checkers of `t`: `lake build`, and the Rust release build in that worktree's own `rust/target`. Then it runs `regen_generated.py --check --committed --only <train entries>`, the check both legs run. If any entry fails, it runs `--write --committed` for those entries (`service-pins` and `rust-pins` pin the binaries it just built), writes the tree `t1`, and the candidate commit is made from `t1`; otherwise `t1 = t`. So the prep's condition is the legs' own check of every train-only file, not a subset of it (the probe, or the `ve_service` pin alone). A Rust-only change (probe 0, `ve_service` pinned) gets its Rust pin here; the branch may not commit that pin, so no verify-fix could add it. Items behind it wait for the prep, which is minutes (section 8), not a gate: mq.py gets a `preparing` state. |
| x86 essentials | Unchanged. It now finds both pins, `ve_service` (`x86-essentials.py:90-93`) and Rust (`:107-108`), written by the prep that built this tree. With `VE_PINS_STRICT=1`, local pins are ignored. |
| Mac leg | Full gate in candidate mode. Its runner-local pins stay as today. |

### R16, trust_map and DELTA counts without committed inventories

`trust_map.py --check` on the branch measures HEAD from the overlay. The overlay is written by the same compiled
environment the committed file would have held, and the accessor refuses it unless its module hashes match the tree.
The base is measured from main's committed copy, which the train keeps fresh. So the numbers are the ones a committed
copy would give, and R16's growth, the per-file counts in the gate record (`--files`, D3 of AR-4) and DELTA's trust
cells are produced the same way. The candidate gate then measures the merged tree in candidate mode, as today.

### L82 becomes

Both pins of a published tree, `ve_service` and the Rust release binary, are written by the same prep step that built
that exact tree, before either leg starts. The step writes whenever a built checker is unpinned, not only when the
inventory probe is above 0. That closes ap-1be's hole, and the same hole for Rust, which L82's fix never covered:
`branchregen` pins `ve_service` only. No commit touched `rust/` in the window of section 2, but `rust_jsonl` holds 18
pins, so Rust changes do happen. The class can then fail only if two builds of the same tree with the same toolchain
on x86 differ. That would be a real reproducibility bug, and x86 essentials would catch it as today.

### Risks

- The prep is on the critical path of every Lean candidate: about 13 min at the median and 18 min at p90, the build of
  `t` included, and one at a time (section 8, review F3). **Estimated** net: today the 1,101 s median branchregen is
  also on that path, in the item's own worktree, and the leg rebuilds afterwards.
  If the prep's `.lake` is shared with the x86 slot (r2-leanshare keyed by `t1`'s `lean/` tree; **assumed** to fit, to
  be checked in gi-3), the leg's build is a restore.
- The prep's Rust build runs on every candidate. **Measured**: 81 `checker-pins` writes in `.git/ve-regen-log.jsonl`
  (Oct 27 22Z to Oct 28 15Z) ran the Rust release build. 76 took under 1.2 s (cargo found nothing to rebuild, median
  0.33 s), and 5 took 28-69 s (rebuilds in builder worktrees). The prep keeps its `rust/target` warm, so an unchanged
  `rust/` costs about a second. A cold target is not in the window (**assumed** a few minutes, measured in gi-3).
- Tests that read an inventory path directly would read main's stale copy on a branch. All 24-31 readers per file must
  go through the accessor (gi-2a). One guard test fails on a literal path outside the accessor.
- Selected-test runs on a branch need the overlay: the conftest writes it once per session for tests marked
  `needs_inventory` (cached, so seconds when nothing changed).

## 5. Design (b): per-module fragments, still committed by branches

### Mechanism

D1 and D2 become `lean/inventory/<Module>.txt`: the module's hash, declarations, predicates, theorem statements and
each theorem's axioms. `Audit.lean` becomes per-directory manifests (or leaves every build, as in gi-1). D4 is unchanged.
**D3 cannot be split**: a `ve_service` digest belongs to the whole service closure. L1-L3 split per item (allowances)
and per module directory (classes).

### Actors

| Actor | Does |
|---|---|
| Builder | Regenerates and commits its modules' fragments, as today but in smaller files. The bookkeeping stays (it shrinks only where conflicts used to happen). |
| gate.py | Unchanged stages, reading a directory. It must also check that fragments of **unchanged** modules are still fresh, because a fragment depends on its imports (below). |
| review-ready.py | Unchanged. |
| merge train | Stacked items whose modules differ no longer conflict on D1/D2. **branchregen stays** for the transitive-staleness case and D3. specregen stays for D3 and for same-module pairs. |
| x86 essentials | Unchanged. L82 stays, so it needs the probe-0 pin fix anyway, i.e. (a)'s pin step for D3 alone. |

### What fragments do not fix

- **Clean merge, stale result (L87) remains.** A module's statement `uses` lines, `expr` hashes of types that unfold
  through notation, and above all its theorems' axioms depend on imported modules. Item A changes lemma X to use
  `Classical.choice`. Item B's untouched fragment for Y, a theorem over X, merges cleanly and is wrong. The gate
  catches it (no check is weaker), and the result is a FAIL plus a verify-fix, rarer than today but the same class.
- **D3 still conflicts and goes stale.** That is the 6 of 8 generated-file FAILs measured since Oct 20.
- **Migration touches every reader's format** (24-31 Python files per inventory, `trust_map.scan_tree`,
  `lean_dump_cache`, `audit.py`), and the 22,948-line `declarations.txt` becomes around 400 files.

### R16 and DELTA

The same as today: committed fragments of HEAD, base from `measure_rev`.

## 6. Comparison

| | (a) train-only D1-D4 | (b) fragments |
|---|---|---|
| Generated-file candidate FAILs (8 of 12 since Oct 20) | D1/D2 (2): gone, because the prep writes the exact tree. D3 (6): gone, because the pin comes with the build | D1/D2: fewer (only transitive cases). D3: unchanged unless (a)'s pin step is added |
| Branch regens (70 runs, 21.8 h in 8 days) | 0 on branches; one prep per Lean candidate, about 13 min at the median with the build, one at a time (section 8) | stays for transitive cases and D3 |
| Builder commits on D1-D3 (266 since Oct 19) | 0 | about the same number, in smaller files |
| Presync and queue conflicts on D1/D2 | none possible | only for same-module pairs |
| Checks | the same checks; candidate mode strict as today; branch mode runs them on the overlay | the same checks |
| Review of changed statements | a printed diff in the review packet (review-ready) | the git diff, as today |
| Product files touched | `lean/VE.lean` (one import), `lean/ResponseShape/Audit.lean` moved out of the lakefile's glob, the dump's module list, accessor users, one pin reader (`lean_service`, `rust_jsonl`) with the local union, gate stage | every inventory reader and the inventory format |
| Size (section 8) | about 1,420 hand-written lines over 4 items | about 1,400 plus D3's pin step anyway (**estimated**, from the reader counts) |

L1-L3 fit neither (a) nor whole-file regeneration, because their entries are decisions. For them the (b) idea is the
right one: one allowance file per item (`docs/trust-allowances/<item>.json`, read as a directory), the budget
recomputed or written by the train only (L85 (a)+(b)), and trust classes split per module directory. With that,
`mkcand`'s `merge-tree` stops leaving the queue on `tools/trust-classes.json`, the other half of L110's 12 leaves.

## 7. Migration (design (a) plus the ledger split)

1. **gi-1**: take both manifests out of every build (section 4, step 4): drop `import VE.Audit` from `lean/VE.lean`;
   move `lean/ResponseShape/Audit.lean` out of the lakefile's `ResponseShape.*` glob to `lean/ResponseShapeAudit.lean`
   (`audit.MANIFESTS`, the registry entry, `.gitattributes`, `tools/layer_policy.py` and the three tests that name the
   path follow); leave `audit.MANIFESTS` out of `lean_statements.dump_all`'s build and imports; derive two `RUN_ONLY`
   entries from `audit.MANIFESTS`, so a manifest that any import or glob brings back into the default build fails
   `test_every_lean_source_is_built_by_the_default_build`. `audit.py` runs the manifests and the gate stage runs
   `audit.py`, both unchanged. Measure `lake build` after a one-theorem change, before and after (resolves the
   **assumed** build-time gain). This works under today's process too.
2. **gi-2a**: the train-only field in the registry, the overlay and the `inventory_path` accessor; move every reader to
   it, with a guard test. Writers still write the committed path by default, so nothing changes yet: until gi-2b turns
   the default on, every run asks for the committed copy, and the accessor's stale error applies from that flip.
3. **gi-2b**: gate.py's "Lean inventories" stage, branch and candidate modes (each train entry checked after the
   stage that builds its input: `rust-pins` after the Rust build), one pin reader for both keys with the local-pin
   union and `VE_PINS_STRICT` (every reader section 8 lists, review F8) and a guard test, the split
   of `checker-pins` into `service-pins` and `rust-pins` (`VE_REGEN_NO_RUST` goes), and `--committed` on the
   writers. Turn the default on: on a branch, writers write the overlay.
4. **gi-3** (manage-agents; DRI improvement review, flag `INV_TRAIN_ONLY`): the candidate prep in `mkcand` (both
   checkers built on every candidate; it writes when the train entries' own check fails, so a Rust-only change gets
   its Rust pin: a harness test beside DRI condition 1(d)'s `ve_service` case), the mq.py
   `preparing` state, the review-ready [inventory] row and statements diff, `--candidate` in both legs, and the build
   checklist line "do not commit train-only files". branchregen and specregen stop for those entries. The veto is
   `rm INV_TRAIN_ONLY`: the train then falls back to branchregen, and branches that committed nothing still pass.
5. **Flip**: branches in flight that already committed D1-D4 are reset to the merge base's copies by the train's
   presync (one `git checkout <merge-base> -- <paths>` commit), which is safe because those files are generated.
6. **gi-4** (in parallel after gi-2a): ledger split (L85).

### Design (b): not adopted (review F7)

The DRI signed (a), so nobody builds these steps. They are here so the comparison in section 6 can be checked.

1. Split D1 and D2 into `lean/inventory/<Module>.txt` in one commit, with the Audit manifests per directory or out of
   every build (gi-1 did the latter). Move every reader to the new format (24-31 Python files per inventory,
   `trust_map.scan_tree`, `lean_dump_cache`, `audit.py`).
2. Teach gate.py to check the fragments of unchanged modules too, because a fragment depends on its imports.
3. Add (a)'s pin step for D3 alone, in `mkcand`, which needs the probe-0 fix either way.
4. Reset in-flight branches: presync replaces their committed D1 and D2 with regenerated fragments.
5. Keep branchregen and specregen for transitive staleness and for D3. Split the ledgers as in gi-4.

## 8. Implementation items

| Item | Scope | Size (hand-written lines, tests included) | Depends on |
|---|---|---|---|
| **gi-1** | Both manifests out of every build: the `VE.Audit` import, `ResponseShape/Audit.lean` out of the lakefile glob, the dump's build; `RUN_ONLY` from `audit.MANIFESTS`. Builder: Lean root, file move, tests; measure build time | ~150 | none (**first**) |
| gi-2a | train-only registry field, inventory overlay, `inventory_path` accessor, readers moved, guard test | ~450 | gi-1 |
| gi-2b | gate.py stage and modes (`rust-pins` after the Rust build), one pin reader with local pins for every `lean/checkers.lock` reader (review F8): `lean_service` and `rust_jsonl` (relay unchanged: the pin set only), `rust_build.pinned_digests` with its callers (gate.py, `rust_output_diff`), x86 essentials, `regen_generated`, `lean_output_diff`, `lean_first_cache`, `gate_collection`, `lean_share`, `answer_cutoff`, `research/defeasible/baseline.py`; plus its guard test, `checker-pins` split, writers' `--committed` | ~550 (~450 plus ~15 lines, test included, for each of the 7 readers added here, F8's five plus `answer_cutoff` and `baseline.py`; **estimated**) | gi-2a |
| gi-3 | merge train: candidate prep (both checkers, the train entries' check as its condition), mq `preparing`, review-ready [inventory], checklist line; test-harness | ~270 plus ~170 harness | gi-2b |
| gi-4 | per-item trust allowances, train-written budget, per-directory trust classes | ~400 | gi-2a (trust_map reader) |

**Expected effect (estimated from section 2; review F3).** About 21.8 h of branch regen VM time per 8 days, spread
over the items' own worktrees, goes to one prep per Lean candidate, run one at a time in the single locked
`ve-cand-regen` worktree. One prep is the `lake build` of `t` plus the dump, at the train's numbers: 573 + 95 + 136 =
804 s (about 13 min) at the median, 806 + 119 + 169 = 1,094 s (about 18 min) at p90. In the window of section 2, 51 of
72 first-parent merges changed a Lean source (`git log --first-parent --merges`); with the 12 FAILs that is at most 63
Lean candidates, so about 14 h, a saving of about 8 h, not 21.8 h. If the leg's build becomes a restore (**assumed**,
section 4, risks), the saving is larger. The lock caps the train at about 3-4 Lean candidates per hour, and a prep
behind the lock must wait for it: `candregen`'s `flock -w 600` skip would publish an unprepared tree, and one prep
outlasts that wait. gi-3 measures both from `merge-train.log` (DRI decision (b), cost claims). The 8 generated-file
FAILs per 8 days, each about 35 Opus-min of verify-fix plus about 2 h of
item latency (L82), go to 0. The 266 builder inventory commits go to 0, and the audit's 6% of builder CW goes with
them. The audit's estimate for its row 4 is about 0.5 h less cycle time per merged item, and these numbers do not
change it.

## 9. No check gets weaker

- Candidate and main: the committed D1-D4 must equal what the candidate's own build produces, the same condition
  `trust_map --files`, `audit.py` and the freshness tests impose today. It is now one explicit stage, with strict pins.
- Branch: the same checks run on data derived from the branch's own build, and the branch is refused if it edits a
  train-only file.
- Trust evidence: R16 growth, the per-file counts and DELTA cells come from the same measurement.
- Statement review: every changed theorem statement is shown, as a generated diff instead of a committed one.
- Audit on x86 (review F6): while `lean/VE.lean` imported `VE.Audit`, x86 essentials' `lean_build` compiled
  `VE/Audit.lean`, a build-time check of its names, and gi-1 removes that check. With the Mac leg unavailable (as with
  ap-1be), a Lean candidate could then merge with no audit on any leg. DRI decision (b) item 3 covers it: x86 essentials
  runs `lean/audit.py`, or the train refuses a Lean candidate no leg audited. gi-1 took the first option:
  `tests/test_lean_service_audit.py` runs the audit in that leg (`test_x86_audit_refuses_failure_and_accepts_success`).

## 10. Questions for the DRI

1. Adopt (a) for D1-D4 and the ledger split for L1-L3, in the order gi-1, gi-2a, gi-2b, gi-3, with gi-4 in parallel?
2. Is a generated statements diff in the review packet acceptable as the statement gate's view, instead of a committed
   `statements.txt` diff on the branch?
3. gi-3 edits merge-train.sh, mq.py and review-ready.py. Who owns it: the DRI improvement review (as with L82, L87 and
   L110) or a builder?

## 11. Revision after review (F1, F2)

The review of this design (gen-inv-design-review.final.md) found two gaps after the DRI signed (a), and this revision
closes both. The DRI's conditions are minimums, and both stay. The items now ask for more:

- **F1**: gi-1 dropped only the `VE.Audit` import, but the `ResponseShape.*` glob still builds `ResponseShape.Audit`, and
  the dump builds every tree module by name. gi-1 now closes all four routes (section 4, step 4), and the `RUN_ONLY`
  check, derived from `audit.MANIFESTS`, fails on any route that comes back. Condition 1(a)'s test stays as it is.
- **F2**: the prep ran only when the probe was above 0 or `ve_service` was unpinned, so a Rust-only change was never
  pinned, and its branch could not pin it either. The prep now builds both checkers, and its condition is the train
  entries' own check. gi-2b checks `rust-pins` after the Rust build and gives both keys one pin reader. Condition
  1(d) gains a Rust-only case in gi-3's harness.

The backlog rows gi-1, gi-2b and gi-3 need these scopes and sizes (REPORT.md lists them).
