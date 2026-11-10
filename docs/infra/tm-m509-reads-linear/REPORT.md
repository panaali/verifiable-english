# tm-m509-reads-linear: READS's worklist made linear, and a probe timeout named

Item tm-m509-reads-linear (infra). Row and task: reviews/dri-decisions-20261110-tm-m509-route-probe.md items 1-2.
This item answers the STOP of tm-m509-route-probe (docs/infra/tm-m509-route-probe/REPORT.md at 42ffbc9f9). Branch
infra/tm-m509-reads-linear, base a7659c5f12. No DRI signature is reserved.

## Result

- **M509 is KILLED on this branch at `--build-timeout 500`.** Before the change it was UNKNOWN.
- **The RouteExamples mutant probe now finishes in 363.5 s.** Before, it was killed at 500 s.
- **A timed-out probe now says so.** Its UNKNOWN reads "the probe did not finish in 500 s (--build-timeout)".
  Before, the text was "Lean could not elaborate it in the probe".
- **The nightly still counts that UNKNOWN as unallowed** (a build timeout).

## Commits (`git log --oneline main..HEAD --no-merges`, base a7659c5f12)

- 3ec0b3d26c: READS's worklist becomes an Array queue, and a probe past --build-timeout says so. Includes the tests.
- 14d35d32b1: `probe`'s docstring names `late`.
- Later commits change only files under docs/infra/tm-m509-reads-linear/: this report, DELTA.md and the run records.

## DO (1): a linear READS worklist, in the same order

`tools/trust_mutants.py` (READS, `tmTrustWalk`) used a `List` worklist read with `head!`/`tail!` and extended with
`todo := todo ++ …`. Every visited constant copied the whole list. Now `todo` is an `Array Name` with a read index
`head`:

- `while head < todo.size`, then `todo[head]!`, then `head := head + 1`.
- New constants are pushed at the end (`todo ++ …`, Array append in place).

So the queue is first-in first-out, as before. Nothing else in the walk changed: what it visits, `seen`, the order,
and each `say`.

**Order test.** `tests/test_trust_mutants_probe_scope.py::test_the_linear_worklist_walks_in_the_list_order` builds a
small real-Lean package (`ORDER_DEFS`) with two checks:

- `tmChk_4`, a shared closure: `twice` → `shared`, `other`, and both reach `helper`.
- `tmChk_6`, a cycle: `isEven._unsafe_rec` ↔ `isOdd._unsafe_rec`.

The test installs today's READS and records every line the probe prints, in order, without the nonce. It checks
three things:

- the breadth-first order `twice, shared, other, helper`;
- `done` is last in each check, and the cycle's `isOdd._unsafe_rec` is reached;
- the lines are identical to those of the old List READS. The test rebuilds the old READS from today's text
  (`LIST_WORKLIST`, three exact replacements, each asserted to occur exactly once).

## DO (2): a probe past --build-timeout says so

`probe` now keeps the lake exit code. If the code is `TIMED_OUT`, each check the run was to walk gets an incomplete
entry with `late`, holding the rest of `Scratch.lake`'s message ("finish in 500 s (--build-timeout)").

`refusal` returns `the probe did not {late}` for an incomplete entry with `late`, on the mutant's side or the
control's. Every other incomplete or absent entry still returns "Lean could not elaborate it in the probe".

The verdict stays UNKNOWN: `settle` refuses on any reason from `reads`, as before. --build-timeout is still the only
limit on a mutant's probes; no new limit was added.

Controls run with `first.lake`, which has no time limit, so they never carry `late`. A timed-out entry is still
incomplete, so `Probes` still falls back to the whole-file probe as before.

**Timeout test.** `test_a_probe_past_the_build_timeout_says_so_and_stays_unknown` drives the real `probe`,
`Probes` and `settle` with a lake that returns `TIMED_OUT`, for both the scoped run and the whole-file fallback. It
checks three things:

- the result is UNKNOWN, and its detail ends in "(the probe did not finish in 500 s (--build-timeout))";
- the opposite direction: a run that fails with code 1 gives no entry and keeps "Lean could not elaborate it in the
  probe";
- the label is also read from the control side.

## DO (3): the nightly's classifier

I read `/home/seyran/code/manage-agents/tm-nightly.py` and did not edit it.

- `build_timeout` (line 347) matches `did not finish in ([0-9.]+) s \(--build-timeout\)` on a row's
  `raw_detail`/`detail` when the status is UNKNOWN. It matches the seeded run's detail. The probe below printed
  `build_timeout match: True` for m509-500-seeded-list-reads.json and `False` for the KILLED m509-500.json.
- `unjudged` (line 383) counts that row as an unallowed UNKNOWN and adds it to the build-timeout count.
- `allow_of` (line 240) allows only through a label's ALLOWED rows. It never reads the detail text, so the new text
  cannot make a row ALLOWED.

Cost note: `size()` (lines 394-398) subtracts one timeout divided by jobs for such a row. A timed-out probe actually
costs about two timeouts: the scoped probe, then the whole-file fallback. This is for information only; nothing
was changed.

## M509 on this branch (measured on this host: the worker VM, 32 cores, shared load)

Command (task text). A driver script in /tmp wrapped `tm.probe` to time each call; the tool file was not changed:

    uv run python tools/trust_mutants.py --base 'a270588eb^' --only M1952 --test lean/VE/Events/WireExamples.lean \
      --test lean/VE/Events/RouteExamples.lean --jobs 2 --build-timeout 500 --json docs/infra/tm-m509-reads-linear/m509-500.json

The summary line (saved in `m509-500.json`, head 14d35d32b1):

    trust_mutants: 1 KILLED, 0 SURVIVOR, 0 UNKNOWN, 0 INVALID, 0 ALLOWED, 0 NOT RUN in 1749 s

Its detail: `lean/VE/Events/WireExamples.lean:55: Expression`.

**Seeded bug: (1) reverted only.** The same driver installed the old List READS (`LIST_WORKLIST` applied in
memory); the tool file was otherwise unchanged. Record: `m509-500-seeded-list-reads.json`. Pasted:

    UNKNOWN lean/VE/Events/Wire.lean:180 VE.Events.decodeThroughLinks (D[V], trusted) list-empty: (← arrAt b "" "events") -> [] (lean/VE/Events/RouteExamples.lean:62: Expression (the probe did not finish in 500 s (--build-timeout)))
    trust_mutants: 0 KILLED, 0 SURVIVOR, 1 UNKNOWN, 0 INVALID, 0 ALLOWED, 0 NOT RUN in 2602 s

Probe seconds per `probe` call, from the driver's `PROBE` lines in /tmp/tm-m509-drv/{new,old}.log:

| probe | List READS (before) | Array READS (after) |
|---|---|---|
| WireExamples, mutant, 91 checks | 49.5 s | 44.3 s |
| WireExamples, control, 91 checks | 38.2 s | 37.1 s |
| **RouteExamples, mutant, 40 checks (scoped)** | **502.0 s, TIMED_OUT, 0/40 whole** | **363.5 s, 40/40 whole** |
| RouteExamples, mutant, whole-file fallback | 502.2 s, TIMED_OUT, 0/92 whole | not needed |
| RouteExamples, control, 40 checks (no limit) | 584.9 s | 319.5 s |

The control row has no time limit, so it gives the cleanest before/after comparison: 584.9 s → 319.5 s, 1.83 times
faster. The route-probe report measured 669.8 s on its run. The host was busy during both runs:

- after run: 5-minute load 130 at its start;
- before run: load 60 at its start.

So the before run had less competition and still timed out.

## Checks run

- `uv run pytest -q tests/test_trust_mutants_probe_scope.py -k "build_timeout or done_marker or lazy_control_incomplete or walk_reads"`:
  13 passed.
- `-k list_order`: 1 passed (12 s).
- `uv run python tools/trust_map.py --check`: `PASS: K, S and untied [V] within a7659c5f12ae`. Trust +0: no Lean file
  changed.
- Regen: not run. No generator input changed. `tools/trust_mutants.py`'s module docstring, which the code map reads,
  is unchanged.
- No Lean product file changed, so no lake build and no `lean/audit.py` run.
- No trust_mutants sweep was run. The task asks for none, and no trusted Lean changed. The M1952 run above is the
  run the task requires.
- Final selected tests: see the next section.

## Final selected run

See the end of this file (added after the run on the committed code).

## Seeded bugs (each restored; file, then the failing test)

Python, `tools/trust_mutants.py`, READS (the Lean text of the walk):

1. A prepend at the read point: `todo := todo.extract 0 head ++ … ++ todo.extract head todo.size`.
   - Fails `test_the_linear_worklist_walks_in_the_list_order`: `At index 2 diff: 'Demo.helper' != 'Demo.other'`.

Python, `tools/trust_mutants.py`, `refusal`:

2. The old text kept for a timed-out probe.
   - Fails `test_a_probe_past_the_build_timeout_says_so_and_stays_unknown`:
     `('UNKNOWN', 'lean/A.lean:2: Expression (Lean could not elaborate it in the probe)')`.

Python, `tools/trust_mutants.py`, `probe`:

3. Every run marked `late` (`if True:` in place of `if code == TIMED_OUT:`).
   - Fails the same test at the opposite-direction assertion: `{(7, 7): {…, 'late': ''}} == {}`.

On the real mutant:

4. (1) reverted only (List READS), the M1952 run above: UNKNOWN with the new timeout text.

The self-reviewer also seeded a LIFO worklist (`todo.back!`/`pop`). The order test caught it.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed Lean answer and no response schema change.
2. PASS: DO (1)-(3), every test the task names, m509-500.json, REPORT.md and DELTA.md are here (sections above).
   Paths are only those allowed. There is no new permanent report test.
3. PASS: seeded bugs 1-4 above. Each fails a named test or the M1952 run.
4. PASS: old and new READS are compared on the same fixture, line by line, in order
   (`test_the_linear_worklist_walks_in_the_list_order`).
5. N.A.: no R8 binding; no field is read from a Lean answer.
6. PASS: the chain's gate runs on the committed final HEAD. m509-500.json is at 14d35d32b1, and later commits touch
   only docs/infra/tm-m509-reads-linear/.
7. PASS: DELTA.md has no rows and reserves no signature.
8. PASS: no product output changes. The only changed text is a test tool's UNKNOWN detail, which DELTA.md states.
9. PASS: `tools/select_tests.py --base a7659c5f12` selects `tests/test_trust_mutants_probe_scope.py` and
   `tests/test_trust_mutants.py`.
10. N.A.: no Lean statement or proof changed.
11. PASS: a timed-out probe stays UNKNOWN, never a kill
    (`test_a_probe_past_the_build_timeout_says_so_and_stays_unknown`). There is no new limit, and no sleep or wall
    deadline in the tests.
12. PASS: the M1952 timings above. If the List worklist comes back, the order test's `LIST_WORKLIST` assertions
    (`old.count(new) == 1`) fail.
13. N.A.: no test removed or renamed.
14. PASS: both directions are tested (a timeout gets the new text; a failure keeps the old one). Every claim above
    cites a command or file. Spec re-read: DO (1) "same lines in the same order", against the task file DO (1) and
    the order test; DO (2) "verdict stays UNKNOWN … one limit", against the task file DO (2) and `refusal`/`probe`.
15. PASS:
    - no overclaim: "same order" is shown by the order test; "stays UNKNOWN" by the timeout test;
    - no cut deliverable;
    - every new check can fail: seeds 1-3;
    - limits: --build-timeout is unchanged and charged as before (`Scratch.lake`).

SELF-REVIEW: 0 A, 2 B, 6 C; fixed 3.

The two B findings were this report's deliverables and the per-file probe timing; both are done above. The C fixed
was the `probe` docstring. The other C findings were left:

- the `" did not "` partition depends on `Scratch.lake`'s wording, in one module;
- the old test's local name `timed_out` (the controls have no limit);
- the nightly's cost note (in DO 3 above);
- `ours` in READS is still quadratic. It is out of scope, but it is the next candidate if probes are still slow.
