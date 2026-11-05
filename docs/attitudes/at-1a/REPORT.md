# at-1a report: the attitudes Lean core, part one (spec 2.1-2.4)

Status: done; deliverables (1)-(5) built; selected tests 105/542 units passed; the chain's gate passed at 18f18b4e, and will gate this final HEAD.
Changed: new lean/VE/Attitudes/{Scale,Syntax,Examples}.lean (spec 2.1-2.4, `table_reviewed`, F-AT0-3/C-a/C-e guards), lean/ATTITUDES.md; the pre-review fix adds a Python layer-policy mutant and focused test.
Signatures: none reserved; S +221 (K +0) SIGNED by the DRI (reviews/dri-decisions-20261104-at-1a.md item 1); layer row likewise (-layer.md).
Open: cut-back row `at-1a-tie` (blocked by at-1b); hand-written size about 960 lines, over the ~600 guide (section "Size").
Next item: at-1b (elaboration and `checkAtt`, spec 2.5-2.6, with the five `WellFormedAtt` statements).

Plan: docs/spec/attitudes-PLAN.md "AT-1. Lean core" (lines 792-~1000), on main. Spec: docs/spec/attitudes.md
(draft 8). The spec's Lean governs where it and the plan's block differ (plan :803). Statement gate: AT-0 is done
(reviews/dri-decisions-20261103-fp-attitudes-r2.md item 3 opened this structure row). Every definition equals the
spec's text after whitespace normalisation (section "Spec re-read"), so nothing was stopped on.

## Deliverables

| Task line | Delivered | Commit | Test or check |
|---|---|---|---|
| (1) `Scale.lean` (2.1): `Word`, `Item`, `Scale`, `Scale.toOrder`, `Scale.atLeast` through QS-1's `Order.atLeast`, `Table`, the frozen `table`, `Table.reviewed`, `scaleCaps`, and `table_reviewed` with its `#guard` | as listed, plus the spec's `Table.words`, `Table.scale`, `Table.hasPair`, `e1Words`. `table_reviewed` is proved `by decide` (spec 6.1 proof notes), and `#guard table.reviewed` is at Scale.lean:90 | 2fac8cabf | `lake build VE.Attitudes.Scale`; Examples.lean:151 (the review on four tables) |
| (2) `Syntax.lean` (2.2-2.4): `Mode`, `Mode.slug`, `Cond`, `AFormula`, `ARule`, `AttDoc` with `lex` and `parts`, `Key`, `Key.sorts`, `Cond.key`, `AFormula.conds`, `ruleContext`, `condsOf`, `partsOf`, `keys` over `condsOf A ++ partsOf A`, `name`, `keyOf`, `envAtt`, `baseEnv` and the rest | as listed, plus `Mode.words`, `Lex`, `AttDoc.scale`, `baseEnvAtt` (the rest of 2.2-2.4) | 2fac8cabf | `python3 docs/attitudes/at-1a/spec_text_check.py`: `52 pieces, 0 missing` |
| (3) `Examples.lean`: a `#guard` for every value 2.1-2.4 compute on F-AT1. The keys and names (fresh, at most 64 bytes, distinct from the regulated and defined names); `keyOf` of each name; each key's sorts; `envAtt`'s added predicates; `Scale.atLeast` on the frozen table (nothing admitted before E1 and E2 report); C-e's part, with `c_e` in its name | F-AT1: keys :218, sorts :220, names :222, freshness/64 bytes/distinctness :224, `keyOf` :227. `envAtt` :252-:260, `baseEnv`/`baseEnvAtt` :262-:269. Scale :151-:188. "Before E1 and E2 reported" is `preReportTable` (:169: no word, no two words related); the frozen table's three refused words are related to no admitted word (:167). C-e: `c_e_node`, `c_e_part`, `c_e_guard`, `c_e_three`, guards :241-:247, :256. Also F-AT2, F-AT3, F-AT0 and C-a's two conditions | 2fac8cabf, 4405a6846, b0df5d0af | `lake build VE.Attitudes.Examples` |
| (4) `lean/ATTITUDES.md`: the module map of the three parts, the owner of each spec section, the stand-ins in force | written | 71d7fc542 | — |
| (5) imports and generated files only through `regen_generated.py --write` (R12) | `regen --write` wrote `lean/VE/Audit.lean`, `axioms.txt`, `statements.txt`, `declarations.txt`, `predicates.txt` and the code map; `lean/VE/Route/frozen-sources.sha256` did not change. `lean/VE.lean` has no writer: regen lists `lean-roots` as `[union]` with write `-`, so its one import line is written by hand (as the plan's "(import union)" says) | f31de636d | `regen_generated: wrote 35 entries` |
| Seeded bugs (three Lean, one Python) and a mutant per new trusted definition | section "Seeded bugs and mutants" | db3d08cd9; ec677229d | `docs/attitudes/at-1a/mutants.json`, `trust-mutants.json`; `tools/test_layer_policy.py::LayerSelectionTests::test_attitudes_modules_share_the_english_lexicon_layer` |
| R16 trust record and FOLLOW-UPS row under "## at-1a" | the DRI signed +221 beyond R16 (section "Trust"); FOLLOW-UPS.md row written | db3d08cd9 | `tools/trust_map.py --check` rc 0 |

Not delivered: nothing. Kept out on purpose: `lean/VE/Attribution/`, and at-1b's and at-1's modules.

## Spec re-read

- `python3 docs/attitudes/at-1a/spec_text_check.py`: `52 pieces, 0 missing`. Every docstring and declaration of the
  four Lean blocks of attitudes.md 2.1 (lines 268-336), 2.2 (371-454), 2.3 (465-505) and 2.4 (518-534) appears,
  whitespace-normalised, in Scale.lean + Syntax.lean. Opposite direction: `"attitude__"` in `name` gives
  `52 pieces, 1 missing`, rc 1.
- `table` against spec :303-:328 and the stub's S1 (identical): five words, ten pairs, premises 1 and 2, premise 3 for
  all five. Examples.lean:156 and :172.
- `keys` against spec :460-:462 ("rules, then guard before carve-outs, pre-order; then the reading-set parts").
  Examples.lean:207 (carve-outs after the guard), :242 (`attitudes__wants__1` after the rules' three keys).
- C-e against spec 7.1 :1738: names `attitudes__knows__1`, `attitudes__intends__1`,
  `attitudes__thinks_quite_likely__1`, `attitudes__wants__1` (Examples.lean:242). The part's claim and D14c are at-1b's.
- F-AT0 against spec 7.1 ("0 keys … `envAtt` agrees with `E` on every declared name and on three generated-looking
  names"). Examples.lean:239 and :259.
- `Scale.atLeast` against spec 1 (owners row "Order closure": `Scale.atLeast` is `Order.atLeast`, no second
  closure). Scale.lean:24 calls `σ.toOrder.atLeast`.
- `lex`'s owner against spec 1 (row "English lexical data"). `Lex` holds `VE.EnglishGrammar.Env`, `Overlay`,
  `Lexicon`, used as on main.

## Seeded bugs and mutants

Each Lean bug was planted, the build of `VE.Attitudes.Examples` run, and the file restored (`cmp` against a copy).
For the changed Python file, `VE.Attitudes.*` was moved from layer 3 to layer 2; the focused pytest test failed in
three subtests (exit 1). Restoring layer 3 made it pass (one test, three subtests). The test also checks that
`VE.EnglishGrammar.Lexicon` is at layer 3.

| Bug (task) | File | Failing check |
|---|---|---|
| `Scale.atLeast` without reflexivity (`toOrder.above`) | lean/VE/Attitudes/Scale.lean | Examples.lean:164 (`table.words.all (fun w => table.scale.atLeast w w)`) |
| `name` without the key's slot sort (index over keys with `slotSort` erased) | lean/VE/Attitudes/Syntax.lean | Examples.lean:236 (C-a's two keys, which differ only in `slotSort`: names and `Nodup`). F-AT1's three keys differ in mode, so its distinct-names guard (:224) cannot see this bug; C-a is the fixture where two keys differ only there |
| `keys` over `condsOf A` only | lean/VE/Attitudes/Syntax.lean | Examples.lean:242 (C-e's names), :247, :256 |
| `VE.Attitudes.*` at layer 2 instead of 3 | tools/layer_policy.py | `tools/test_layer_policy.py::LayerSelectionTests::test_attitudes_modules_share_the_english_lexicon_layer` (three failed subtests) |

Mutants per new trusted definition. `docs/attitudes/at-1a/trust-mutants.json` (head b0df5d0af, the final Lean;
later commits change no Lean file) has 328 KILLED, 0 SURVIVOR, 0 UNKNOWN, 27 INVALID and 40 ALLOWED, with kills in
20 definitions. Every ALLOWED row was checked against its raw status. 36 are UNKNOWN mutants Lean refuses to
elaborate (type errors, constructors dropped while a `match` still names them). 4 are equivalent survivors: the
`take 1` and `reverse.take 1` cuts before `.isEmpty` at Scale.lean:56, and the two `dropLast` cuts before `idxOf` in
`name`. The reasons are in
`trust-mutants-allow.json`. The first run left 71 survivors and 36 UNKNOWN. The fixtures added in 4405a6846 and
b0df5d0af kill every killable one: tables failing one conjunct of `Table.reviewed` at a time, and documents with
three entries. The definitions the tool has no operator for are hand-planted (`mutants.json`): `Scale.toOrder` is
killed at Scale.lean:90 and by the `table_reviewed` proof, `Mode.words` at :195, `AttDoc`'s `parts` default at
:241, `envAtt` at :252 and `baseEnvAtt` at :266. No mutant of the types `Word`, `Item`, `Scale`, `Table`, `Mode`,
`Cond`, `AFormula`, `ARule`, `Lex` or `Key` elaborates and changes a value. Two field-name swaps were tried
(`Table.factive`/`knowsBelieves`, `ARule.name`/`pred`) and changed nothing, since every fixture builds by name; they
are recorded as such, not as kills.

Commands: `zsh manage-agents/mac-pytest.sh --trustmut -- --max-mutants 1000 --allow
docs/attitudes/at-1a/trust-mutants-allow.json --rescore … --json docs/attitudes/at-1a/trust-mutants.json` (third run,
exit 0). The hand mutants were run by a script applying each edit, building, and restoring.

## Trust

`uv run python tools/trust_map.py --check` on the final HEAD, rc 0: `K +0, S +221, D +0, G +0, tied +0, unclassified
+0`. That is `VE/Attitudes/Syntax.lean` +145 and `VE/Attitudes/Scale.lean` +76, with Examples.lean's 45 fixture
definitions classed T. `tools/trust-classes.json` classes 35 declarations S (13 in Scale.lean, 22 in Syntax.lean),
as attribution's syntax is classed. The growth is over R16's 150. The DRI signed it as option A, bounded at S ≤
+230, K +0 (reviews/dri-decisions-20261104-at-1a.md item 1). The allowance was recorded with that signature, DELTA
row 1 written, and `review-ready.py --delta-dri-needed` answers `no DELTA row reserved for the DRI`. The cut-back
row `at-1a-tie` (decision item 3) is in the manage-agents FOLLOW-UPS.md "## at-1a" row with the ties pass.

## Layer

`tools/check_lean_imports.py` refused `VE.Attitudes.Syntax -> VE.EnglishGrammar.Lexicon`. That import comes from the
spec (`AttDoc.lex`). The DRI signed one `tools/layer_policy.py` row placing `VE.Attitudes.*` at layer 3
(reviews/dri-decisions-20261104-at-1a-layer.md item 1), and `tools/lean-layer-exceptions.json` is unchanged. The
import check now prints `Lean layer graph kept (768 modules, 22 reviewed legacy edges)`, and
`tests/test_architecture_docs.py tests/test_soft_norms_conformance.py` give `65 passed`. Merge note: wg-2 adds rows in
the same part of `lean_layer`; keep both.

## Size

`git diff --numstat $(git merge-base HEAD main)`, without generated files and the tool-written trust-mutants.json:

| Kind | Lines |
|---|---|
| Spec Lean, verbatim | Scale.lean 92, Syntax.lean 166 |
| Guards and fixtures | Examples.lean 319 |
| Docs | ATTITUDES.md 33, DELTA.md 16, this report |
| Evidence | mutants.json 12, trust-mutants-allow.json 20, spec_text_check.py 24 |
| Side tables | trust-classes.json 92, trust-baseline.json 7, layer_policy.py 2, VE.lean 1; the pre-review fix adds 6 test lines |

The total is about 960 with this report (now over 160 lines), over the ~600 guide. The spec's Lean cannot shrink. 49 of the
guard lines (Examples.lean:271-319) are the trust-mutant fixtures R16 requires. The DRI ruled out a split (decision item 2: it adds a merge
without lowering the total).

## Pilot bytes

None expected: a structure row (bytes 0, fp-attitudes-r2 item 2). No route, verdict or wording changes, so nothing is
claimed.

## Runs

- `lake build` (full) on the final Lean: `Build completed successfully (1284 jobs)`. `python3 lean/audit.py`:
  `PASS: 768 source files; 8406 named theorem declarations audited …`.
- `zsh manage-agents/mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` on 5e74390b8: `105/542 test
  units`. Shards 1-5 passed 26, 25, 23, 20 and 19 units, 0 failed. The selector deferred
  `tests/test_safety_framework.py` to the chain gate. The first run on db3d08cd9 stopped at the import check (section
  "Layer") before any test ran.
- `uv run python tools/gate_collection.py --check --prebuilt`: `0 added, 0 removed by a trailer, 0 refused, 0 stale
  and 0 malformed`.
- Pre-review Python mutant: `UV_CACHE_DIR=/tmp/ve-at-1a-uv-cache uv run pytest -q tools/test_layer_policy.py -k
  attitudes_modules_share_the_english_lexicon_layer` failed with `3 failed, 1 passed` while the row returned layer 2,
  then passed after restoration (`1 passed, 3 subtests passed`). The full `tools/test_layer_policy.py` passed
  `49 passed, 110 subtests passed`.
- No test in manage-agents/main-known-red.txt was touched. The full gate was not run here; the chain runs it.

FOLLOW-UP: at-1a-tie: tie `keys`, `name`, `keyOf`, `envAtt` and `baseEnvAtt` (after at-1b), and `Cond.key`,
`AFormula.conds`, `condsOf` and `partsOf` (after at-1), out of S. Target: at-1a net trusted growth ≤ +150.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is relayed; no service mode, schema or relay changes.
2. PASS: section "Deliverables" lists each task line with its commit and check. The one Python code row
   (`tools/layer_policy.py`) is DRI-signed and has a killing test in `tools/test_layer_policy.py`;
   `tools/trust-classes.json` is the R16 classification. No report test was added.
3. PASS: three Lean seeded bugs fail their guards (Examples.lean:164, :236, :242); one Python seeded bug fails
   `test_attitudes_modules_share_the_english_lexicon_layer`. Trust mutants: 0 SURVIVOR, 0 UNKNOWN
   (`docs/attitudes/at-1a/trust-mutants.json`); hand mutants in `mutants.json`.
4. PASS: `test_attitudes_modules_share_the_english_lexicon_layer` checks the layer-policy Python row;
   Lean is new and read by no route. No Rust code changed.
5. N.A.: no relayed field.
6. N.A.: the chain owns the final HEAD gate after handoff; its previous gate passed at 18f18b4e.
   `trust-mutants.json` names b0df5d0af; later commits change no Lean file
   (`git diff --stat b0df5d0af HEAD -- lean/` is empty).
7. PASS: DELTA row 1 cites the DRI's decision file; `review-ready.py --delta-dri-needed` gives `no DELTA row reserved
   for the DRI`.
8. PASS: no user-visible output changes (no route reads the modules); DELTA says so.
9. PASS: the selection runs `lake build`, which builds Examples.lean's guards (log line `+ lake build`), and
   `tests/test_architecture_docs.py` for the layer row.
10. PASS: `table_reviewed` is `by decide`. The `H-toOrder` mutant makes `decide` refute it (Scale.lean:88), so the
    theorem is about the value computed.
11. N.A.: no evaluator, budget or deadline.
12. N.A.: no runtime path changes.
13. PASS: `tools/gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.
14. PASS: opposite directions are guarded. Reviewed and refused tables (:283, :287). Fresh names, and `keyOf` =
    `none` elsewhere (:224, :227). `envAtt` adds names and agrees elsewhere (:252, :253). `spec_text_check.py`
    passes and fails (section "Spec re-read"). Every claim here cites its command.
