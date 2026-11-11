# sc-admit-cpu: `admitSD`'s Lean CPU on the large soft-chain documents, measured

## Method

- Machine: the VM, AMD EPYC 7B12, 32 vCPU, Linux 7.0.0-1014-gcp. Compiled Lean, leanprover/lean4:v4.24.0.
- Code: main at 5f756e791d (`lean/` tree ba59cfa973). The figures in "On main" are of that code.
- Requests: `admit_docs.py` (this directory) writes each document as a readings@1 request: `tests/test_readings_sd_lean.py`'s
  `env4()` environment (the vocabulary of `frame4`, `y_permitted` unspecified) and the units and reading sets of
  `NSDbig n g` and `withRules n m g` (docs/rd-9/sc-11w/cpu_bench.lean). The bench's `check` mode decodes each request and
  confirms that the decoded document's items, chain, couplings, narrowings, unspecified predicates and `sdSizeCharge`
  equal the Lean `NDoc` it restates. Every case printed `same as the Lean NDoc: true`.
- Bench: `admit_bench.lean` is the `main` of a throwaway Lake package that requires this worktree's `lean/`.
  `run_bench.sh <worktree> <dir> <case>...` builds it and runs `/usr/bin/time -f %U ./bench <mode> <request>`, one mode
  per process, three runs each. Modes:
  - `parse`: the floor (read and parse the request).
  - `s2`: `admitS2` (S1's and S2a's admission).
  - `admit`: `admitSD`, the whole admission. This is the figure R4 is checked against.
  - `sup`: `admitS2`, then `sup D` (what `readings-dead` builds).
  - `free`, `chain`, `nd`, `texts`: the parts of `admitSDOf` (used for the cost split below).
- Figures: user CPU of the whole process, which includes about 0.05-0.08 s of start-up and parsing (`parse`). The
  5-minute load was 15-24 (other worktrees' builds), printed before each case in the output files.
- Output: `output-main-step1.txt` (the three named documents), `output-main-wider.txt` (sc-11w's other documents) and
  `output-main-scaling.txt` (the scaling families).

## On main: the three named documents (step 1)

| Document | Choices | `sdSizeCharge` | `admitSD` | `admitSD` CPU | `admitS2` CPU | `parse` CPU |
| --- | --- | --- | --- | --- | --- | --- |
| NSDbig 6 | 64 | 703 | ok | 0.13, 0.12, 0.13 s | 0.09, 0.08, 0.09 s | 0.08, 0.08, 0.07 s |
| `wideGuard767` (`NSDbig 8 (wide 8)`) | over 64 | 20,375 | ok | 0.09, 0.09, 0.09 s | 0.07, 0.08, 0.07 s | 0.05, 0.08, 0.08 s |
| `wideGuard3071` (`NSDbig 6 (wide 10)`) | 64 | 59,033 | `ResourceLimit: generated norm layer layer:norms:x_required under rs0@1:0` (`admitS2`) | 0.06, 0.06, 0.07 s | 0.06, 0.06, 0.06 s | 0.08, 0.08, 0.08 s |

All three are within R4's 1 s:
- The 767-node document has more than 64 compatible choices, so `admitSDOf` runs no per-choice text
  (SoftWire.lean:53-54).
- The 3,071-node document is refused by S2a's admission, before `admitSDOf`. Its set 0's generated layer is over the
  layer limit.

## Does a live path evaluate `superposable` or `supU` on a soft-chain document?

No, on main at 5f756e791d. Every live entry into a document under the soft completion goes through
`underSoftCompletion` (SoftWire.lean:24) to `admitSDOf` (SoftWire.lean:41). The entries are:
- `runS2ND` (Run.lean:499-502);
- `validateOne` (Run.lean:546-547);
- `runOne`'s `readings-separate` (Run.lean:563-564);
- `runVerdictsD` (DefaultVerdicts.lean:495);
- `replayVerdictsSD`'s `admitSD` (SoftVerdicts.lean:77).

Neither `admitSDOf` nor these callers read `superposable`, `ndSuperposable`, `routeND`, `routeSD`, `sdSuperposable` or
`supU`:
- `admitSDOf` reads `ndTextWith`, `softShaped`, `choices` and `sdChoiceText` (SoftWire.lean:49-55).
- `runSDKind` (Run.lean:487-493) answers:
  - `readings-elaborate` with the enumerated row and the completion finding (Run.lean:449-458);
  - `readings-choice` with one choice's replay;
  - the superposed kinds with `sdRefusal`'s text (Run.lean:483-484).
- `routeOf true D` returns `.enumerated` on the soft chain before it reaches `superposable` (Route.lean:34-39, its
  third row).
- The split refuses a soft-completion case (`splitAdmissible`, ComponentsWire.lean:326-327).
- `routeND` and `ndSuperposable` (UnspecifiedWire.lean:594-601) are reached only under `underCompletion`, which is
  the norms chain (UnspecifiedWire.lean:41-42).
- `routeSD`/`sdSuperposable` are reached only from SoftSupWireExamples.lean (sc-11b switches the dispatch).

One live path builds `sup D` itself, though not `superposable` or `supU`: `readings-dead` (`deadAnswer`,
SupRun.lean:132-148). It calls `deadCheck`/`unsatCheck` (Superpose.lean:788-791), which read
`envAt (soften (correlate (sup D).1)) 0` when `supReady D`. Its cost on the documents admitted above (`sup` mode):
- NSDbig 6: 0.06-0.08 s.
- `wideGuard767`: 0.06-0.10 s.
- `wideGuard3071`: refused in `admitS2`.

## On main: admission over R4 on sc-11w's other documents

`admitSDOf` runs `sdChoiceText` on every compatible choice when there are at most 64 (SoftWire.lean:53-55). That is
the same per-choice text `routeSD`'s `sdChecked` reads (SoftSupWire.lean:91-93, row sc-11wc), but admission is live
today. On sc-11w's own documents it is over R4. Figures are from `output-main-wider.txt` and
`output-main-scaling.txt`, load 17-24:

| Document | Choices | `sdSizeCharge` | choices × charge | `admitSD` | `admitSD` CPU |
| --- | --- | --- | --- | --- | --- |
| NSDheavy (`withRules 6 10 (wide 4)`) | 64 | 14,703 | 940,992 | ok | 1.96, 1.88, 2.00 s |
| heavyIn (`withRules 6 9 (wide 4)`) | 64 | 12,880 | 824,320 | ok | 1.30, 1.32, 1.60 s |
| `withRules 6 16 (wide 4)` | 64 | 27,615 | 1,767,360 | ok | 2.78, 2.28, 2.47 s |
| `withRules 6 8 (wide 4)` | 64 | 11,151 | 713,664 | ok | 1.02, 1.13, 1.63 s |
| `withRules 6 4 (wide 4)` | 64 | 5,175 | 331,200 | ok | 1.09, 0.87, 0.93 s |
| `withRules 6 32 (fun _ => .top)` | 64 | 3,519 | 225,216 | ok | 2.56, 2.68, 2.40 s |
| `withRules 6 16 (fun _ => .top)` | 64 | 1,855 | 118,720 | ok | 0.83, 0.68, 0.50 s |
| `withRules 6 9 (wide 2)` | 64 | 3,808 | 243,712 | ok | 0.74, 0.67, 0.60 s |
| `withRules 6 2 (wide 4)` | 64 | 2,751 | 176,064 | ok | 0.55, 0.60, 0.54 s |
| `withRules 6 1 (wide 4)` | 64 | 1,680 | 107,520 | ok | 0.34, 0.54, 0.51 s |
| `withRules 6 9 (wide 0)` | 64 | 1,540 | 98,560 | ok | 0.47, 0.40, 0.48 s |
| `withRules 6 9 (fun _ => .top)` | 64 | 1,288 | 82,432 | ok | 0.26, 0.23, 0.24 s |
| `wideGuard191` (`NSDbig 8 (wide 6)`) | over 64 | 5,975 | (no per-choice text) | ok | 0.11, 0.11, 0.07 s |
| NSDbig 8 | over 64 | 1,225 | (no per-choice text) | ok | 0.09, 0.09, 0.11 s |

Cost split on NSDheavy, one run each at load 23:
- `admitS2` 0.14 s.
- `ndTextWith` (free and reading documents) about 0.02 s.
- The 64 per-choice texts 1.17 s:
  - `choiceChainText` (S2a's chain text on each choice): 0.95 s.
  - `WellFormedU (choiceU N c)` with its author checks: 0.35 s.

The per-choice text cost grows with choices × `sdSizeCharge` (sc-11w's measure), but not in proportion to it:
- From about 1.1 µs per unit on wide-guard rules to about 11 µs per unit on 32 one-node rules.
- The per-choice chain text grows about with the square of the number of fixed rules: 16 rules 0.5-0.8 s, 32 rules
  2.4-2.7 s.

These documents are over R4 through a live admission, so step 2 applies (DRI 2026-11-11 sc-admit-cpu item 1).

## The limit: `maxSdAdmitWork` = 131,072

The DRI's provisional value was 524,288 (item 3), lowered to the next power of two while an admitted 64-choice
document was over 1 s:
- 524,288 admits `withRules 6 4 (wide 4)` (331,200 units, 0.87-1.09 s) and 32 one-node rules (225,216 units,
  2.40-2.68 s).
- 262,144 still admits the 32-rule document.
- 131,072 admits the 64-choice documents at or just under it within 1 s:
  - `atLimit`, below, 0.57-0.61 s;
  - 16 one-node rules (118,720 units), 0.50-0.83 s;
  - one 31-node rule (107,520 units), 0.34-0.54 s.
- 131,072 refuses every 64-choice document measured over 1 s.
- It also refuses a few documents that were within 1 s, for example `withRules 6 2 (wide 4)` (176,064 units,
  0.54-0.60 s). That is the conservative direction.

## With the charge (step 2), at ba8900650b's parent 5cfea74ca9

Output: `output-charged.txt`, at the 5-minute load printed before each case (27-41). The `lean/` tree differs from the
final one only in SoftWireExamples.lean's last `#guard` and the generated files.

| Document | Choices | `sdAdmitWork` | `admitSD` | `admitSD` CPU |
| --- | --- | --- | --- | --- |
| NSDheavy | 64 | 940,992 | `ResourceLimit: the per-reading checks of 64 readings exceed 131072 units` | 0.23, 0.22, 0.22 s |
| heavyIn | 64 | 824,320 | the same refusal | 0.23, 0.20, 0.21 s |
| `atLimit` (`NSDbig 6`, 13 rules of 2-3 nodes) | 64 | 131,072 | ok | 0.57, 0.61, 0.61 s |
| `overLimit` (one node more) | 64 | 133,120 | the same refusal | 0.21, 0.23, 0.22 s |
| NSDbig 6 | 64 | 44,992 | ok | 0.15, 0.18, 0.17 s |
| `wideGuard767` | over 64 | (not read) | ok | 0.09, 0.09, 0.08 s |
| `wideGuard3071` | 64 | (not reached) | `admitS2`'s `ResourceLimit` | 0.07, 0.08, 0.07 s |

## Open: documents with many fixed rules (reported to the DRI)

The charge bounds the per-choice texts on the documents above. It does not bound two other costs, both of which grow
with the number of fixed rules faster than `sdSizeCharge` does:
- `admitS2`, S1's and S2a's admission, which runs before `admitSDOf`;
- the per-choice texts when there are few choices.

Output: `output-gap.txt` (at ba8900650b, load 16-24) and `output-charged.txt`.

| Document | Choices | `sdAdmitWork` | `admitS2` CPU | `admitSD` CPU |
| --- | --- | --- | --- | --- |
| `withRules 1 32 (.top)` | 2 | 2,808 | 0.50, 0.49, 0.48 s | 0.59, 0.56, 0.57 s |
| `withRules 3 28 (.top)` | 8 | 14,288 | 0.45, 0.47, 0.45 s | 0.52, 0.54, 0.54 s |
| `withRules 3 32 (.top)` | 8 | 17,136 | 0.86, 0.79, 0.76 s | 1.46, 0.83, 0.83 s |
| `withRules 5 28 (.top)` | 32 | 83,072 | 0.72, 0.75, 0.75 s | 1.62, 0.95, 0.97 s |
| `withRules 4 30 (.top)` | 16 | 37,840 | 1.32, 1.37, 1.34 s | 1.63, 1.61, 1.54 s |
| `withRules 1 64 (.top)` | 2 | 9,656 | 6.50, 7.14, 9.19 s | 9.25, 10.34, 9.19 s |
| `withRules 1 128 (.top)` | 2 | (not reached) | 54.41, 55.60, 55.02 s, then `ResourceLimit: generated norm layer …` | (not timed) |

Lowering `maxSdAdmitWork` cannot close this gap. `admitS2` is over R4 before the charge is read, and 32,768 would
already refuse the named NSDbig 6 (44,992). The fix is a rule-count bound or a cheaper chain check in S1's and S2a's
admission and `choiceChainText`. That is outside this item's files. It is reported to the DRI in REPORT.md
("Notes for the DRI").
