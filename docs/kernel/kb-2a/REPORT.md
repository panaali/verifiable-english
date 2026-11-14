# kb-2a step A: the lowering of a document to its core documents (REPORT)

Status: built; trust mutants exit 0; selected run: one failure (assurance manifest classification), fixed and its file rerun (167 passed). HEAD: see `git log -1`.
What changed: one new experimental Lean module, `lean/VE/Experimental/CoreDocument.lean` (the lowering, its refusals,
origins and theorems), and its examples, `lean/VE/Experimental/CoreDocumentExamples.lean`; no Python, Rust or service change.
Open items: none of this task's deliverables. For step B: couplings, narrowings and purposes/markers (section "Gaps").
Signatures: none needed; the trusted growth (+147, K +0, S +0) is signed by standing ruling R16 (DELTA.md row 1).

SIZE: 579 product, 350 tests, 196 other hand-written lines (DELTA 11, FOLLOW-UPS 9, seeded bugs 22, allow 4,
trust-classes 143, trust baseline 7; this report not counted).

## Where and why

- **Path.** The task says `lean/VE/Service/CoreDocument.lean`. The experimental tier kb-1 built is the namespace
  `VE.Experimental` (`tools/check_lean_imports.py`, `EXPERIMENTAL = "VE.Experimental"`, docs/spec/kernel-boundary.md
  section 5), so the module is `VE.Experimental.CoreDocument` in `lean/VE/Experimental/`. Its docstring carries
  `Expires: 2026-12-07`. Step B moves it to the shell when it promotes it.
- **Size.** The task says "at most 500 lines". The module has 579 lines: lines 350-579 are the theorems and their
  helper lemmas. Standing override 1 (no line cap) applies; nothing was cut.
- **Document.lean.** Unchanged. No private definition had to be made public: `check`'s pieces the lowering reads
  (`Env`, `SourceUnit`, `UnitContent`, `listedOf`, `wireJson`, `softCanonical`, `decodedEnvironment`) are already public.

## Types (verbatim)

```lean
structure Origin where
  unit : String
  feature : String
  reading : Option (String × Nat) := none
  deriving DecidableEq, Repr

inductive Body
  /-- A soft rule: one norm object of the soft route's source, as `decodeSoftSource` reads it. -/
  | soft (rule : Json)
  /-- A premise of the slot `P` (`Compose.SlotWellFormed`). -/
  | premise (φ : VE.Formula)
  /-- A judgment term: a base predicate with its decider (`Judgments.admit`); it contributes no premise. -/
  | judgment (term : VE.Judgments.Judgment)

structure Statement where
  body : Body
  origin : Origin

structure CoreDoc where
  environment : Json
  norms : Json
  premises : List VE.Formula
  statements : List Statement

abbrev Choice := List (String × Nat)

abbrev ActiveSet := FrontSet × List (Option VE.Judgments.Content)

structure Coupling where
  id : String
  members : List (String × List String)

abbrev Options := List (Option (String × Body))

structure UnitPlan where
  unit : String
  declarations : List (String × Body)
  set : Option String
  options : Options
```

The lowering:

```lean
def lower (E : Env) (senses : Bool) (records : List VE.Judgments.Rec) (views : List VE.Judgments.UnitView)
    (units : List SourceUnit) (sets : List ActiveSet) (couplings : List Coupling) :
    Except String (List (Choice × CoreDoc)) := do
```

It has no success flag, status word or "admissible" boolean (deliverable 3): its only outputs are the core
documents or a refusal string. No part of `lower`'s output is a `Bool`: the module's Boolean tests (`compatible`, `declared`,
`readingNamed`) only feed a refusal or the choice filter.

## Theorems (verbatim; each proved from the checks `lower` makes, no `sorry`)

```lean
theorem lower_origin_units {E : Env} {senses : Bool} {records : List VE.Judgments.Rec}
    {views : List VE.Judgments.UnitView} {units : List SourceUnit} {sets : List ActiveSet}
    {couplings : List Coupling} {cs : List (Choice × CoreDoc)}
    (h : lower E senses records views units sets couplings = .ok cs) :
    ∀ d ∈ cs,
      (∀ st ∈ d.2.statements, st.origin.unit ∈ units.map (·.id) ∧
        ∀ r i, st.origin.reading = some (r, i) →
          ∃ x ∈ sets, x.1.id = r ∧ x.1.unit = st.origin.unit ∧ i < x.1.readings.length) ∧
      ∀ p ∈ d.1, ∃ x ∈ sets, x.1.id = p.1 ∧ x.1.unit ∈ units.map (·.id) ∧ p.2 < x.1.readings.length

theorem lower_readings_distinct {E : Env} {senses : Bool} {records : List VE.Judgments.Rec}
    {views : List VE.Judgments.UnitView} {units : List SourceUnit} {sets : List ActiveSet}
    {couplings : List Coupling} {cs : List (Choice × CoreDoc)}
    (h : lower E senses records views units sets couplings = .ok cs) :
    ∀ x ∈ sets, ∃ opts, readingOptions E (wire E.lower) x = .ok opts ∧
      (opts.map (·.map Prod.snd)).Nodup

theorem lower_choices {E : Env} {senses : Bool} {records : List VE.Judgments.Rec}
    {views : List VE.Judgments.UnitView} {units : List SourceUnit} {sets : List ActiveSet}
    {couplings : List Coupling} {cs : List (Choice × CoreDoc)}
    (h : lower E senses records views units sets couplings = .ok cs) :
    cs.map Prod.fst = compatibleChoices couplings sets ∧
    cs.length = (compatibleChoices couplings sets).length ∧ cs.length ≤ 64 ∧ (cs.map Prod.fst).Nodup

theorem lower_names_bound {E : Env} {senses : Bool} {records : List VE.Judgments.Rec}
    {views : List VE.Judgments.UnitView} {units : List SourceUnit} {sets : List ActiveSet}
    {couplings : List Coupling} {cs : List (Choice × CoreDoc)}
    (h : lower E senses records views units sets couplings = .ok cs) :
    ∀ d ∈ cs,
      (∀ φ ∈ d.2.premises, ∀ p ∈ VE.Norms.preds φ, (E.rv.environment.predicates p).isSome) ∧
      ∀ st ∈ d.2.statements, ∀ j, st.body = .judgment j → (E.rv.environment.predicates j.name).isSome

theorem lower_parts {E : Env} {senses : Bool} {records : List VE.Judgments.Rec}
    {views : List VE.Judgments.UnitView} {units : List SourceUnit} {sets : List ActiveSet}
    {couplings : List Coupling} {cs : List (Choice × CoreDoc)}
    (h : lower E senses records views units sets couplings = .ok cs) :
    ∀ d ∈ cs, d.2 = CoreDoc.of (wire E.lower) d.2.statements
```

(a) is `lower_origin_units`, (b) `lower_readings_distinct`, (c) `lower_choices` (`cs.length` is the number of
compatible choices, at most 64, no choice twice), (d) `lower_names_bound` (through the decoded vocabulary
`E.rv.environment`). `lower_parts` says the core document's `norms` and `premises` are its statements' soft rules and
premises in order. `python3 lean/audit.py`: PASS, only the standard axiom allowlist (/tmp log, last line
"PASS: 874 source files; 9977 named theorem declarations audited").

## What the lowering does with each piece of decoded data

`UnitContent` constructors (Document.lean:1273):

| Constructor | Lowering |
|---|---|
| `formula φ` | one premise `φ` of `P`, origin (unit, `facts`); a formula naming a regulated predicate is refused `UnsupportedLowering: unit <u> feature facts: a formula over the regulated predicate <p> ...` |
| `soft r` | one soft rule, `wire r` (the JSON the soft relay sends, as `DocumentChain.requestOf` does), origin (unit, `soft-norms@0`) |
| `norm n` | one soft rule `wire (encodeNode n)`, origin (unit, `norms@0`), only when `decodeSoftNorm` over the core environment reads it back as exactly `{ toNode := n, mode := .strict, rank := none, alterable := [], exception := none, hard := false }` (example "A strict norm", `#guard` comparing name, predicate, sign, guard, carve-outs, mode, exception and hardness). Under a plain `norms@0` environment (no `soft-norms@0`) the soft decoder refuses the environment, so it is refused `UnsupportedLowering: unit <u> feature norms@0: a strict norm has no soft rule: ...`: no embedding is invented |
| `rights b` | refused `UnsupportedLowering: unit <u> feature rights@0: a rights block has no row` |
| `cardinality s` | refused `UnsupportedLowering: unit <u> feature cardinality@0: a cardinality statement has no row` |
| no content (register labels, headings) | no statement |

A unit whose `open` meaning lists judgment terms first gets one `judgments@0` declaration per listed term (in the
order listed), never a premise; then its content's statement. A unit under an active reading set gets, per choice,
the statement of the chosen reading (origin with the set id and the reading index); a pending reading gives none.

Front matter and environment layers:

| Layer | Lowering |
|---|---|
| environment (`E.lower`) | the core document's `environment` is `wire E.lower`, as the soft relay sends it |
| profiles | the rows' profiles (`data@0`, `documents@1`, `judgments@0`, `norms@0`, `readings@1`, `relational-fol@0`, `soft-norms@0`); any other (rights, cardinality, norm-defaults, scope, events, ...) is refused `UnsupportedLowering: unit <first unit> feature <profile>: the table has no row for it` |
| `senses` | refused (feature `senses`) |
| alternatives or risk block (`E.block`) | refused (feature `alternatives or risk block`) |
| `events@0`, cardinality environment, W3 `definitions` | refused (features `events@0`, `cardinality@0`, `definitions`) |
| judgment records (`judgments@0`) | `Judgments.admit` over them, then `Judgments.status` on every unit view; their refusals (`JudgmentUnbound`, `JudgmentNotChecked`, `JudgmentNotListed`, `JudgmentListedUnused`, ...) are returned unchanged |
| active reading sets (`(FrontSet × candidates)`) | one core document per compatible choice; refusals `ReadingsCollapsed`, `ResourceLimit` (more than 64 compatible choices, or more than 4096 combinations to enumerate), `UnknownPart` (a set naming a unit the document lacks, candidates and readings of different counts, two sets with one id or unit) |
| couplings (`Coupling`) | a choice is kept when the readings it chooses in each coupling's sets carry at most one label; `UnknownPart` for a coupling naming a set that is not active or labelling a set's readings in the wrong number |

## Gaps: where the decoded data did not carry what the lowering needs (for step B)

1. **Couplings.** `check` gates couplings (Document.lean:366) but does not decode them. The lowering takes its own
   `Coupling` (set id and one label per reading). The readings route owns the coupling rule
   (`VE.Readings.couplingHolds`, lean/VE/Readings/Choice.lean:78, over `VE.Readings.Doc.Coupling` with an axis and
   candidate labels; decoded by `VE.Readings.SupWire.decodeCouplings`). The lowering's `compatible` states the same
   rule over its own type. Step B must build the input from the route's decoder and, to keep one owner, replace
   `compatible` by the route's rule (or tie the two by a theorem).
2. **Narrowings.** Not an input. The readings route's `compatible` also reads narrowings (`narrowingHolds`).
   A caller must not pass a document with narrowings in force until step B adds them. Conservative choice taken here:
   no narrowing semantics invented.
3. **Purposes and markers.** `check`'s decoded data has none (no purpose or marker field in `Env`, `SourceUnit` or
   `UnitContent`), so the lowering has no such references to check. A profile that carries them is outside the rows
   and is refused as a document feature.
4. **The judgment term in a soft rule's exception.** `Judgments.softContent` reads a soft rule's guard and carve-outs
   only, so a rule whose exception reads a term does not depend on the term and need not list it (example "A judgment
   term in a rule's exception"): the term is declared by the unit that lists it, and the fact unit about it is one
   premise with that unit's origin.
5. **Unit views.** `judgedViews` (Document.lean:2258) is built inside `check`; the lowering takes the views as an
   argument and refuses views that are not the document's units (`UnknownPart: the unit views are not the document's units`).

## Examples (`CoreDocumentExamples.lean`, all `#guard`)

One document per table row (soft-norms@0, facts, judgments@0 with one and with two listed terms, register labels);
a judgment term in a rule's exception beside a fact about it (one premise, origin `u2`; the rule mentions `redacted`;
the core document decodes with `decodeSoftSource`); a two-reading set (two core documents that differ exactly in
that unit's statement); couplings (two coupled sets: two choices with their statements; three sets coupled by one
coupling or by two sharing a set; a coupling with no members constrains nothing; couplings that leave no choice are
refused); each refusal (`UnsupportedLowering` for regulated predicates in either position and each regulated
predicate, rights, cardinality, norm-defaults, alternatives, senses, a strict norm without embedding;
`ReadingsCollapsed`; `UnknownPart` for a set's missing unit, a coupling's missing set, an undeclared predicate, views
that are not the units; `ResourceLimit` at 65 and 128 choices and 8192 combinations, 64 choices accepted; the judgment
refusals on the first and the last of two units); the strict norm accepted with equal fields; the soft relay's fuel
(`wire` drops a null inside 256 arrays and keeps it inside 257); `judgments@0` first or last in the profile list.

## Seeded bugs (`docs/kernel/kb-2a/seeded-bugs.json`; Lean only, the only language changed)

| Bug | File | Caught by |
|---|---|---|
| (a) the last fact unit's premise dropped (`units.dropLast`) | lean/VE/Experimental/CoreDocument.lean | the row examples, e.g. the facts row `#guard` (CoreDocumentExamples.lean:137) |
| (b) a premise takes the origin of the unit before it | lean/VE/Experimental/CoreDocument.lean | the facts row (137), the judged fact's origin (186, 189), the reading examples (236-260) |
| (c) `readingsOf` without `distinct` | lean/VE/Experimental/CoreDocument.lean | `lower_readings_distinct` does not build (CoreDocument.lean:518) |
| (d) `setFault` accepts a set naming a missing unit | lean/VE/Experimental/CoreDocument.lean | `preliminaries_sets`, so `lower_origin_units`, does not build (CoreDocument.lean:463) |

Each was planted alone, rebuilt (`lake build VE.Experimental.CoreDocument` or `...CoreDocumentExamples`, exit 1),
and restored with `git checkout`.

## Trust mutants (R16; `docs/kernel/kb-2a/trust-mutants.json`, allow file `trust-mutants-allow.json`)

`zsh manage-agents/mac-pytest.sh --trustmut -- --max-mutants 1000 --test lean/VE/Experimental/CoreDocumentExamples.lean
--allow docs/kernel/kb-2a/trust-mutants-allow.json --json docs/kernel/kb-2a/trust-mutants.json` on the merged HEAD:
186 mutants of 13 definitions, 172 KILLED, 12 INVALID, 2 ALLOWED, 0 SURVIVOR, 0 UNKNOWN, exit 0 (ve-cloud-2).
The two allowed are `compatible`'s `[]` in place of `labels` and of `labels.eraseDups.length`, which Lean cannot
elaborate (no element type for `BEq`/`LE`). History: the first sweep (with `CoreDocument.lean` itself as a `--test`
file, so its own theorems' failures read UNKNOWN) left 50 SURVIVOR and 42 UNKNOWN; the module was then reshaped (one
body per unit instead of the `Plan` inductive, the fuel in one `wire`, a single structural comparison in
`strictRule`, typed lambdas so `[]` mutants elaborate) and examples added that kill the rest.

## Runs (each once, on the code as committed)

- `lake build` (full): exit 0, "Build completed successfully (1440 jobs)".
- `python3 lean/audit.py`: PASS.
- `uv run python tools/regen_generated.py --write` then `--check` after the main merge: 41 entries, nothing stale.
- `uv run python tools/kernel_closure.py --check docs/kernel/closure-baseline.json`: PASS, kernel 9552 <= 9552,
  verdict writers outside the kernel 56 <= 56, `document` path spec lines 34821 (the baseline's 34821).
- `uv run python tools/check_lean_imports.py`: exit 0 (the experimental module is unreachable from the service).
- `uv run python tools/trust_map.py --check`: PASS, against f0f2b1a0b6eb K +0, S +0, trusted +147 (allowance 147).
- Selected tests: `MAC_PYTEST_NO_DEFER=1 zsh manage-agents/mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`
  on ff07374e0d (clean tree), ve-cloud-2, 7722 s: exit 1, one failure,
  `tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified` (the two new Lean files build
  JSON and were not classified in `ve/assurance-manifest.json`); every other selected file passed (log /tmp/kb2a-select.log).
  Fixed by two hand-reviewed `other_json` entries (the manifest's writer only restores its layout); rerun:
  `uv run pytest -q tests/test_assurance_manifest.py`, 167 passed; `tools/assurance_manifest.py --check` exit 0;
  `check_assurance_layout()` and `check_assurance_pins()` 0. Not on main's known-red list.
- Not run: the full gate (the chain runs it on the final HEAD).

## Acceptance

| Item | Tag | Evidence |
|---|---|---|
| `lake build`, `python3 lean/audit.py` pass | AGENT | Runs |
| `kernel_closure.py --check` with kernel and `document` figures unchanged | AGENT | Runs |
| experimental boundary check | AGENT | `tools/check_lean_imports.py` exit 0 |
| selected tests pass, no test changed | AGENT | Runs; `git diff main...HEAD --stat -- tests` is empty |
| generated Lean files regenerated with their tool | AGENT | `tools/lean_statements.py`, `tools/regen_generated.py --write` |
| no Python change; `Document.lean` unchanged | AGENT | `git diff main...HEAD --stat -- ve lean/VE/Service` lists only `ve/assurance-manifest.json` (two data entries classifying the new Lean files, required by `tests/test_assurance_manifest.py`) |

## Notes for the DRI

- Gap 1 (couplings) is a one-owner question for step B: the lowering restates the readings route's coupling rule
  over its own `Coupling` type. Nothing calls it today.
- The strict-norm embedding exists only where the environment lists `soft-norms@0`; a plain `norms@0` document's
  strict norms are refused (the soft decoder requires the profile). Step B decides whether such documents keep their
  own route.
- The lowering re-runs `Judgments.admit` and `Judgments.status` from the records and views `check` decodes; step B can
  pass `check`'s own results instead to avoid the second run.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained Lean answers: N.A., no relayed answer, schema or route (the module is unreachable).
2. Deliverables built, no rule broken: PASS, deliverables (1)-(5) above with their examples and theorems; no Python
   copy, no report test (`git diff main...HEAD --stat -- tests ve` empty).
3. Tests and gates can fail: PASS, seeded bugs (a)-(d) and `docs/kernel/kb-2a/trust-mutants.json` (exit 0).
4. Python, Lean and Rust agree: N.A., Lean only, no route output changed.
5. R8 binding: PASS for the lowering's own references, examples "UnknownPart: ..." (`CoreDocumentExamples.lean`
   refusals section); no relayed field.
6. Gate evidence matches the final HEAD: PASS, synced with main (merge 58820451f7); trust evidence on the merged HEAD;
   the gate is the chain's.
7. No unsigned item: PASS, DELTA rows cite R16 and R12.
8. Every user-visible change in DELTA: PASS, none is user-visible (unreachable module); trust and generated rows recorded.
9. Test selection: PASS, the final selected run (Runs) selected the Lean-wide tests and caught the manifest classification (`tests/test_assurance_manifest.py`).
10. Lean statements say what is claimed: PASS, seeded bugs (c), (d) break `lower_readings_distinct` and
    `lower_origin_units`; statements quoted above from the source.
11. Budgets fail closed: PASS, `ResourceLimit` examples at 65, 128 choices and 8192 combinations (refused before
    enumeration); 64 accepted.
12. No CPU or memory regression: PASS, nothing in the service calls the module; enumeration bounded by 4096 combinations
    before it starts.
13. Removed or renamed tests: N.A., none.
14. Both directions, cited evidence, spec re-read: PASS, each refusal has an accepted neighbour (64 vs 65 choices,
    strict norm accepted vs refused, coupled vs uncoupled, `judgments@0` first/last); spec re-read: the table rows
    against manage-agents/fable-team/architect/kb-2a/DESIGN.md:42-48, refusal words against the task text.
15. No overclaim / no silent cut / every check can fail / limits charged before work: PASS, trust mutants (172 KILLED),
    no deliverable cut, the combination bound is checked before `allChoices` runs (example with 13 sets).
