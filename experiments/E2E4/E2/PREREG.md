Status: DRAFT — 2026-09-21; scored run deferred today: size-256 prompts reach ~40k tokens and exceed judge context.
# E2 revision 2: proof length, remaining evidence, and checker visibility

Draft amendment; **no live model calls in this revision**. The earlier pilot was
at floor for BAD items, so the revised materials require a new dev-only pilot.
E2 remains a mechanism demonstration unless VE differs from matched structured
FOL with the same checker findings and evidence. Do not attribute a generic
checker advantage to VE language. Judge IDs and repetitions remain to be frozen.

## Colab DEV output budget (not a scored freeze)

max_new_tokens: 400

The offline exporter reads this cap; the DEV ladder uses temperature 0, seed 0,
one response per item/cell, and an 8192-token context including the response.
The three judges are Qwen2.5-7B-Instruct, 14B-Instruct-AWQ and 32B-Instruct-AWQ.
Export all sizes/workloads without truncation or exclusion. The exact-token
preflight refuses a job if any assigned prompt plus the cap exceeds context;
large E2 assignments may require a separately reviewed larger-context run.
Whitespace counts do not establish token fit or L4 memory fit. Scored export
requires this file to begin `Status: FROZEN` and equal HEAD byte for byte.
This DEV budget does not freeze scored settings or change the primary analysis.

## Primary contrast

Per judge, the paired interaction (FA_VE,256 − FA_VE,4) −
(FA_direct,256 − FA_direct,4), negative favoring VE. Report it separately for
fixed and growing evidence workloads and for checker-visible versus invisible
errors; the combined balanced-error estimate is secondary. The VE versus
structured-FOL interaction is the language-specific comparison. Size 32 is an
intermediate descriptive point. Failure/unparseable/timeout trials remain in
assigned denominators: approval for BAD, rejection for GOOD; report their rates.

## Refutation condition

An interval entirely above zero rules out a scaling advantage in that setting.
Intervals covering both benefit and harm are inconclusive. Without a feasible,
dev-based precision calculation, no useful-size superiority/refutation claim is
made. A VE/direct difference without a VE/FOL difference supports only the
checker/display mechanism. Near-zero BAD approval precludes identification.

## Honest-acceptance constraint

Report GOOD acceptance at each size and workload. A protection claim also requires
its lower paired 95% honest-acceptance bound relative to direct to be ≥−.05.
Failure to establish that condition does not demonstrate harm. Size-dependent
losses of GOOD acceptance remain outcomes even when BAD approval is at floor.

## Smallest useful effect

No confirmatory useful-size effect is frozen by this small template inventory.
The old 10-point threshold lacked a supported power calculation. Estimate dev
cluster variance and freeze an attainable effect, expanded inventory if needed,
judge IDs and repetitions before scored calls; otherwise report a pilot only.
Repetitions reduce within-item noise, not uncertainty over eight scored templates.

## Capability gate

Use only dev: response parseability ≥90%, direct balanced accuracy ≥60% at size 4,
and BAD approval away from floor/ceiling (target .20–.60) in a selected larger-size
workload. Record failures of the gate and all attempted ladder judges. Do not claim
this range has been attained without calls. Select settings and freeze the run
manifest before scoring; do not optimize a size interaction on scored results.

## Sample size

432 items: 144 dev, 288 scored. There are four dev and **eight scored distinct
inference-shape templates**, each with two vocabulary families disjoint across
splits. Each template × vocabulary × workload × size has one honest item, one
invalid-step item and one invisible-error item. Workloads are fixed/growing;
sizes are 4/32/256. Overall there are 144 honest, 144 invalid-step, 72 false-leaf
and 72 wrong-specification items. Exactly half of error-bearing items have an
error the logical checker cannot see, within every size and workload. Full scored
crossing is 288 × 3 cells = 864 calls per judge per sample, before any selection.

Templates vary nesting, mixed clauses, shared clauses, extensions and parallel
clauses. Every family gets fresh synthetic predicate names, not just a new
registrar. Invalid intermediate steps strictly strengthen the current fact while
using exactly the same word multiset (including connective and predicate counts) as
the corresponding honest step. Invalid positions are seeded among nonfinal steps. Subsequent
steps return to the faithful form, yielding exactly one checked gap. All local
positive certificates and all negative witnesses are replayed; sources and
adjacent links are checked against their certificate packages.

Half the items have a fixed two-leaf workload. In the other half, each nonfinal
step additionally establishes a predicate of a newly named work-unit object
from a new cited record. There are size+1 leaf obligations (5, 33, 257). Those
claims are required for the submitted intermediate steps, although the final
root can omit the auxiliary facts. Thus both checked prompts carry growing
leaf statements, citations, records and remaining-premise lists—not merely a
size integer. This creates real opportunities to overlook evidence or misuse
a long outstanding-obligation list. It is still synthetic intermediate work,
not a claim about every form of real-world problem growth.

Structured-FOL converts **every formula-bearing field**, including records,
leaf lists, root, unresolved deductions and checker obligation sources, to the
FOL-keyword view. VE and FOL have equal semantic information; their strings and
lengths necessarily differ. Countermodels remain the same extensional data.

## Analysis and interpretation

Pair item conditions and sizes before computing differences, then average within
structural templates, retaining both vocabularies/workloads as paired variants.
Use `experiments.cluster_stats.cluster_t` with df K−1, K=8 scored templates, on
the directly computed interaction; never subtract unrelated CI endpoints or
resample individual trials. With eight clusters, t intervals still depend on
approximate normality and independent templates and can be fragile. Label this
limitation and do not present it as broad population precision.

The 256-step sequence exceeds one core argument package's claim-count envelope.
Local inferences and every boundary are certified; the aggregate link audit is
experiment code and is labeled as such. No single 256-step core composition
certificate is claimed. Report every judge separately, including actual context
limits and assigned failures; no pooling across judge families. Freeze any
additional scored templates before inspecting scored effects.
