# kb-10e: prepared soft documents — build report

No DRI signature needed: every DELTA row cites a standing ruling (R16, R3, R8, R2, R12). The kernel growth is
under the architect seat's signed allowance (`docs/kernel/ALLOWANCES.md`).

Kernel 9,552 to 9,560 lines (+8, allowance +60). Lines added to `lean/VE/Service/Protocol.lean`: 219 (26
removed), which the measure does not count. Trust K +0, S +0, V +5 (R16). A repeat `soft-selected` call on a
registered Preparedness document takes 2.1 ms median in the service (7.0 ms through the relay). A first call takes
114.5 ms (111.7 ms through the relay). The targets were at most 80 ms and at most 500 ms. The five frozen keys are
unchanged.

SIZE: 591 product (Lean 532, Python 59), 200 tests, about 880 other hand-written lines (bench and trace scripts,
tables, DELTA, this report, seeded bugs, allow file, ALLOWANCES, kernel-paths, layer_policy).

## Commits (`git log --oneline main..HEAD --no-merges`, saved here)

| Commit | Part |
|---|---|
| 9b7401559d | (1) measure the soft-selected stages before the change: `bench.py`, captured cases, tables |
| e6b79b081b | (2) `Prepared`, `prepare`, `runSelectedP`; `prepare_ok`, `runSelected_eq_prepared`, `soft_wire_selected_prepared` |
| 679ce8c726 | (3) soft-document handles in the service table, answered from the prepared entry (`softResult_cached`) |
| 23833cce1b | (4) the client sends soft-selected cases by handle; handshake `soft_member`; kernel registry and allowance; regenerated files |
| 120b6538bd | (5) `prepareDocument_ok`; trust classes, baseline row (R16), regenerated files |
| 7b36e2d951 | after-change timings, registration trace of a Preparedness run, seeded bugs |
| 50b45e7902 | trust mutants (`--deep`): 24 KILLED, 21 ALLOWED |
| f4b2a61cb1 | the fake service's handshake states `soft_member`; `test_handshake` and the handshake fuzz |
| 3a31727ba4 | DELTA |
| 2025551d10 | the code map, regenerated after the merge with main (c9214a2608, merge b9724f0628) |
| 6383f22a93 | (11) REPORT |
| 46d87523a0 | (12) the kernel figures quoted in kernel-boundary.md and frozen-keys; the wire gate's test inputs |
| 2521eefcf9 | (13) REPORT: the final selected run |

## (1) Measure: the stages before the change

`uv run python docs/kernel/kb-10e/bench.py <case> --reps 5` under
`zsh manage-agents/iso.sh kb10e-bench 8G --`. The script talks to `lean/.lake/build/bin/ve_service` with the
request lines `ve/backends/lean_service.py` writes, on one process. Each variant cuts the runner after one stage, so
the difference of two medians is one stage. Cases: `docs/kernel/kb-10e/cases/*.json`, captured by wrapping
`ve.soft_route._run` during the harnesses' `soft-selected` calls. The script's docstring says how. Saved tables:
`before-pf-case-1.md` and `before-rsp-case-1.md`, run on main's binary (9a3fd7a9f9, saved as
`/tmp/kb10e-ve_service-before`).

| stage (median of 5, wall ms) | Preparedness pf-case-1 | RSP rsp-case-1 | stage cost pf / RSP |
|---|---:|---:|---|
| request parse (a bad kind) | 7.8 | 8.5 | 8 / 9 |
| `decodeSoftSource` (no model) | 80.6 | 103.0 | 73 / 95 |
| `primeModelVocabulary` (a model that fails to decode) | 479.9 | 593.9 | **399 / 491** |
| model decode, query check (no query) | 492.3 | 616.2 | 12 / 22 |
| `expanded` + `classificationBackgroundValid` + first query | 703.4 | 822.7 | **211 / 207** |
| the captured queries (9 / 8) | 714.4 | 871.7 | 11 / 49 |
| 200 queries | 718.7 | 903.1 | under 0.2 per query |

About 680 of the 700 ms are per document: the vocabulary and the expansion. The assumed cause holds. The bodies
recompute `soften D` and its derived values. `primeModelVocabulary` and `expanded` each soften the document
again. `expanded`'s `expList` recomputes the layer order once per layer symbol, and `selects'` softens the
document once per rule. With them shared (`prepareFrom`: `soften` once, `syms` once, the layer table once),
everything after `decodeSoftSource` costs 9 ms (pf) and 22 ms (RSP) on the first call. See the next table.

## (ii) The stages after the change

`bench.py <case> --reps 5 --handle` on this branch's binary (`after-pf-case-1.md`, `after-rsp-case-1.md`). The
machine was loaded (load average about 50) when these tables were taken. So main's binary was rerun right
afterwards under the same load (`before-*-sameload.md`). The written-out path computes what it did on main: its
figures match main's binary under the same load (one query: 987 against 980 ms pf, 1,007 against 1,142 ms RSP).

| variant (median of 5, wall ms) | pf-case-1 | rsp-case-1 | main's binary, same load: pf / RSP |
|---|---:|---:|---|
| written out, 1 query | 987.4 | 1006.9 | 979.8 / 1142.4 |
| written out, captured queries | 949.2 | 1024.4 | 1013.9 / 1153.5 |
| **handle: first call** (registers the document, fresh process) | **114.5** | **135.1** | (written out: about 1,000) |
| handle: first call, the process holding another document | 130.2 | 128.1 | |
| **handle: repeat call** (captured queries) | **2.1** | **1.7** | |
| handle: repeat call, 1 query | 1.3 | 1.0 | |

Targets: repeat call at most 80 ms median, met (2.1 ms). First call at most 500 ms, met (114.5 ms). What remains
of a first call is `decodeSoftSource`, about 95 to 105 ms of the 115 to 135.

Through the relay (`uv run python docs/kernel/kb-10e/bench_relay.py cases/pf-case-1.json cases/rsp-case-1.json
cases/pf-case-2.json --reps 5`: `relay.decide`'s path, `LeanServicePool.run_bound`, schema and binding checks
included):

| relay, pf-case-1, median of 5 | first call ms | repeat call ms |
|---|---:|---:|
| soft-document handle | 111.7 | 7.0 |
| written out (`handles=False`) | 787.7 | 860.7 |

### Which process holds a document

The pool hands a call to any idle process, and each process registers the documents of the calls it answers.
Measured with `bench_relay.py`: 20 calls over 3 documents, alternating, on a pool of 2.

- One caller, one call after another: registrations per process `[0, 3]`. A sequential caller always finds the
  same process idle, so each document is registered once, which is what document-to-process routing would give.
- Two threads: `[3, 3]`, each document registered once per process.

A registration costs about 105 ms more than a repeat call. With `N` processes busy at once, registering in each
costs at most `(N − 1) × 105` ms per document. Routing a document's cases to one process would save that, but it
would queue them behind that process while others are idle. The harnesses call one after another, so for them the
two choices make the same registrations. I kept "registered in each": nothing to route, and no queueing. Speed only;
answers are the same either way (`softResult_cached`).

## Estimate: the Preparedness harness after kb-10b switches

From the measured figures, 1,125 first calls and 5,241 repeat calls:

- service only: 1,125 × 114.5 ms + 5,241 × 2.1 ms = 128.8 s + 11.0 s, about **140 s (2.3 min)**;
- through the relay: 1,125 × 111.7 ms + 5,241 × 7.0 ms = 125.7 s + 36.7 s, about **162 s (2.7 min)**;
- with the registrations the present table bound gives in pair order (1,381, next section), through the relay:
  1,381 × 111.7 ms + 4,985 × 7.0 ms, about **189 s (3.2 min)**.

The written-out path's figure was about 83 minutes (6,366 × about 780 ms).

## Registrations under `maxHandles` = 64 (emptied when full)

I traced a Preparedness run (`usecases/openai-preparedness/run.py --check`, exit 0, 27 min) with kb-10b's
read-only wrappers (`usecases/safetyfw_shadow.py` from feature/kb-10b, d2c5ca76d4) and the Lean comparison skipped.
Script: `docs/kernel/kb-10e/trace_order.py`. Saved order: `registration-trace.json`, 1,125 documents with their text
sizes and the 6,366 (document, model) pairs in first-call order, the order kb-10b's shadow asks Lean in. Simulated
with `registrations.py`; output in `registrations.txt`. Document texts: median 40,396 bytes, 44.9 MB in all, so
the 64 MiB byte bound is never reached below 1,024 entries.

| order | rule, bound | registrations | per document |
|---|---|---:|---:|
| pair order (6,366 asks) | **present: empty when full, 64** | **1,381** | **1.23** |
| pair order | empty when full, 256 | 1,200 | 1.07 |
| pair order | least recently used, 64 | 1,275 | 1.13 |
| pair order | least recently used, 256 | 1,125 | 1.00 |
| call order (167,364 asks, one per harness call) | present: empty when full, 64 | 2,294 | 2.04 |
| call order | least recently used, 256 | 1,528 | 1.36 |

In the pair order kb-10b uses, the present rule makes 1.23 registrations per document. That is under 1.5, so I
propose no change. If a later switch asks Lean once per harness call rather than once per pair, the present rule
makes 2.04 per document (about 1,169 × 105 ms ≈ 2 min more). Evicting the least recently used of 256 would make
1.36. That proposal is for the architect seat, and only for that case. `maxHandles` and the emptying rule are
unchanged.

## (2) Pure part: `lean/VE/SoftNorms/Prepared.lean`

`structure Prepared` (`src`, `softened`, `layers`, `vocabulary`, `expanded`, `background`); `prepareFrom`,
`prepare`, `decodeModelIn`, `runSelectedP` (reads only `model` and `queries` of the case), `runCaseReportedP`.
The faster computations are new definitions proved equal to the existing ones: `vocabularyIn_eq`,
`expandedIn_eq`, `backgroundIn_valid`, `decodeModelIn_prime`. No body of a definition that a listed theorem
mentions changed: `tools/kernel_closure.py` shows every existing module of the softNorms path with the same spec
lines (Selected 15, SelectedSound 15). The only addition is `VE.SoftNorms.Prepared` +8. In `Selected.lean`,
`runSelected`'s query block moved into `selectedQueries`, with `selectedQueries_ok`. `soft_wire_selected`'s
statement is byte-identical: `lean/statements.txt` against main has 0 removed lines and 27 added theorems.

Statements, verbatim:

```lean
-- lean/VE/SoftNorms/Prepared.lean:181, (a)
theorem runSelected_eq_prepared (id : String) (j : Json) :
    runSelected id j = (do
      let e ← j.getObjVal? "environment"
      let p ← prepare e (j.getObjValD "norms")
      runSelectedP p id j)

-- lean/VE/SoftNorms/Prepared.lean:137, (b)
theorem prepare_ok {e n : Json} {p : Prepared} (h : prepare e n = .ok p) :
    decodeSoftSource e n = .ok p.src ∧ p.softened = soften p.src.D ∧ p.layers = syms (soften p.src.D).T ∧
      p.vocabulary = primeModelVocabulary p.src.se p.src.D ∧ p.expanded = expanded p.src.D ∧
      p.background = VE.Norms.backgroundBase (soften p.src.D) ++ excPremises p.src.D

-- lean/VE/SoftNorms/Prepared.lean:200, (c)
theorem soft_wire_selected_prepared (e n : Json) (p : Prepared) (id : String) (j answer : Json)
    (hp : prepare e n = .ok p) (h : runSelectedP p id j = .ok answer) :
    ∃ (src : SoftSource) (M : VE.FiniteModel VE.Bridge.Entity)
      (hM : M.Valid (envAt (soften src.D) 0)) (raws : Array Json) (qs : List SelectedQuery),
      decodeSoftSource e n = .ok src ∧
      decodeModel src j = .ok ⟨M, hM⟩ ∧
      j.getObjValD "queries" = Json.arr raws ∧ raws.toList ≠ [] ∧
      qs.length = raws.size ∧ (∀ x ∈ raws.toList.zip qs, QueryDecoded src.D M x.1 x.2) ∧
      SelectedAnswer id src.D M qs answer

-- lean/VE/SoftNorms/Prepared.lean:246: the reported answer, stated on VE.SoftNorms.Run.runCaseReported
theorem runCaseReportedP_eq (e n j : Json) (he : j.getObjVal? "environment" = .ok e)
    (hn : j.getObjValD "norms" = n) : runCaseReportedP (prepare e n) j = runCaseReported j
```

`background` is held as the formula list `backgroundBase (soften D) ++ excPremises D`. Its evaluation under a model
equals `classificationBackgroundValid D M` (`backgroundIn_valid`).

## (3) Service: `lean/VE/Service/Protocol.lean`, section "Environment handles"

A soft document is registered the way an environment is. Its text `{"environment": …, "norms": …}` goes in the
request's `environments` member under its SHA-256, and `registerOne` refuses a key that is not the SHA-256 of its
text, as before. It shares the table, the bounds and the emptying rule. `Entry` gains `soft : Thunk (Except String
Prepared)` with `soft_eq : soft.get = prepareDocument environment`, so the prepared document is replaced or dropped
exactly with its handle. A `soft-norms` request runs through `runSoftRequest` (`runSoftRequest_ok`: the same checks,
expansion and response as `runRequest`, each result `softResult`'s).

```lean
-- Protocol.lean:1206: the point of the item
theorem softResult_cached (h : Handles) (i : Nat) (kvs : Std.TreeMap.Raw String Json compare) (d : String)
    (entry : Entry) (hd : (Json.obj kvs).getObjVal? softHandleKey = .ok (.str d))
    (ht : h.table[d]? = some entry) (hw : kvs.WF) :
    softResult h i (.ok (.obj kvs)) (.ok (softExpanded kvs entry.environment)) =
      VE.SoftNorms.Run.runCaseReported (softExpanded kvs entry.environment)

-- Protocol.lean:1152
theorem expandSoft_hit (h : Handles) (kvs : Std.TreeMap.Raw String Json compare) (d : String) (entry : Entry)
    (hd : (Json.obj kvs).getObjVal? softHandleKey = .ok (.str d)) (hn : softNamed .softNorms (.obj kvs) = true)
    (ht : h.table[d]? = some entry) :
    h.expandSoft .softNorms (.obj kvs) = .ok (.ok (softExpanded kvs entry.environment))

-- Protocol.lean:1160: a handle the table does not hold is never answered from another entry
theorem expandSoft_miss (h : Handles) (m : Mode) (kvs : Std.TreeMap.Raw String Json compare) (d : String)
    (hd : (Json.obj kvs).getObjVal? softHandleKey = .ok (.str d)) (hn : softNamed m (.obj kvs) = true)
    (ht : h.table[d]? = none) :
    h.expandSoft m (.obj kvs) = .error s!"CheckerUnavailable: soft document handle {d} is not registered"

-- Protocol.lean:1167: other kinds, other modes, a case with environment, norms or environment_handle
theorem expandSoft_refused (h : Handles) (m : Mode) (kvs : Std.TreeMap.Raw String Json compare) (handle : Json)
    (hd : (Json.obj kvs).getObjVal? softHandleKey = .ok handle)
    (hn : ∀ d, handle = .str d → softNamed m (.obj kvs) = false) :
    h.expandSoft m (.obj kvs) = .ok (.error softRefusal)

-- Protocol.lean:652
theorem prepareDocument_ok {document : Json} {p : VE.SoftNorms.Run.Prepared}
    (h : prepareDocument document = .ok p) :
    VE.SoftNorms.Wire.decodeSoftSource (document.getObjValD "environment") (document.getObjValD "norms") =
      .ok p.src
```

Together: the case naming a held soft document expands to the written-out case (`expandSoft_hit`), and
`softResult` on it equals `VE.SoftNorms.Run.runCaseReported` of that written-out case (`softResult_cached`), which
is `runMode .softNorms` (`runMode_softNorms`). That is the answer of the unprepared runner. `Run.lean` (kb-3a's file)
is not edited.

## (4) Python: `ve/backends/lean_service.py`

`_encode` (soft-norms mode only) sends a `soft-selected` case whose environment is an object and whose norms are a
list, and which names no handle, as `soft_document_handle` = SHA-256 of the exact text it registers. That text is
`'{"environment":' + env_text + ',"norms":' + norms_text + '}'`, encoded once per pair of objects. The registration
is mirrored in the client's table (`_note`). If the service answers with the request error `CheckerUnavailable`
while the chunk has a soft case, the client registers every handle of the chunk again and retries once
(`stats["handle_reregistered"]`). Any other request error, or a second one, is resent written out, as for
environment handles. `bind_selected` and `ve/soft_route.py` are unchanged: `selected_at` reaches the handle path
through the client, so it needed no change.

## Acceptance

(i) Answers byte-identical. `uv run pytest -q tests/test_soft_selected.py tests/test_soft_document_handles.py`:
**186 passed** (log `/tmp/kb10e-sel.log`, after commit 8). `tests/test_soft_selected.py` is kb-10a's, unchanged.
`test_twenty_alternating_cases_answer_the_same_bytes_by_handle_and_written_out` sends 20 cases (documents A and B,
which differ in the strict rule's guard; three models; alternating) by handle and written out, one call per case
and in one request, and compares the answer bytes. `test_captured_safety_framework_cases_answer_the_same_bytes`
does the same for the captured RSP and Preparedness cases.

(ii) Timing: the tables above. Repeat call 2.1 ms (target at most 80), first call 114.5 ms (target at most 500).

(iii) `cd lean && lake build`: `Build completed successfully (1441 jobs)`, 0 errors (`/tmp/kb10e-lakefinal.log`).
`python3 lean/audit.py`: `PASS: 873 source files; 9993 named theorem declarations audited ... only the declared
standard axiom allowlist` (no new axiom; the new theorems use `propext`, `Classical.choice`, `Quot.sound` or
none, `lean/axioms.txt`). `VE_NATIVE_PREBUILT=1 .venv/bin/python tools/kernel_closure.py --check
docs/kernel/closure-baseline.json`: `PASS: kernel 9560 <= 9560`, `PASS: verdict writers outside the kernel 56 <=
56`. Kernel figures:

| | main 9a3fd7a9f9 | this branch |
|---|---:|---:|
| kernel (distinct lines, tier kernel) | 9,552 | 9,560 (+8) |
| softNorms path: theorems / spec / lines | 4 / 4,912 / 4,920 | 5 / 4,920 / 4,928 |
| under the frozen keys' answers | 16,198 | 16,206 |
| lines added to `Protocol.lean` (not measured) | | +219, −26 |

The +8 is `soft_wire_selected_prepared`, listed on `softNorms` (`tools/kernel-paths.json`): the `Prepared`
structure and `prepare` in its spec. The allowance line is in `docs/kernel/ALLOWANCES.md`.

(iv) Frozen keys, on 120b6538bd (product code as final; later commits change only tests, docs, generated files
and the merge with main), `.venv/bin/python` with `docs/kernel/frozen-keys-20261111.md`'s commands, without the
tracer, one after another under `iso.sh` (`/tmp/kb10e-trace/frozen.log`):

| Key | Command | Exit | Seconds |
|---|---|---:|---:|
| RSP | `usecases/anthropic-rsp/run.py --check` | 0 | 326 |
| Preparedness | `usecases/openai-preparedness/run.py --check --base-only` | 0 | 192 |
| FSF | `usecases/safety-framework/run.py --check` | 0 | 107 |
| agent-policy | `usecases/agent-policy/check.py base` | 0 | 99 |
| eligibility | `usecases/eligibility/run.py --no-write --no-mutants` | 0 | 155 |

`git status --short` afterwards showed only the new uncommitted timing tables, so every `results.json` is
byte-identical. No harness calls the new path. The client sends a handle only for `soft-selected` cases.
`grep -rln "soft-selected\|selected_at" usecases` names only `usecases/safetyfw_shadow.py`, kb-10b's
evidence-only shadow, merged to main after these runs. It is not one of the five keys. Its Lean calls now go by
handle, and their answers are the same bytes (acceptance (i)).

## Answers on main to a case naming a soft document

The same requests went to main's binary and this branch's (`/tmp/kb10e-trace/oldprobe.py`; one `soft-norms`
request registering the document, each case naming its handle):

| case | main | this branch |
|---|---|---|
| handle only (soft-selected) | `SOFT_INVALID_INPUT: property not found: environment` | answered (`status: ok`) |
| another kind (soft-elaborate) | `SOFT_INVALID_INPUT: property not found: environment` | case error `InvalidInput: soft_document_handle names a soft document only …` |
| with an environment | `SOFT_INVALID_INPUT: InvalidInput: invalid environment envelope` | the same InvalidInput |
| with norms | `SOFT_INVALID_INPUT: property not found: environment` | the same InvalidInput |
| with an unheld environment_handle | request error `CheckerUnavailable: environment handle … is not registered` | the same InvalidInput |
| a handle that is not a string | `SOFT_INVALID_INPUT: property not found: environment` | the same InvalidInput |

## Seeded bugs (`docs/kernel/kb-10e/seeded-bugs.json`)

| Id | Lang | File | Bug | Fails |
|---|---|---|---|---|
| a | Lean | `lean/VE/Service/Protocol.lean` | `softEntry?` answers the last entry of the table, whatever the digest | `softResult_cached` does not build (Protocol.lean:1211, unsolved goals). The theorem catches it, so it was not strengthened. |
| b | Lean | `lean/VE/SoftNorms/Prepared.lean` | `prepareFrom` drops the last rule from the expansion | `prepare_ok` (:143) and `runSelectedP_prepareFrom` (:169) do not build |
| c | Python | `ve/backends/lean_service.py` | `_encode` keys documents by environment only, so document B's case (B's model) is sent with A's handle | `test_a_model_for_another_document_is_not_answered_from_this_one`: Lean's model decoder refuses (`fields do not match`). Also `test_twenty_alternating_…[one-request]`: when the vocabularies agree, `bind_selected` accepts A's answer (same rule names) and the byte comparison fails. |
| d | schema | `ve/backends/lean_service_schema/envelope.json` | `required` without `soft_member` | `test_bad_or_missing_handshake_is_unavailable[missing-soft-member]` |

Each was restored with `git checkout`.

Trust mutants: `zsh manage-agents/mac-pytest.sh --trustmut -- --max-mutants 1000 --deep --allow
docs/kernel/kb-10e/trust-mutants-allow.json --json docs/kernel/kb-10e/trust-mutants.json` gives **24 KILLED, 0
SURVIVOR, 0 UNKNOWN, 21 ALLOWED, exit 0**, after one run without the allow file (`--deep`: 24 KILLED, 19 SURVIVOR,
2 UNKNOWN). Without `--deep` the handshake's `#guard` (lean/ResponseShape/Schemas.lean:113) is out of the cone, and
all 45 were SURVIVOR or UNKNOWN. Every allowance has its reason in the file. Seventeen are mutants that only loosen
the handshake's response shape; those change the generated envelope.json. One is `respondMemo`'s branch, an
equivalent mutant: `runRequest` and `runSoftRequest` answer alike. Two are `Entry.soft_eq` mutants that do not
compile.

## Other soft kinds

None of them uses `Prepared` yet. `Prepared` holds the source and the softened document, so each kind needs one
field and one equality, plus `softNamed` widened with a `runCaseReportedP_eq` case for it:

- `soft-elaborate`, `soft-pairs`: `decodeSoftSource` and the elaboration of `soften D`. Add
  `elaborate (soften D).T` as a field with `rfl`.
- `soft-certificate`: `background' D` and `elaborate (soften D).T`. The same, plus `background'`.
- `soft-conflict`: `targets (soften D)` and the conflict search, which depends on the case's budget, so only the
  targets and the background formulas can be held. The model, when given, decodes over `p.vocabulary`
  (`decodeModelIn_prime`).
- kb-3a's slot kinds: on feature/kb-3a, not on main; each would need its runner stated over `Prepared` and a
  `runCaseReportedP_eq` case.

## Spec re-read

- `softHandleKey = "soft_document_handle"` against the task's member name (task (3)).
- The registration key is the SHA-256 of the exact text, refused otherwise (`registerOne`, Protocol.lean:690),
  against task (3) "keyed by its SHA-256 exactly as environments are".
- Neither `environment` nor `norms` may appear with a handle (`softNamed`, Protocol.lean:728) against task (3)
  "with neither environment nor norms". I also refuse `environment_handle`, the narrower reading.
- An unheld handle gives `CheckerUnavailable … is not registered` (`expandSoft_miss`) against task (3).
- Other kinds give `InvalidInput` (`expandSoft_refused`) against task (3).
- The client retries once on `CheckerUnavailable` (`lean_service.py`), against task (4).
- `bind_selected` is unchanged (`git diff main...HEAD -- ve/soft_route.py` is empty), against task (4).

## Notes for the DRI

- After this item the written-out path (`handles=False`, and any caller outside the service client) still computes
  `soften D` several times per case, about 1 s for a Preparedness case. `runSelected_eq_prepared` would let a
  `@[csimp]` lemma route `runSelected` through `prepare` for everyone. Not done: the task is the handle path, and
  `runSelected` is mentioned by a listed theorem.
- `decodeSoftSource`, about 100 ms, is now the whole of a first call.
- Timings were taken on a loaded machine (load average about 50); the before/after pair under the same load is
  saved with them.

## Final selected run

`MAC_PYTEST_NO_DEFER=1 zsh manage-agents/mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` ran on
6383f22a93, committed and clean, on the VM (the Mac last; 9,313 s). It selected 618/618 test units (map c9214a2608).
Before the tests it ran the layer checks, `lake build` and `lean/audit.py`. Units: 632 lines `exit 0` and 2 `exit 1`
(`/tmp/kb10e-final-sel.log`). Both failures were this branch's, and both are fixed in commit (12):

- `tests/test_kernel_closure.py::test_the_records_quote_the_saved_measurement`: `docs/spec/kernel-boundary.md` and
  `docs/kernel/frozen-keys-20261111.md` still quoted 9,552 and 16,198. They now quote the regenerated baseline
  (9,560, 16,206, and the softNorms, readingsRoute, discourse and document rows).
- `tests/test_wire_gate_corpus.py::test_gate_corpus_holds_every_test_input_of_every_unit`: the soft source of
  `test_the_relay_answers_a_document_by_handle` was missing from the gate's corpus. It was recorded with `uv run
  python -m conformance.wire_contract_gate --record-test-inputs`, keeping only the
  `soft-norms@0-test-inputs.json` change, as kb-10a did (546d2d43c5). The same command also rewrites
  `soft-norms@0-gate.json`, last written 2026-10-03. That rewrite reported 778 boundary problems in validation
  messages that have nothing to do with this item (for example `AST exceeds depth or node budget` against
  `ResourceLimit: AST exceeds depth or node budget`), so it was reverted. Note for the DRI: the saved gate report
  is out of date with today's tree.

The two failed ids were rerun: `zsh manage-agents/mac-pytest.sh -- <the two ids>`, **2 passed** (700 s, exit 0,
`/tmp/kb10e-rerun.log`). The full gate is the chain's, on the final HEAD.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained: PASS. The answer by handle is the kb-10a typed row, checked by the same schema and
   `bind_selected` (`test_the_relay_answers_a_document_by_handle`). The handshake's new field is a schema `const`,
   with fuzz for missing, retyped and other values (`test_bad_or_missing_handshake_is_unavailable[missing-soft-member]`,
   `[retyped-soft-member]`, `[other-soft-member]`). The unheld-handle request error is checked
   (`test_a_handle_the_process_does_not_hold_is_a_bound_request_error`).
2. Deliverables: PASS. Parts (1) to (4), acceptance (i) to (iv), seeded bugs (a) to (c), the ALLOWANCES line and the
   report items are all above, each with its commit and test. `ve/soft_route.py` needed no change (section (4)).
3. Tests can fail: PASS. `seeded-bugs.json` (a, b, c) plus (d); `trust-mutants.json`, exit 0.
4. Python and Lean agree: PASS. `test_twenty_alternating_…`, `test_captured_safety_framework_cases_…`, and the five
   frozen keys. No Rust change.
5. R8 binding: PASS. `bind_selected` is unchanged and kb-10a's binding tests pass (`tests/test_soft_selected.py`,
   186 passed with the handle tests). A wrong document's handle is refused (`test_a_model_for_another_document_…`).
6. Gate evidence on the final HEAD: PASS. Synced with main (merge b9724f0628), regenerated after it, and the final
   selected run is on the committed tree (section above). The full gate is the chain's.
7. No unsigned item: PASS. DELTA rows cite R16, R3, R8, R2 and R12. The kernel allowance is the architect seat's
   signed line.
8. Every user-visible change in DELTA: PASS. Rows 2 to 4, with main's answers probed (section "Answers on main").
9. Test selection: PASS. `tools/select_tests.py --base $(git merge-base HEAD main)` selects all 615 units because
   `ve/backends/lean_service.py` and the service binary are read by every relay test, a real dependency. It
   contains `tests/test_soft_document_handles.py` and `tests/test_lean_service.py`, which fail under seeds (c) and (d).
10. Lean statements: PASS. Seeds (a) and (b) break the build of `softResult_cached` and `prepare_ok`. The statements
    are about the value returned (`softResult` is what `runSoftRequest` puts in the response, `softResults_eq`).
    No `tools/check_*_statements.py` covers these modules.
11. Budgets fail closed: PASS. A handle case goes through the same `runSoftRequest` budget checks
    (`runSoftRequest_ok`: bytes, cases, digests before expansion), and the query count is charged before decoding
    (`selectedQueries`: `maxTuples` before `decodeQueries`). No sleeps or timers in the new tests.
12. No CPU or memory regression: PASS. The written-out path matches main's binary under the same load (table (ii)).
    Memory: one prepared entry per held handle, bounded by `maxHandles`.
13. No test removed or renamed: PASS. `uv run python tools/gate_collection.py --check --prebuilt`: "34978 collected, 34959 at c9214a2608; 19 added, 0 removed by a trailer, 0 refused, 0 stale and 0 malformed trailers".
14. Both directions, cited evidence: PASS. Accepted and refused for the handle (`…answer_the_same_bytes…` against
    `test_any_other_case_naming_a_soft_document_is_refused[*]`), and for the handshake (`test_handshake` against
    the three fuzz cases). Each claim above names its command or log.
15. Overclaim, silent cut, new checks fail, limits first: PASS. Universal words checked against the tests named
    beside them; no deliverable cut; each new check has a seed; limits are charged before work (item 11).
