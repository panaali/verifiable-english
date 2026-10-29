NEAR-LINEAR REACHABLE: yes (`filledAdmission` and `admitS2`; projected 185 KB admission 15–25 CPU s at UDHR density).
Status: measurement complete; the real 185,033-byte constitution's `runCase` median is 1.29 CPU s (three runs).
HEAD: this report is committed on `infra/scale-admission-profile`; baseline `471ccc7e4`.
Changed: opt-in Lean admission timings, reproducible UDHR and constitution inputs, CPU evidence and fits.
Open: the 4× UDHR is refused at the vocabulary limit; the chain runs the release gate. No DRI signature is needed.

# Readings admission profile, 2026-10-29

## Decision

The superlinear work is in the filled-document admission (`admitDecoded` called by
`admitNDFull`) and the preceding `admitS2` checks. On the controlled three-main-set
prefixes, their fitted exponents against norm count are 2.47 and 2.93 respectively.
The complete distinguishing-model checks are small in these cases (0.02–0.03 CPU s)
but their current validation scans the full author vocabulary for every model.
The 64-choice whole UDHR also pays for `choiceStepText` once per compatible choice.

A near-linear implementation can build indexes once per admission: rule name and
predicate to norms, predicate to units that use it, and set to candidate units;
validate the complete model's declared tables once, then evaluate each model only
against the units whose predicates it uses. Reuse the filled frame and derived
norm layers across the checks of those units and across compatible choices. This
changes work order and lookup cost; every candidate, rule, choice and model check
still runs and every answer must remain byte-identical. The expected exponent is
about 1.0–1.2 for a bounded choice count. The low-density 13- and 19-norm runs
cost 0.49 and 0.68 CPU s per ordinary `runCase` on 5,545 and 8,260 source bytes;
linear scaling of their per-byte costs to 185 KB is 15.2–16.4 s. Allowing for
larger indexes and fixed overhead gives a **15–25 CPU s projection** for an
admissible UDHR-density 185 KB input. This is a proposed fix target, not a
measured result. The real constitution is already under the 30 s admission target
at its actual density: 64 predicates, 16 norm-kind units, two reading sets and
1,132 units; its ordinary `runCase` stage took 1.29 CPU s median. Source bytes
alone are therefore a poor cost predictor.

The 4× UDHR has 520 units and 28 independently named companion sets after
replication; Lean refuses it with `ResourceLimit: vocabulary size` before a
complete admission. The 2× version is admitted (260 units, 14 companion sets).
The vocabulary cap is a separate constraint for dense documents. It does not
block the measured constitution, whose 64 predicates are fewer than the UDHR's 89.
The next infra row should be **scale-linear-admission: index norms and reuse
filled checks across readings admission**. If a future document exceeds the
vocabulary cap, it also needs a limit decision or the parts-plus-interface design.

## Method and inputs

`VE_READINGS_STAGE_TIMES=1` makes `ve_service` write one JSON line per stage to
stderr using `IO.monoNanosNow`. Each line also carries process CPU ticks from
`/proc/self/stat` on this VM (100 ticks/s), status, part, case and item count.
The default and `=0` write nothing, and stdout is unchanged. The hook executes
separate pure probes for each stage, then the ordinary `runCase`; the sampled
stage costs overlap and **must not be added** to estimate one admission.
`runCase` is the normal route's cost within the profiled process. Process CPU
also includes parsing, the duplicate probes and JSON output.

Inputs are saved in `inputs/` from the scale review's 50%, 75% and 100% UDHR
prefixes and the 2026-10-29 06Z constitution pilot. The 100% prefix is the
whole UDHR. `admission_cases.py` builds each direct `readings-elaborate` case;
it repeats article units and renames predicates, constants, rules, unit IDs and
set IDs for the synthetic 2× and 4× cases. Each replica's companion keeps its
own complete model, and the generator rebinds its situation ID to Lean's split
environment. Main sets in synthetic cases are fixed to their first reading:
their original whole-vocabulary distinguishing models would otherwise be
incomplete after adding predicates. The 31-norm controlled case likewise fixes
four extra main sets, leaving three main sets and eight choices, as in the
13- and 19-norm prefixes. This preserves their norm content while controlling
choice count; the whole UDHR row retains its 64 choices. The 4× refusal is
measured as a refusal, not as an admission time.

Each case ran in a fresh Lean service process three times. `measure_admission.py`
first called `zsh /home/seyran/code/manage-agents/iso.sh exp-scale-admission 24G -- …`.
This VM's user systemd bus returned `Failed to connect to bus: No data available`
before every attempt; the script used the same service at `nice -n 15` and saved
that failure in every run. The one-minute VM load was 28.63–57.16 on 32 vCPUs;
it exceeded 32 for several runs, especially the 4× refusal and the constitution.
The CPU figures below are retained; wall timings under that load are not used for
the fits. The evidence JSON records all repeats, load, status, stage ticks,
service SHA-256 and exact request hashes.

| Input | Source bytes | Units | Norm-kind units | Sets | Ordinary `runCase` CPU s, median | Process CPU s, median | Outcome |
|---|---:|---:|---:|---:|---:|---:|---|
| UDHR 50% | 5,545 | 64 | 13 | 7 | 0.49 | 1.82 | admitted |
| UDHR 75% | 8,260 | 101 | 19 | 9 | 0.68 | 2.51 | admitted |
| UDHR 100%, three main sets | 10,916 | 130 | 31 | 10 | 2.90 | 11.14 | admitted, eight main choices |
| Whole UDHR | 10,916 | 130 | 31 | 14 | 3.54 | 12.79 | admitted, 64 main choices |
| Synthetic 2× UDHR | 21,832 | 260 | 62 | 14 | 13.33 | 29.57 | admitted; main sets fixed |
| Synthetic 4× UDHR | 43,664 | 520 | 124 | 28 | 0.04 refusal path | 0.44 | `ResourceLimit: vocabulary size` |
| Constitution pilot | 185,033 | 1,132 | 16 | 2 | 1.29 | 4.89 | admitted |

The stage table uses the three controlled UDHR prefixes. Entries are medians
of three runs in CPU seconds, summed over the stage's calls in each run before
taking the median. The exponent is ordinary least squares on log(stage CPU)
against log(norm-kind unit count) at 13, 19 and 31; it is descriptive because
unit and companion counts also change. CPU ticks are 0.01 s, so the splitCase
exponent cannot be resolved.

| Stage | 13 norms | 19 norms | 31 norms, 3 main sets | Fitted exponent | Code path |
|---|---:|---:|---:|---:|---|
| `splitCase` | <0.01 | 0.01 | 0.01 | unresolved | `Companions.splitCase` |
| `admitS2` | 0.02 | 0.03 | 0.24 | 2.93 | `SupWire.admitS2` → `Wire.admitReadings` |
| `admitNDFull` | 0.34 | 0.48 | 2.31 | 2.25 | `UnspecifiedWire.admitNDFull` |
| `filledAdmission` (inside previous row) | 0.28 | 0.41 | 2.29 | 2.47 | `Wire.admitDecoded` on `fillDoc N` |
| `choiceStepText` (inside `admitNDFull`) | 0.06 | 0.08 | 0.15 | 1.07 | each complete choice checks the filled document |
| `ndTextWith` (inside `admitNDFull`) | 0.01 | 0.01 | 0.03 | 1.31 | each active reading's document |
| `distinguishingModels` | 0.02 | 0.02 | 0.03 | 0.48 | `setPairsWith`, each set's complete models |
| Ordinary `runCase` | 0.49 | 0.68 | 2.90 | 2.09 | actual route dispatch and admission |

`filledAdmission` validates a filled document again. In `Wire.frontText`,
`duplicateText` checks each item against `D.items.take k` and scans earlier
names; `interfaceText` loops over sets then items; `frameWF` scans all sets and
attachments. In `SoftNorms.Once.checkSoftOnce`, loops over every norm call
`checkSoftRule` and `derivedList` on the whole document; `softSemanticCheckOnce`
also loops nodes with `sortsOf D N.pred` (a linear regulated-list lookup) and
constructs `collidingPairs`. Those nested scans explain the superlinear
`filledAdmission` and `admitS2` fits. `choiceStepText` loops over compatible
choices and calls `choiceChainText (fillDoc N)` and `ndChoiceText` for each;
whole-UDHR CPU for that substage is 0.64 s versus 0.15 s with three main sets.
For every distinguishing model, `replayPair` checks its base against
`authorVocabulary` and then the pair's sides. Its current cost is small in
these inputs, but a predicate-to-unit index would prevent repeated irrelevant
unit checks as model and document counts grow.

## Evidence and acceptance

| Item | Owner | Evidence |
|---|---|---|
| Env-gated Lean stage timings, silent by default and same answer | AGENT | `test_readings_stage_times.py`; three seeded failures below |
| UDHR prefixes, whole UDHR, synthetic 2×/4×, three CPU repeats and load | AGENT | `admission-profile-evidence.json`, `admission-profile-controlled.json`; generator and runner in this directory |
| Direct 185 KB target | AGENT | `admission-profile-constitution.json`; saved source under `inputs/` |
| Fits, cause, reachable decision and no-answer-change fix direction | AGENT | stage table above; source paths named above |
| Final release gate on committed HEAD | EXTERNAL | deferred to the chain, as directed by the task |

The hook changes no route verdict, diagnostic, schema or response bytes.
`test_readings_stage_times_do_not_change_the_answer` compares the two stdout
responses, and the environment-unset test checks silent stderr. No model API
calls, full suite, or release gate were run for this report. The selected
test run and final build evidence are in the build report. The saved evidence is data, with no permanent test that diffs
a moving Git HEAD.

## Seeded bugs

Each temporary code fault was removed before the final build.

| Changed product file and planted fault | Failing test |
|---|---|
| `lean/VE/Service/ReadingsAdmissionProfile.lean` (formerly `lean/VE/Readings/AdmissionProfile.lean`): gate on `=0` instead of `=1` | `test_readings_stage_times_are_silent_by_default` |
| `lean/VE/Service/ReadingsAdmissionProfile.lean` (formerly `lean/VE/Readings/AdmissionProfile.lean`): emit `splitCaseWrong` | `test_readings_stage_times_are_json_lines_for_each_stage` |
| `lean/Serve.lean`: replace the answer line with JSON `null` | `test_readings_stage_times_do_not_change_the_answer` (after strengthening its expected-response assertion) |
