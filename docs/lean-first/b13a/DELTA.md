# Batch 13a A/B delta

Base `7345e3ed`; comparison target: this batch's head. The machine-readable
allowlist is [`DELTA.json`](DELTA.json). `tools/lean_first_diff.py compare`
checked 94,489 public records across the conformance, Stage-0 probe, quantity,
rights, discourse, readings and historical-pilot cohorts. 94,440 records were
identical. The 49 differences are all diagnostic **wording**, represented by
16 exact before/after pairs in `DELTA.json`: the Lean answer carries its
diagnostic code prefix, followed by the same message that Python supplied.
There are zero order, verdict, identity, count, or availability changes and
zero unlisted differences. All 294 pilot records are identical.

The DRI's 2026-10-04 answer 3 to the Lean-first plan signs the policy for this
wording block: Lean texts are canonical, and Python's better messages move into
Lean. The block contains precisely that transfer. Exact pair review remains a
HUMAN item for the DRI; this document does not claim a new DRI signature.

The full A/B comparison is in [`evidence/corpus-ab.json`](evidence/corpus-ab.json).
The paired 15-run differential-fuzzer comparison is in
[`evidence/difffuzz-ab.json`](evidence/difffuzz-ab.json): the reviewed baseline
stays at 357, with no head-only signature or unreviewed finding. The service
latency samples are in [`evidence/latency-ab.json`](evidence/latency-ab.json).
Five paired samples of 100 calls per operation kept the largest median CPU
change below 20%; the slowest head p95 was 1.732 ms and every head median CPU
was below 0.49 ms.
