# The kernel boundary: what VE trusts, and how a feature gets in

Status: architect decision, 2026-11-11 (Fable architect seat), for the DRI to adopt. Branch
`fable/arch-kernel-1`. It changes no product code. It adds a measuring tool, a registry and this
specification, and it names the build work that follows (section 7).

Labels: **(M)** measured on main `97b3c7999a` with the commands in section 1; **(S: file)** sourced;
**(A)** assumed.

## 0. Decisions

1. **The trusted base is read off theorem statements, not off a class table.** A *verdict path* is a
   service mode's way to a verdict. Its trusted lines are its *spec* (what the acceptance theorems
   say, transitively) plus its *wrap* (what runs between the wire and the code the theorems are
   about). `tools/kernel_closure.py` measures both from the compiled Lean environment (section 2).
2. **The kernel is four paths that already exist:** certificate replay, the route, norms and soft
   norms. Together they are **9,565 lines (M)**, under the 10,000-line target. The five frozen keys
   rest on 17,355 lines (M): these four paths plus wire code around two proved evaluators
   (`metered`, `quantity`) that no theorem covers yet (section 1.3).
3. **Only the kernel states a verdict.** Every other mode is *shell*: it may elaborate, search,
   display and refuse, and it may show a verdict only as a row the kernel itself produced for a
   case the answer carries (the carry rule, section 3). Today 54 definitions write a verdict token
   and 51 of them, in 25 modules, are outside the kernel (M); that count goes to zero.
4. **One statement form.** A document's checked content is one core document: definitions, rules
   (soft-norm nodes) and premises over one vocabulary, `(X : SoftDoc, P : List Formula)`, whose
   acceptance theorem is already proved for any `X` and any `P` (`VE.Compose.slot_route_acceptance`).
   Features combine by lowering into it, never by pairing two wrappers (section 4).
5. **Three doors, three tiers.** A feature enters by lowering (the default; no kernel change), by a
   logic extension, or by a new claim kind (both rare, both signed). It lives in one of three tiers:
   experimental (unreachable from the service), shell, kernel (section 5).
6. **A ratchet that cannot go stale.** The kernel total may not grow without the architect's
   signature in the same change; the count of verdict writers outside the kernel may not grow at
   all (section 6).

What this replaces: the per-pair refusals of `lean/VE/Service/Document.lean:1166-1180`, the stack
whitelist `VE.Compose.Contract.listedStacks` with `RouteFacts … | _ => False`
(`lean/VE/Compose/Contract.lean:181-184`), and the profile-composition (PC) lineage's plan to prove
one route per stack. The Lean it proved (`Compose/Slot.lean`) is kept: it is the core document.

## 1. What was measured

### 1.1 The old number is stale and counts the wrong thing

| Quantity | Value | Source |
|---|---:|---|
| Trusted lines quoted in both reviews | 50,034 | S: `docs/trust-baseline.json` `budget` (997 + 9,958 + 39,079) |
| Trusted lines by the same tool today | **63,068** | M: `python3 tools/trust_map.py --check` (984 K + 14,795 S + 47,289 untied [V]) |
| Lean lines | 267,229 in 843 files | M: same run |

The baseline file is 13,034 lines behind because the merge train's `--write` has not run; the
check passes because it compares a branch with its base commit, not with the file. The tool's
output says so. More important, the number is a hand-kept classification of every declaration
(`tools/trust-classes.json`): it counts a decoder as trusted until someone records a tie by hand,
and only 2,261 lines are recorded as tied although about 115 theorems are stated on the runners (M:
section 1.2). It cannot tell a small kernel with a large shell from a large kernel.

### 1.2 The statement-closure measure

Commands (from the repository root, after `lake build VE`):

```
python3 tools/kernel_closure.py --out docs/kernel/closure-baseline.json
```

| Path | Tier | Theorems | Spec | Wrap | Lines |
|---|---|---:|---:|---:|---:|
| certificate (`checkCertificate`) | kernel | 4 | 1,709 | 5 | 1,714 |
| route | kernel | 26 | 4,879 | 15 | 4,890 |
| norms | kernel | 21 | 4,365 | 2,703 | 4,404 |
| softNorms | kernel | 2 | 4,730 | 35 | 4,738 |
| **kernel, distinct lines** | | | | | **9,565** |
| metered (`evaluate-budgeted`) | candidate | 7 | 519 | 3,761 | 3,761 |
| quantity | candidate | 4 | 613 | 1,804 | 2,040 |
| rights | candidate | 2 | 5,598 | 35 | 5,614 |
| alternatives | candidate | 2 | 3,907 | 22 | 3,920 |
| reports | candidate | 3 | 4,395 | 32 | 4,417 |
| normDefaults | candidate | 7 | 5,693 | 5,503 | 6,433 |
| risk | candidate | 6 | 6,159 | 5,669 | 7,839 |
| readingsRoute | candidate | 8 | 9,357 | 20,356 | 24,044 |
| discourse | candidate | 6 | 35,727 | 4,541 | 35,733 |
| document | candidate | 7 | 34,403 | 12,347 | 35,231 |

All (M), saved in `docs/kernel/closure-baseline.json`. Other measurements of the same run:

| Quantity | Value |
|---|---:|
| Code that runs for some service mode (the closure of `VE.Service.runMode`) | 54,500 lines (M) |
| Code that runs for the document mode | 35,142 lines (M) |
| Spec of the abstract route theorems of every family (`*_route_acceptance`, `_countermodel`, `_entails_iff`, `_intended`; 37 theorems) | 4,445 lines (M) |
| Spec of `VE.Norms.norms_route_acceptance` alone | 761 lines (M) |
| Definitions that write a verdict token, outside example, check and schema modules | 54, of them 51 in 25 modules outside the kernel (M) |

Reading the table:

- The kernel paths are small because their theorems are about a runner and say what its answer
  means in terms of the logic. The reader reads the decoders and the meaning, not the runner.
- `document` and `discourse` are large because their theorems are stated in terms of other large
  functions (`checkDocSets j = .ok a → … checkCore j' = .ok a …`): the specification is the
  implementation. This is the wrapper architecture as one number.
- `norms`' wrap is the acts decoder (`VE.Acts.*`, `VE.Grammar.Table`), which the norms runner takes
  as a parameter: its theorems hold for every decoder, so the decoder is read. Section 7, KB-4.

### 1.3 The frozen keys

Each of the five harnesses was run once through `tools/kernel_trace.py`, which records every Lean
service call by mode and case kind ([frozen-keys-20261111.md](../kernel/frozen-keys-20261111.md)). All
five reproduce their recorded answers with exit code 0 (M): RSP 111/126, Preparedness 231/239, FSF
257/262, agent-policy 42/42, eligibility 269/269.

| Fact (M) | Value |
|---|---:|
| Service modes the five keys call | 9 of 43 |
| Calls to `document`, `readingsRoute` or `discourse` (35,142, 20,356 and 35,782 lines of code) | 0 |
| Lean lines under the keys' answers (spec and wrap of every path they call; validators in full) | 17,355 |
| of which in the proved kernel | 9,565 |
| Calls to `metered` `evaluate-budgeted` (proved core 519 lines; 3,761 lines of wire code under no theorem) | 24,945 |
| Calls to `quantity` (proved core 613 lines; 1,804 lines of wire code under no theorem) | 9,452 |
| Calls to `route` `certificate` (kernel) | 12,746 |

So the keyed answers do not depend on the wrapper modes at all, and what separates them from a fully
proved path is about 7,800 lines of wire code around two proved evaluators and three validators
(KB-7, KB-8). In every harness the Python side holds the premises between `soft-elaborate` and
`route certificate`: the harnesses already work by the carry rule of section 3.

## 2. The measure

**Verdict path.** One entry of `tools/kernel-paths.json`:

| Field | Meaning |
|---|---|
| `entry` | the right-hand side of the mode's `runMode_*` pin in `lean/VE/Service/Protocol.lean` |
| `theorems` | the theorems that say what an accepted answer means |
| `subject` | the runner those theorems are about: `∀ j answer, subject j = .ok answer → …` |
| `delegates` | entries of other paths this entry hands cases to |
| `nonverdict` | exits reviewed as carrying no verdict, each with its reason |
| `tier` | `kernel` or `candidate` |

**Spec.** The reading closure of the theorems' statements: every constant a statement mentions, and
for each definition reached its type and body, for each inductive type its constructors. A theorem
reached from inside a definition adds nothing (a proof does not change what a definition computes).
The subject is not read: the theorems hold for whatever it computes.

**Wrap.** Every definition the entry reaches without passing through a subject, a delegate or a
non-verdict exit: code that runs on the way to a verdict and that no listed theorem covers.

**Lines.** The distinct source lines (docstring included) of the declarations in spec and wrap. The
kernel total is the distinct lines over all paths of tier `kernel`.

The tool refuses a registry that names a constant the environment lacks, and reports any
definition on a path that the compiler replaces (`implemented_by`, `extern`) or the kernel cannot
unfold (`partial`, `opaque`); none is on a path today (M).

What the measure does not cover, and what covers it:

| Outside the measure | Covered by |
|---|---|
| Lean's kernel, compiler and runtime; the service's request loop (4,270 lines, M) | the toolchain pin; `VE.Service.runRequest`'s binding theorem |
| Python's envelope, schema and binding checks | `tests/`, the relay mutation gate (unchanged) |
| Whether a theorem's statement is the right one | statement review (unchanged) |
| Whether the English means the core document | section 3's show-back, the fidelity audits (`uc-audit`) |

## 3. The verdict rule and the carry rule

**Verdict rule.** A *verdict token* is a string an answer uses to assert something about a document:
today `CHECKED`, `CONFLICT-FREE`, `CONFLICT`, `INCONSISTENT`, `FOLLOWABLE`, `DILEMMA`, `ALL`, `SOME`,
`NONE` (the registry's `verdict_tokens`; `valid: true` on a certificate row is the kernel's own).
Only a definition inside the kernel may write one. `tools/kernel_closure.py` lists every definition
whose body holds one of these literals and whether it is inside the kernel.

**Carry rule.** A shell mode that wants to show a verdict does not compute it. It elaborates the
request into kernel cases; the kernel answers each case; the answer is a fold of the kernel's rows,
and it carries the cases. In Lean (type-checked on this branch's toolchain; axioms `propext`,
`Quot.sound`; the file is KB-1's `lean/VE/Kernel/Carry.lean`):

```lean
structure Path where
  run : Json → Except String Json
  Meaning : Json → Json → Prop
  sound : ∀ case answer, run case = .ok answer → Meaning case answer

structure Row where
  case : Json
  result : Except String Json

def Path.row (p : Path) (case : Json) : Row := ⟨case, p.run case⟩
def Path.Ran (p : Path) (r : Row) : Prop := r.result = p.run r.case

def shell (p : Path) (elaborate : Json → Except String (List Json)) (fold : Json → List Row → Json)
    (request : Json) : Except String Json :=
  (elaborate request).map fun cases => fold request (cases.map p.row)

theorem shell_sound (p : Path) (elaborate : Json → Except String (List Json))
    (fold : Json → List Row → Json) (request answer : Json)
    (h : shell p elaborate fold request = .ok answer) :
    ∃ rows : List Row, answer = fold request rows ∧
      ∀ r ∈ rows, ∀ a, r.result = .ok a → p.Meaning r.case a
```

`elaborate` does not occur in the conclusion. A mode built as `shell p elaborate fold` therefore has
a spec of `fold` plus `p`'s spec, whatever its elaboration does and however large it is. That is how
a 35,000-line mode gets a spec of a few hundred lines without proving 35,000 lines correct.

What the rule asserts and what it does not:

- It asserts: each verdict shown is the kernel's, about the case shown next to it.
- It does not assert that the case is what the English says. That is *fidelity*. It is shown (the
  answer carries the core statements, which render to English by the existing printers), tested and
  audited, and it may be proved per feature (`Intended` with a faithfulness theorem, as soft norms
  and rights do today). A proof raises a feature's fidelity grade; it does not move the kernel
  number.
- A fold is kernel code. It is listed in the registry and counted. The plain fold `carry view`
  (answer = `{"view": …, "rows": […]}`, rows verbatim) is the default; a fold that derives a unit
  status from rows (`CHECKED` when every row of the unit is an accepted one) is written once, for
  the document mode, and reused.

Soundness is not relaxed. No check, guard or theorem is removed. A verdict that a shell mode
computes today with no theorem behind it becomes a kernel row with one. The one change a reader
sees: an answer that shows a verdict also shows the core case it is about.

**For the DRI:** this fixes what `CHECKED` claims in public wording: "the core statements shown for
this unit were proved", with the translation step visible. `NORTH-STAR.md` line 5 (retained text is
not coverage) is unaffected. If the wording must stay as it is, the alternative is a faithfulness
theorem per feature before its verdicts count, which is the path that produced the present size.

## 4. The statement and composition model

### 4.1 The core document

The kernel checks one kind of document. Its Lean types exist (`lean/VE/Norms/Tree.lean`,
`lean/VE/SoftNorms/Tree.lean`, `lean/VE/Compose/Slot.lean`):

| Statement | Core form | Where |
|---|---|---|
| assertion (a fact, a threshold list, a classification) | a premise of the slot `P`, or of `Γ` when it mentions a rule's predicate | `Compose.SlotWellFormed`, `BaseAdmissibleP` |
| definition | `Definition` (name, arguments, body) | `Norms.Tree` |
| norm (must, must not, may; strict or default; exceptions; precedence) | `SoftNode` on a `Regulated` predicate | `SoftNorms.Tree` |
| open term | a base predicate with its decider (`decidedBy`, the vocabulary's legend); no premise | `SoftNorms.Exception`, the environment |
| attributed content | premises over reified relations (as `VE.Attribution` and `VE.Attitudes` generate) | lowering, door A |
| register label (aspiration, exposition, example) | no core statement: the unit's status is `LABELLED` | the document mode's fold |

Its meaning is one theorem, proved for every soft document `X` and every premise list `P`:

```
VE.Compose.slot_route_acceptance :
  WellFormedSoft X = true → SlotWellFormed X P → ConflictFreeP X P →
  checkCertificate (envAt (soften X) (size (soften X)))
      (backgroundP X P ++ elaborate (soften X).T ++ Γ) φ c = true →
  (every admissible structure in which X's rules, definitions and P hold, and Γ holds, satisfies φ)
  ∧ (for Γ, φ over the base vocabulary: every base structure satisfying P and Γ satisfies φ)
```

with `slot_route_countermodel` and `slot_route_entails_iff` for the other direction. The route under
it is a chain of `VE.Route.Layer`s composed by `Layer.comp` (`comp_faithful`, `comp_expands`): the
proved composition block is the kernel's engine and is already applied; families do not call it.

### 4.2 Composition by construction

Two features on one document are combined by taking the union of what each lowers to:

```
core(doc) = (X with the rules and definitions of every feature, P ++ P' ++ …)
```

and asking the kernel to admit the result. The kernel checks, on the combined document and not on
the features: well-formedness and name uniqueness (`WellFormedSoft`), acyclic dependencies
(`Route.dependencyOrder`), slot well-formedness (`slotCheck`) and conflict-freedom with a replayed
certificate (`ConflictFreeP`). If the combination is ill-formed or conflicting it is refused with
the kernel's diagnostic, which names the clashing statements. No theorem about the pair is needed
and no table row admits it. The only cross-feature rule is a naming one: a lowering writes new
symbols under its own prefix (the existing `Rewriter.Laws.fresh` idea, kept as a lint on the output).

What does not combine this way, and is refused as today: two documents over different logics. A
document is checked over one of the three proved logics (first-order, closure, order with time);
`CONSOLIDATION-PLAN.md` step 3 (one logic with profiles) is the way to remove that limit, and it is
a logic extension (door B), not a wrapper.

### 4.3 The three doors

| Door | Use it for | Kernel change | What must exist before it merges |
|---|---|---|---|
| **A. Lowering** (default) | a new statement family, a new surface form, a rewriter, a reading set, a pack of premises | none | an elaboration to core statements inside `VE.Kernel.shell`; a fidelity pass on built code (section 5); zero new verdict writers outside the kernel |
| **B. Logic extension** | a formula constructor, a theory or a checker the three logics lack (counting, a new arithmetic) | yes, signed | a `Route.Semantics` instance, a `Checker` with `sound`, the route theorem, a wire codec with its round trip; a keyed answer that needs it |
| **C. Claim kind** | a question about a core document that is not entailment, countermodel or conflict | yes, signed, small | a `Meaning` of at most 50 lines (A), its acceptance theorem, its row in the registry |

There is no fourth door. In particular: no new service mode with its own verdict, no new row of
`refuses` pairs in `VE.Compose.profileTable`, no new entry of `listedStacks`, and no new route "for
X with Y".

Readings are door A: a reading set lowers to one core document per compatible choice, and the
answer carries each choice's rows. The superposed route (`VE.Readings.superpose_all_extra`) is an
optimisation that proves all choices with one certificate; it stays as a claim kind (door C) only
if a measured document needs it (the RSP has 30 sets, S: `usecases/anthropic-rsp/coverage.json`).

## 5. Tiers

| Tier | Reachable from the service | May show a verdict | Enters when | Enforced by |
|---|---|---|---|---|
| experimental | no | no | a design passes its meaning-first screen | an import boundary: no module that `VE.Service.Protocol` imports, directly or transitively, imports it (`tools/check_lean_imports.py`, KB-1); an expiry date in its module docstring |
| shell | yes | only carried kernel rows | a fidelity pass **on built code** (the family's two-seat pilot, run on what main accepts, not on plan text) and a keyed answer or audit finding that pulls it | `tools/kernel_closure.py`: the verdict-writer count outside the kernel does not rise |
| kernel | yes | yes | the architect signs the registry change | the kernel total (section 6) |

Full proof rigour (statement review, mutation sweeps on the branch, verbatim-statement rule) applies
to kernel changes and to folds. Shell changes need tests, the fidelity pass and the carry rule; an
experimental module needs only to build. This is review finding 4's two-tier proposal with the
verifier's amendment (an import boundary, not a flag; an expiry).

## 6. The ratchet

1. `python3 tools/kernel_closure.py --check docs/kernel/closure-baseline.json` runs where
   `tools/trust_map.py --check` runs today (KB-1 wires it). It fails when the kernel total exceeds
   the saved one.
2. A change that raises the total updates the baseline in the same change and carries, in
   `docs/kernel/ALLOWANCES.md`, one line: lines added, door (B or C), reason, the architect's
   signature. A change that lowers it updates the baseline with no signature.
3. The verdict-writer count outside the kernel never rises (no allowance). It starts at the
   baseline's figure and falls as KB-2 lands.
4. A path moves from `candidate` to `kernel` only by the architect, with its wrap at most 50 lines
   (A) or each wrap line's reason recorded as `nonverdict`.
5. `tools/trust_map.py` keeps running until KB-5; its number is reported as "classified lines",
   never as the trusted base.

Targets (A, to be re-set after KB-4 measures them): kernel at most 9,565 now, at most 7,000 after
KB-4; verdict writers outside the kernel 0 after KB-2; document-mode spec at most 1,500 after KB-2a.

## 7. Build work, in order

Each row is filed in the backlog under the same id. Every row's acceptance includes: the five
frozen keys' harnesses pass unchanged (`uv run python usecases/anthropic-rsp/run.py --check`,
`usecases/openai-preparedness/run.py --check`, `usecases/safety-framework/run.py --check`,
`usecases/agent-policy/check.py base`, `usecases/eligibility/run.py --no-write`), and the kernel
check of section 6 passes.

| Id | What | Door / tier | Acceptance, beyond the above |
|---|---|---|---|
| KB-1 | Wire the measure: `lean/VE/Kernel/Carry.lean` (section 3, verbatim), the kernel check in the gate and in `tools/regen_generated.py`, the experimental import boundary, a rewritten `docs/trust-baseline.json` (`trust_map.py --write`, so the old file says 63,068) | kernel (signed here: +about 70 lines) | the gate fails on a seeded kernel growth of one definition and on a seeded verdict writer in a shell module |
| KB-2a | The document mode shows verdicts by the carry rule: `Service.Document`'s unit statuses become one fold over kernel rows; the chain's routes are called as kernel paths | shell | `document`'s spec at most 1,500 lines; its two verdict writers are the fold; every `tests/` document fixture's answer is unchanged except for the added carried cases |
| KB-2b | The same for the other writers: readings (17), the service's own modes (9, the document's among them), alternatives (6), discourse (5), risk (3), speech acts (3), the rest (8); one change per module group of `closure-baseline.json` `verdict_writers` | shell | writers outside the kernel fall by the group's count |
| KB-7 | A wire theorem for `metered` `evaluate-budgeted` on the entry's own runner (`MeteredRun.runCase`), ending in `MeteredProofs.fol_sound` and its three siblings | candidate, then kernel | `metered`: wrap at most 30 lines, spec at most 2,500 (A) |
| KB-8 | The same for `quantity` (`Time.Wire.runCase`), ending in `checkW6Certificate_sound`, `evalB_sorted_sound`, `refutesB_sorted_sound` and `admit_quantity_report_sound` | candidate, then kernel | `quantity`: wrap at most 30 lines |
| KB-3 | The core mode: the soft route's `soft-certificate`, `soft-conflict` and `admission` kinds accept `premises` (the slot `P`), with the wire theorem from `slot_route_acceptance`; then delete, one per family as it lowers, the pair refusals (`Document.lean:1166-1180`), `layersApart`, `listedStacks` and `RouteFacts` | kernel (signed per change) | a document listing `judgments@0` with `soft-norms@0` (RSP probe P8) is admitted through the slot and its judgments are premises of the carried case; the refusal text is gone from `lean/` |
| KB-4 | Shrink the kernel's own spec: the acts decoder becomes a lowering instead of a decoder parameter (removes norms' 2,703-line wrap); one formula codec with a round-trip theorem replaces the per-route decoders (`CONSOLIDATION-PLAN.md` step 8a) | kernel | kernel at most 7,000 lines (A) |
| KB-5 | Retire the class table as a gate: `trust_map.py` reports only; `docs/ARCHITECTURE.md` section 5 is rendered from `closure-baseline.json` | tools | `tests/test_architecture_docs.py` reads the new file |
| KB-6 | Promote rights, alternatives and reports to `kernel` once their theorems name the entry's own runner (their wrap is already 22 to 35 lines) | kernel | each path's row has tier `kernel`; the total stays within the signed figure |

Order: KB-1, then KB-7 and KB-8 (they are under the frozen keys' answers today), then KB-3 (it
unblocks judgment terms beside norms, the largest family the RSP's unchecked bytes wait for: 50
units, S: `usecases/anthropic-rsp/README.md`), then KB-2a and the rest. KB-2a and KB-2b change no
keyed answer (no key calls those modes); they are what whole-document checks need.

Not in this list, on purpose: a new statement type in Lean, a new wire format, a migration of the
use cases. The core document and its theorem exist, and the use cases already work by elaborating
and letting the kernel replay (section 1.3). The work is to prove the two unproved paths under
them and to make everything else go through the kernel.

Work this decision stops or changes:

- The PC rows (`pc-2b` … `pc-11`, `sn-wire-pc6`, `syn2-pc1-exchange`): superseded by KB-3. Their
  fidelity pilots failed on fresh draws (S: `REPORT-1.md` finding 3) because each stack was a new
  surface notation; KB-3 adds no notation.
- Any row whose deliverable is "a composed Lean route for X with Y": re-file as a lowering of X or
  of Y (door A) once KB-3 is in.
- Family build rows that add a service mode or a verdict token: hold until KB-1 lands, then re-file
  under door A.

## 8. The frozen keys on this measure

[docs/kernel/frozen-keys-20261111.md](../kernel/frozen-keys-20261111.md) holds the per-harness tables
(answers, wall time, Lean calls by mode and kind). They are the "before" of every KB row.

## 9. Risks and open points

| Risk | Why it may bite | What limits it |
|---|---|---|
| The registry's theorem lists were grouped mechanically (theorems whose hypothesis is `subject … = .ok …`) | a listed theorem may say less than a reader assumes (for example only one case kind) | KB-1 adds a per-kind table: each case kind of a kernel runner names its theorem, or is listed `nonverdict` |
| Carrying cases makes answers larger and the document mode slower | each verdict row now carries its case | the cases are the ones the chain already builds; measure UDHR time and memory before and after KB-2a, and refuse the batch if it is markedly slower (the lean-first rule) |
| A fold becomes a second place where verdicts are made | a status fold reads rows and writes `CHECKED` | folds are kernel code, counted and reviewed; target: one status fold |
| Fidelity, not soundness, loses the answers (RSP 111 → 77, Preparedness 231 → 68 after audit; S: `reviews/uc-audit-rsppf-20261111.md`) | this design does not by itself repair a mistranslation | it makes the translated core statements part of every answer, which is what a back-translation check and a per-rule distinguishing scenario need; those aids are the operations seat's and the audit loop's |
| The 64-predicate limit and the act-phrase limits bound the RSP fix cycle | `checkW1` refuses more than 64 regulated predicates (`SoftNorms/Soften.lean:471`); the RSP uses 64 | backlog `translim-predicates`; it is a resource bound, so door B's proof duties do not apply: it needs a measured check time at the new bound, nothing else |
