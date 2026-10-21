# me-2 report: the `ve-calc@0` wire and the `calc` runner (math-evidence ME-2, first part)

No DRI signature is reserved: the one DELTA row cites R16. The item is cut as the task suggested: the wire and the
runner with the route cases; the service mode, its shape and encoder, and the row fields beyond the outcome are the
next item **me-2b**. Size is over the ~600-line guide (below, "Size").

## Statement gate

ME-S passed its bounded re-checks (manage-agents `math-evidence-p3ver1.final.md`, then `math-evidence-p3ver2.final.md`:
PASS). Plan and spec are main's (`docs/spec/math-evidence-PLAN.md` and `docs/spec/math-evidence.md`, identical to
c5197da78). Spec 3.4 gives the elaborated forms of 3.2's statements (the plan says so under 3.2), so they are the
ones built. Each statement proved here equals the reviewed text after whitespace normalisation (checked by a script
over the spec section and the Lean files): `Wire.decodeCase_wellFormed`, `Check.run_claim`, `Check.run_sound`,
`Run.rows_outcome`, `Run.outcome_sound`, `Run.row_sound`, `Run.verdict_sound`, `Run.unknown_named`. `Check`,
`Check.UnknownCause` and `Check.OutcomeMeans` are the reviewed text with the `claim` constructor and its clauses only,
as spec 3.4 says ("each batch adds its constructor, its clauses and its case of `Check.run_sound`"); `Case`, `Row`,
`Run.row` and `Run.rows` are as written. `runMode_calc` and `runCaseReported_fits` are me-2b's (the mode). No
statement changed.

## Plan rows (ME-2 at main; plan 3.2, spec 2.1 and 3.1-3.4, J1)

| Row | Delivered | Where, checked by (`lean/VE/Calc/RunExamples.lean` guard line) |
|---|---|---|
| `lean/VE/Calc/Wire.lean`: `Case`, `Wire.decodeCase` | yes: format, values (stated or defined), claims (`eq`, `lt`, `le`, `gt`, `ge`, `within`, `rounds` with an optional rule, `rounds-down`, `rounds-up`), `rounding`, `software`, `support`, `span` | 91, 299-490, 494, 548, 574 |
| Limits of 3.2 in order: 10,000 JSON values, depth 64, 512 values, 512 claims, exponents 64, literals 40 digits (W6's `parseDecimal`), strings 64 bytes (2.6 and 3.2's names and claim ids; round 3: every string and object key of the case but a value record's `words`); checked before anything else | yes, each on both sides, and their order (exponent before digits before strings; a limit before a field error) | 316-490 |
| Decoder refusals of 13.1 owned by ME-2: `InvalidInput` (with the JSON path), `ResourceLimit`, `UnknownName`, `DuplicateName`, `DuplicateClaimId`, `NoClaims` | yes | 494, 548, 574 |
| `VerbalisationCollision`, `ValueWordsForm`, `ReservedWord` | **me-2b**, with the `line` field they serve; until then `words` is any string | 413 states it |
| Identity 3.3 with J1: `meaning_id` through `VE.Route.Wire.meaningId ["calc@0"]`, the frozen encoder unchanged; `words` removed; values in shortest plain decimal (no `sci` left); printed numbers as `[digits, places]` canonical decimal strings; each `rounds` claim with its rule; claim ids by `ve-calc-claim-v0.2:calc@0` | yes; I-1 pinned (`b3798e85…`, and `c7cd36a4…` for the `"20000000"` spelling), R-1 and R-2 claim ids pinned; one table (`identityFamilies`) holds a family per normalisation and per hashed field, at every place a literal or a printed number is read, among them the case's rule in an implicit `rounds` claim and a `lit`'s shortest spelling (round 2, review F9 and F10) | 54-55, 135-281 (`identityFaults == []` at 242) |
| `Wire.decodeCase_wellFormed` | yes | proof; `lean/VE/Audit.lean` |
| Spec 3.4: `Check` (claim), `Check.UnknownCause`, `Check.OutcomeMeans`, `Check.run`, `Check.run_sound`, `Row`, `Run.row`, `Run.rows`, `Run.rows_outcome`, `Run.runCaseReported`, `Run.outcomeAt`, `Run.outcome_sound`, `Run.row_sound`, `Run.verdict_sound`, `Run.unknown_named` | yes, all proved; the decided-row meaning is also decidable for route cases | 54-60, 123 |
| Route cases V-1, V-2, V-5 (20 claims in one case), V-11, V-9, I-1, R-1, R-2 | yes, as `#guard`s with every expected result of spec 13.3 and 13.6 (R-1 and R-2 pinned whole, every field) | 54-55, 91 |
| Hostile set: unknown name, a name defined after its use, `pow` above the limit, a literal of 41 digits, a printed spelling with a sign error, a forged `meaning_id` | yes (a forged `meaning_id` in the request is an unknown field: the identity is Lean's) | 289, 333 |
| Plan's seeded bug: claim i + 1's verdict reported for claim i | yes: `mutants.json` `plan-seeded-bug` fails the R-1 and R-2 guards (54, 55) | `mutants.json` |
| `calc` constructor, name, list entry, dispatch, `runMode_calc`; `MODES` (generated from the handshake) | **me-2b**: registering the mode needs `ResponseShape.Encoders.runMode_fits`' case, so the shape and encoder come with it | |
| `lean/ResponseShape/{Schemas,Encoders}/Calc.lean`, `calc.json`, `DEADLINES` | **me-2b** | |
| `calc@0` row of AR-10's profile table | **not built; to ME-10**: no case of the `calc` mode lists profiles (spec 3.1), and admitting `calc@0` in a document environment before any route checks calculation content would widen what is accepted, which no standing ruling covers. ME-10 (calculation content in documents) adds the row with its composition proof | FOLLOW-UPS "## me-2" |
| `ve/assurance-manifest.json` decoder pins | yes: `Wire.lean` and `Run.lean` pinned whole, `Units.lean` re-pinned, `RunExamples.lean` under `other_json` | `tests/test_assurance_manifest.py` |
| `ROADMAP.md` trust-cost line | yes | |
| Generated files via regen | `regen_generated.py --write` (inventories, `docs/spec/assurance-manifest.md`); `calc.json`, `ResponseShape.lean` and `route-cases.json` are unchanged until me-2b | `regen_generated.py --check` |

One owner: `VE.Calc.Units` now takes `checkFields` and `invalid` from `VE.Calc.Wire` (moved, with an optional-field
list) and spells a factor with `Wire.plain` (the shortest plain decimal), so `ve-units@2`'s factors and `ve-calc@0`'s
values share one canonical spelling. Every `UnitsExamples` guard is unchanged. me-6c (factors written
`["sci", d, e]`) can now read them with `Wire.literal`.

Fault order (no base exists, so none of it is a delta; recorded for me-2b's relay): the limits in 3.2's order;
then the case's fields (unknown before missing), the format, the rule, the software convention, the lists and
`NoClaims`; then each value record and each claim entry in order (fields, name, words, source, support, span); then
`DuplicateName`, `UnknownName` (definitions in order, then claims) and `DuplicateClaimId`.

## Identity and decoder truth tables (recheck 2)

Acceptance and hashing have one condition: every limit, field, type, name and expression check passes, and the
decoder constructs every identity part in the canonical form of spec 3.3. A case failing a limit is `ResourceLimit`; a malformed
field, type, literal or expression is `InvalidInput`; the later duplicate, unknown-name and no-claim checks have
their named error kinds. The `#guard`s in `VE.Calc.RunExamples` evaluate the Lean decoder and digest. Fields planned
for later ME batches (`source`, `data`, `premises`, counted values and units) are refused by this batch.

| Hashed part or normalisation | Fixture that pins it | Wrong encodings killed by that fixture |
|---|---|---|
| Case `format` and profile/environment domain (`calc@0`, `{}`) | pinned I-1 digests; `identityFamilies` | changed spelling, dropped field or domain |
| Ordered `values` and `claims` arrays | `identityFamilies`: value names/order, claim forms, claim IDs | swapped, dropped or duplicated entry |
| Value `name`, source selector `stated`/`defined` | `identityFamilies`: value names/order and value source | renamed, selector changed, dropped source |
| Stated, defined and expression `lit` values: shortest plain decimal, no `sci` or negative zero | `identityFamilies`: each `literalSites` plain/zero family; pinned I-1 digests | raw spelling, unnormalised `sci`, sign or place error |
| `words` excluded, object keys sorted | `identityFamilies`: words and key order | retaining words or input key order |
| `pow` exponent, and expression and comparison operator/operand order | `identityFamilies`: pow exponent, operations, comparisons as written; canonical claim guards | number changed to string, operand swap, operator fold |
| Printed number `[digits, places]` as two canonical decimal strings | `identityFamilies`: every `printedSites` family; explicit canonical-claim guard | number/string type swap, written-place loss, digit/place swap |
| `rounds` rule (explicit or inherited); `rounds-down`/`rounds-up` name | `identityFamilies`: tie rule and claim forms; canonical-claim guard | dropped rule, wrong inheritance, rule/name swap |
| Claim `id`, canonical claim and case meaning in each claim digest | `identityFamilies`: claim IDs; pinned R-1/R-2 complete rows | dropped/changed id, claim, meaning or claim-domain prefix |
| Value `support` (all three enum spellings) | `Wire.supports.all` exact `recordJson` guard; `identityFamilies` support | spelling, type, dropped or duplicated field |
| Value and claim `span` (ordered JSON natural numbers) | two exact span digests for `[3,5]` plus `identityFamilies` span families | number→string, endpoint swap, dropped or duplicated span |
| Case `software` | exact `P` digest plus `identityFamilies` software family | spelling, type, dropped or duplicated field |

The exact digest guards test the frozen encoder's output; the support guard covers its whole finite vocabulary.
The F11 probe's four encoding mutants were survivors before these fixtures and are killed after them. A separate
`testimony`/`assumption` spelling mutant found in the second hunt is killed by the `Wire.supports.all` guard.

| Decoder check and branch | At boundary; one past; error kind | Guard and mutation it catches |
|---|---|---|
| JSON values ≤10,000; depth ≤64 | 10,000/10,001; 64/65, then `InvalidInput`/`ResourceLimit`; values counted at any nesting (20,000 values 256 and 300 deep; a chain of 10,001 arrays is limit 1, of 10,000 limit 2) | `nodes`, `nodes-over`, `depth`, `depth-over`, guard 322; `<` or constant change, count fuel `maxNodes`, depth fuel `maxDepth` |
| `values` and `claims` ≤512 each | 512/513, then malformed entry/`ResourceLimit` | `values`, `values-over`, `claims`, `claims-over`; `<` or branch dropped |
| `pow` exponent ≤64 and `sci` exponent absolute value ≤64 | 64/65 and −64/−65, then answer/`ResourceLimit` | `pow`, `pow-over`, `sci`, `sci-over`, positive `sci` 64 guard; sign, constant or branch dropped |
| W6 digits ≤40: stated and `lit` plain/`sci` | 40/41, then answer/`ResourceLimit` | `digits`, `digits-over`, `digits-lit*`, new `sci` 40/41 guard; constant or form dropped |
| W6 digits ≤40: `rounds`, `rounds-down`, `rounds-up` plain and `sci` | each 40/41, then answer/`ResourceLimit` | new three-branch guards; `startsWith` narrowed to `==` |
| Every string and object key ≤64 UTF-8 bytes, but a value record's `words` string (one allow-list, `stringFault` over `unworded`) | each 64/65, then answer or its own refusal/`ResourceLimit`, with 1-, 2-, 3- and 4-byte characters: value name, claim ID, `val`, `software`, `support`, `rounding`, `format`, a claim's and an expression's operator, a claim's rule, a premise id, an unknown field, a non-object value, `words` in a claim entry, in the case, as a list and inside `defined`, and keys of the case, a value record and a claim entry; at JSON depth 64 a string and a key; a value's `words` of 192 bytes accepted; a 65-digit literal is still limit 6, an exponent and the value count still come first | `name`, `name-over`, `id-over`, `val-over`, `multiByteNames` (362), F16 (383), `stringSites` (409), `words` (413), order (417), `deepScanFault` (470); cap 63 or 65, character count, keys skipped, `words` exception widened to every key, to a non-string `words` and to claim entries |
| Expression fuel and JSON depth at both entry points | claim nesting 59/60 and defined nesting 60/61: accepted/`ResourceLimit` | new `nestedExpr` guards; fuel 20 mutation at either entry point |
| Limit scan through the full admitted depth | a `pow` or `sci` exponent, 41-digit literal, or overlong name at JSON depth 64 still gives its specific `ResourceLimit`; a valid nested `pow` expression does too | `deepScanFault` checks the exact JSON depth before each answer, and `nestedPow` checks a valid expression; scan fuel 20 or 63 fails |
| Limit order, ahead of field validation | simultaneous exponent/digits/name and digit/unknown field | `order-*` guards; branch reordered or skipped |
| Record, rule and claim-form checks | accepted edges and `hostile set`, `paths`, `malformed` | one branch dropped or a wrong type admitted |

The wide-array guard evaluates `Wire.count` and `Wire.depth` on 100,000 flat children (over ten times the old
largest fixture), so the elaborator exercises the worklist count and the depth fold without the former `List.sum`
stack growth. (`Wire.size` until round 3; it is now `count` and `depth`, below.)

F14 and F15 recheck: before the new guards, the supplied scan-fuel mutants (20 and `maxDepth - 1`) and the
character-count mutant each built `VE.Calc.RunExamples` successfully. After the guards, all three builds fail
at the expected guards; the original source was restored after each probe and the unmutated focused build passes.
The scan guard covers every node-local limit at the last admitted depth, so neither a generic JSON-depth refusal
nor a shallow scan can mask the tested fault. The Unicode guard covers every name site at the exact byte boundary
with characters of three different UTF-8 widths. Neither finding changes the production decoder or public output.

The review probes F11 (four encodings), F12 (the narrowed `rounds` branch) and F13 (both expression entry points)
all survived the old guards before the fix and all nine final source mutants, including the two hunts below, fail
`lake build VE.Calc.RunExamples` after it. Each mutant build was capped at 600 seconds; the original source was
restored and rebuilt successfully. Hunt 1 tried branch-specific decoder boundaries and found the missing accepted
64-byte claim ID; its 64-byte rejection mutant now fails the `name64` claim-ID guard. Hunt 2 tried enum-specific
identity spellings and found that `testimony` and `assumption` could change while `observation` stayed correct; its
mutant now fails the guard over the whole `Wire.supports` vocabulary. No form from either hunt remains open.

FM1 reproduced on ve-mac-1 before the fix (`VE.Calc.RunExamples` exited 134, deep recursion in `Wire.size`). After
the accumulator fold, the same Mac test command built Lean and reported `151 passed`; the FM1 failure grep had no
match. The 100,000-child `Wire.size` guard is the permanent FM1 regression.

## Round 3: F16 and the class (looprecheck2, DRI note 20261021b)

F16 (B): `software` had no 64-byte cap (spec 2.6); 65 bytes or more answered "c1 holds reproduction unknown".
PROBE F16 exited 1 before the fix and exits 0 after it. The class, not the field, is removed: `nameFault`, which
capped only the strings it named (`name`, `id`, `["val", n]`), is replaced by one allow-list. `stringFault` refuses
any string or object key of more than 64 UTF-8 bytes, anywhere in the case, and `unworded` sets each value record's
`words` string to `null` before that scan, so `words` is the only string the cap does not reach. It is still
position 7 of 3.2's order: the exponent and literal scans run over the whole case first. Any string me-2 does not
decode yet (`support`, `rounding`, `format`, operator tags, premise ids, a field a later ME adds) is capped by
default. The message is `ResourceLimit: a string exceeds 64` (3.2's `<limit> exceeds <n>`), and the guards that
pinned "a name" now pin it. No route case (V-1, V-2, V-5, V-11, V-9, I-1, R-1, R-2), hostile-set row or seeded bug
changed its expected outcome. Refusals that did change, all for strings of more than 64 bytes, go from
`InvalidInput` to `ResourceLimit` (an over-long `format`, `rounding`, `support`, operator or unknown field), the
safe direction the note accepts.

The tests are the note's list, one per safe case, each at 64 and 65 bytes in ASCII and in 2-, 3- and 4-byte
characters (`strings64`): `software` (F16's guard, 383); name, claim id and `val` (362 and the limit table);
`support`, `rounding`, `format`, both operator positions, a claim's rule, a premise id, an unknown field, a value
that is not an object, `words` outside a value record or not a string, and object keys of the case, a value record
and a claim entry (`stringSites`, 409); a string and a key at JSON depth 64 (470); a value's `words` of 192 bytes is
accepted (413); a 65-digit literal is still limit 6 at every literal site, and an exponent and the value count still
come before the cap (417). The mutants the note names all fail those guards: cap at 63 and 65, `length` for
`utf8ByteSize`, keys skipped, and the `words` exception widened to every key of a value record, to a `words` that is
not a string, and to claim entries (`mutants.json`, `string-*` and `words-*`; each build under `timeout 600`).

R16 budget: `stringFault`, `unworded`, `count` and `depth` are D[R], like the limits before them, so
`trust_map.py --check` measures K +0, S +14, untied V +134, trusted +148 on the final HEAD, unchanged. The
allow-list is 13 lines against `nameFault`'s 12, none of them trusted. `trust_mutants.py --max-mutants 1000` on 401bf3675 (the Mac
runner unreachable, on the VM): 125 killed, 0 survivors, 0 unknown, 21 allowed, exit 0.

Hunts (subagents given only class B, PROBEs F14, F15 and F16, and the code):

- **Hunt 1** tried duplicate keys, `\u` escapes and surrogates in strings and keys (an escaped `words` key is the
  real key), `words` under a `values` object, in `pad.values`, in a wrapped record, a long name beside a long
  `words`, top-level strings, long strings at `pow`, `lit` and `sci` positions, fullwidth digits, exponents as
  huge integers, `1e100`, `65E0`, `-0`, `65.0`, `6.5e1`, digit counting with signs, leading zeros and junk, wrong
  arities, and 512/513 records. Found: (a) **fixed**, values nested below 257 levels were not counted, so 20,000
  values 300 deep reported the depth limit before the node limit. `size` is now `count`, a tail-recursive worklist
  exact up to 10,001 at any nesting (a recursive count with that fuel overflowed the interpreter's stack at depth
  10,001), and `depth`, bounded by the depth limit (guard 322; mutants `count-fuel`, `depth-fuel`). (b) **open**,
  below: duplicate keys. (c) a spelling question, not a limit passed: `getInt?` reads an exponent's written form,
  so `65.0` is `InvalidInput` and `6.4e1` is accepted as 64. Every spelling is refused or read as its value, and
  the canonical form re-encodes the integer. Whether fractional spellings are admitted is a wire decision for
  me-2b; it is a follow-up.
- **Hunt 2** tried limit 6 at every printed number and `within` bound, literals and exponents where the scans do
  not match (`stated` as an array, `sci` in `stated`, `defined` holding a literal), 10,000/10,001 values with
  objects, keys and mixed nesting, depth 64/65 mixed, the order of every pair of limits, `unworded` beside each
  earlier limit, and a 41-digit `words`. It found no case where a limit is exceeded and the decoder answers rows
  or reports a different limit. It found the safe direction only: `literalFault` also matches shapes the grammar
  refuses anyway (`["sci", d]`, `["sci", d, 1, 2]`, `["roundsX", x, d]`, `rounds-down` with a rule, `rounds` with
  five members), and limits 5 and 6 fire anywhere in the case, as `limitFault` says, so such a case is
  `ResourceLimit` where its field check would say `InvalidInput`. The note keeps that direction ("do not widen the
  rule"), so it is unchanged and recorded as a follow-up. Hunt 2 also noted that 3.2 says "JSON nodes" while the
  count and message say "JSON values" (keys are not counted), and that 3.2's item 7 names only names and claim
  ids. The DRI note reads 2.6 and 3.2 together as the string cap, and the spec text is unchanged.

Open (B), for the item that adds the text entry: **duplicate JSON keys**. The decoder reads a parsed `Json`, and
`Lean.Json.parse` (the only parser `RunExamples` uses) keeps the last of two equal keys, so an earlier member
over any limit is never seen: `"software": <65 bytes>, "software": "P"` answers rows, and so do 600 values or a
41-digit value before a second `values`. me-2 has no text entry (no mode; `Run.runCaseReported` takes `Json`), and
the service decodes non-English cases with `VE.JsonInput.parseCases`, which refuses a duplicate key. It also
refuses negative numbers, which `sci` needs, so me-2b's mode must choose its parser with both in view. PROBE:

```
cd lean && export PATH="$HOME/.elan/bin:$PATH" && lake env lean --stdin <<'EOF'
import VE.Calc.RunExamples
open Lean VE.Calc VE.Calc.RunExamples
#guard let L := name64 ++ "x"
  [req x1 ok1 s!", \"software\": \"{L}\", \"software\": \"P\"",
   req s!"\{\"name\": \"{L}\", \"name\": \"x\", \"words\": \"w\", \"stated\": \"1\"}" ok1,
   req (nulls 600) ok1 s!", \"values\": [{x1}]",
   req x1 ok1 s!", \"software\": [{nulls 20000}], \"software\": \"P\"",
   req x1 (c1 r#"["eq", ["pow", ["val", "x"], 65], ["lit", "1"]]"#) s!", \"claims\": [{ok1}]",
   req (stated "x" s!"\"{ones 41}\"") ok1 s!", \"values\": [{x1}]"].all fun c => ((answer c).getObjVal? "rows").toOption.isNone
EOF
```

## Trust (R16)

K +0, S +14, untied V +134, trusted +148 (`trust_map.py --check`: PASS; allowance recorded; FOLLOW-UPS "## me-2"
has the ties-pass row). Per declaration in DELTA row 1. The limits, refusals and name checks are D[R]; canonical forms
and digests D[I]; `decodeCase`, `Row`, `Run.row`, `Run.rows`, `Run.words`, `Run.outcomes`, `Run.outcomeAt` and
`Run.runCaseReported` are tied to the theorems that fix what they answer. To stay within 150 the first draft (+165)
was reshaped: reject-only and identity code split into their own declarations, `runCase` folded into the tied
`runCaseReported`, and `Run.row` tied by `Run.row_outcome`.

## Seeded bugs and mutants

- [`trust-mutants.json`](trust-mutants.json): `uv run python tools/trust_mutants.py --max-mutants 1000 --json
  docs/math-evidence-me-2/trust-mutants.json --allow docs/math-evidence-me-2/trust-mutants-allow.json` on the final
  Lean change: 125 KILLED, 0 SURVIVOR, 0 UNKNOWN, 10 INVALID, 21 ALLOWED, 0 NOT RUN; exit 0. The first runs (150
  killed, 45 survivors, 81 unknown; then 122/0/7) were answered with fixtures (every argument's path, asymmetric
  comparisons, claim ids, one-character values) and with code every mutant can reach (cons patterns, the parser's
  fuel from `VE.Limits.maxDepth`, no singleton list wrappers). The allowed: equivalent mutants (`eq` swapped; `take 1`
  of a list of at most one element), mutants that are no program (an Option or a lookup table emptied), and
  `Check.UnknownCause` with the unknown arm of `Check.OutcomeMeans`: a Prop over `Claim.Overflows` and
  `Claim.ReadsExhausted`, which quantify over the rationals, so no evaluated check can read it (FOLLOW-UPS: a
  decidable restatement through `Expr.eval_iff` would). `OutcomeMeans`' `=`→`≠` mutant is killed by the guard at
  123, run by hand with the proofs stubbed (the tool marks a check that decides through the instance as unknown).
- [`mutants.json`](mutants.json): 23 hand mutants, each alone, with every theorem of `Wire.lean` and `Run.lean`
  stubbed so only `#guard`s can catch it (the control build passes); all killed. Lean, one per claimed behaviour and
  per trusted definition: `plan-seeded-bug` (`Run.runCaseReported`, guards 54-55), `literal-sci-sign`,
  `operations-sub`, `comparisons-gt`, `rules-half-even`, `expr-pow`, `claim-within`, `claim-rule`, `value-stated`,
  `entry-id`, `decl-defined`, `decode-software`, `decode-rounding`, `outcome-means` (123), `rowjson-reason`,
  `rowjson-reproduction`, `words-undefined`, `limit-nodes` and `limit-order` (289), `admit-unknown` (333),
  `identify-domain`, and `units-factor-spelling` (`lean/VE/Calc/Units.lean`, `UnitsExamples.lean` 107 and 229).
  Round 2 (review F9, F10 and their class): 20 `identity-*` mutants of `Wire.lean`, each normalisation of 3.3 and
  each hashed field replaced by its input or a constant, each applied alone with the proofs as they are; every one is
  refuted by a guard (the identity table at 242, the canonical claims at 252 and 265, or the pinned answers).
  Python (`tools/layer_policy.py`, a tool): the route cases taken out of the runner layer fails
  `tools/check_lean_imports.py` ("new outward Lean import: VE.Calc.RunExamples -> VE.Calc.Run"). No Rust changed.

## Tests and checks run

- `lake build` (whole library), `python3 lean/audit.py` (PASS, 604 files), `regen_generated.py --write` then
  `--check`, `trust_map.py --check`, `repo_map.py --check`, `check_lean_imports.py`,
  `tests/test_assurance_manifest.py -k "pinned or classified or json_use"` (5 passed).
- Selected tests: "Final selected run" below. Synced with main 6454946a5 (et-3cb) before it, and again with
  768a935fc (df-1ac, only the shared registries overlap): `lake build`, `regen_generated.py --write`,
  `trust_map.py --check` (+148, PASS), `check_lean_imports.py`, and the two fixed test files (141 passed) after it.
- Not run: the full gate (the chain's). No test in `main-known-red.txt` is touched.

## Size

Hand-written lines over the merge base: Lean product 558 (`Wire.lean` 380, `Run.lean` 162, `Units.lean` 13,
`VE.lean` 3), route cases 286 (`RunExamples.lean`), side tables about 200 (`tools/trust-classes.json` 142, assurance
manifest 56), tool 5, evidence and docs about 190 (DELTA, REPORT, `mutants.json`, the allow file, ROADMAP);
`trust-mutants.json` and the inventories are generated. About 1,240 in all, twice the ~600 guide. The cut the task
named was taken (no mode, shape, encoder, words checks or row fields beyond the outcome); a further cut would split
the decoder (380 lines, of which the limit scan is 75 and the refusals and identity most of the rest) from the runner
whose route cases and seeded bug ME-2 asks for, and the decoder alone would still be about 800.

## Pilot bytes and next item

0 expected (plan: "Bytes: 0"); nothing claimed. Next: **me-2b** (the `calc` mode: `Mode.calc` in
`lean/VE/Service/Registry.lean`, the dispatch line and `runMode_calc` in `Protocol.lean`, `Schemas/Calc.lean`,
`Encoders/Calc.lean` with `runCaseReported_fits`, `calc.json`, `DEADLINES`, service-level route cases in
`tests/data/route-cases.jsonl`; the row fields `line`, `display`, `sides`, `tie`, `finding` and `rests_on` with the
words checks), then qt-a3 (protocol queue), me-4 and me-12.

## Final selected run

`mac-pytest.sh --select -- --base 6454946a5f54 --run` on 6035a2de (the synced HEAD): the Mac runner's setup failed
("lake build failed twice (runner problem)"), so it ran on the VM: 81 of 460 units, the lake build (every route case)
and every Lean and layer check passed; 4 tests in 2 files failed, both mine:
`tests/test_assurance_manifest.py::test_decoder_files_are_pinned_whole` and `::test_trusted_decoder_line_ranges_are_pinned`
(`Wire.lean` and `Run.lean` changed after their pins), and
`tests/test_lean_limits.py::test_no_non_frozen_lean_check_hard_codes_a_limit` and `::test_the_reviewers_probe` (the
node, depth and name limits written as numbers). Fixed in cfee74b09: the limits are `VE.Limits.maxNodes`, `maxDepth`
and `maxIdentifierBytes`, the files re-pinned. Then: both files rerun, 141 passed; `lake build VE.Calc.RunExamples
VE.Calc.UnitsExamples` (every guard); `regen_generated.py --check` (33 entries); `trust_map.py --check` PASS (+148);
`trust_mutants.py` again on cfee74b09, the same 125 killed, 21 allowed, exit 0; `gate_collection.py --check
--prebuilt`: 0 added, 0 refused, 0 stale, 0 malformed. The `limit-nodes` hand mutant was rerun on the new text:
killed (guard 153; 289 after round 2).

Round 2 (looprecheck1 F8, F9, F10): `mac-pytest.sh --select -- --base 768a935fcd03 --run` on 55dadbe83, on the VM
(the Mac runner unreachable): 81 of 460 units, 0 failed, exit 0, 5,499 s; the lake build, `lake build
ve_english_lean_bench` and `lean/audit.py` (PASS, 606 files) passed in it. `trust_mutants.py --max-mutants 1000` on
4e91c29ce (VM): 125 killed, 0 survivors, 0 unknown, 21 allowed, exit 0. The allow file's reason for
`Check.UnknownCause` arm-true was reworded after that run (it names the killing proof), so that one mutant's
`detail` in `trust-mutants.json` still shows the earlier wording; no status reads it. A rerun on the VM timed out at
3,500 s under load and was not repeated.

## Self-review against BUILDER-CHECKLIST

1. PASS (decoder side): every field of a case, a value record and a claim entry replaced by 7, true, null, [], {},
   1.5, "" and a nested list is refused and answers no row (guard 413); deep input is the depth limit (289). No Python
   reads a `calc` answer yet (me-2b/ME-3), so the relay half is N.A.
2. PASS: plan rows table above; me-2b and ME-10 named with reasons; no Python copy of a Lean decision, no permanent
   report test; overlap: no in-flight branch edits `Wire.lean`, `Run.lean`, `Units.lean` or `layer_policy.py`; the
   shared registries (`lean/VE.lean`, `tools/trust-classes.json`, `ve/assurance-manifest.json`) are append-only.
3. PASS: `mutants.json` 52 of 52 killed (the first 23 with proofs stubbed, the 20 `identity-*` and the 9 round-3 ones by guards with the proofs as they are); `trust-mutants.json` exit 0.
4. PASS: reordered keys and renamed words keep the `meaning_id`, spellings "0.30"/"0.3" as values do and as printed
   numbers do not, and so on for every normalisation of 3.3 (the identity table, 135-281); `UnitsExamples` unchanged after the shared spelling. No Python or Rust implementation.
5. N.A.: no relayed field yet; inputs: undeclared names refused (`unknown-name`, `defined-after-use`,
   `unknown-claim-name`, 333).
6. PASS: synced with main 768a935fc; selected run on the earlier sync, fixes rerun after; the full gate is the chain's.
7. PASS: DELTA row 1 cites R16 with per-declaration lines; `trust_map.py --check` PASS; FOLLOW-UPS row.
8. PASS: no public output (no mode or route); DELTA says so.
9. PASS: `select_tests.py` selects 81 of 460 units, `lake build` among them, which evaluates every route case; it
   also selected and caught `tests/test_lean_limits.py` and the manifest pins (above).
10. PASS: the eight statements equal the reviewed text; mutants break the proofs before they are stubbed (for
    example `outcome-means` breaks `Check.run_sound` and `Run.verdict_sound`). No `check_*_statements.py` covers
    math-evidence.
11. PASS: each limit tested at and past its value (153); a digit-limit hit is UNKNOWN for the claim (R-2's v1), never
    a verdict. No budget field until ME-4 (refused as unknown).
12. N.A.: no runtime path changes; the route cases evaluate in about a second of the Lean build.
13. PASS: no test removed; `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.
