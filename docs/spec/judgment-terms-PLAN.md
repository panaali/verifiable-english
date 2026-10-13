# Judgment terms: plan

> **Status.** Draft 1, 2026-10-13, branch `design/judgment-terms` from `main` at `f98183bf`. Docs only: no product
> code, no tests, no generated file touched, no model calls. It builds the recommendation of
> [docs/research/judgment-terms.md](../research/judgment-terms.md) (cited as R and a section number): design B, "bound
> judgments". Every number is measured (R2 gives the method) or marked **estimate**. The Lean blocks of section 3 are
> written against `main` (names checked in the files cited). They are statements for the statement review (JT-0), not
> elaborated code; where the review changes a name, the review's text wins.

## 0. Summary

| # | Batch | Hours | Owner | Moves a pilot number? |
|---|---|---:|---|---|
| JT-0p | Pilot: measure judgment terms in both ledgers; write UDHR u010 and u060 as asserted judgments | 2 | pilot runner (prompt text from this plan, merged by the DRI) | **yes**: UDHR +132 to +198 B claimed (**estimate**), until audited |
| JT-0 | Statement spec, Lean stub against `main`, statement review | 3–4 | planner, then reviewers | no |
| JT-1 | Lean core in a new directory: W2 records, binding, admission, computed status, dependence through definitions, legacy proofs | 5–6 | Lean | no (integrity) |
| JT-2 | `judgments@0` in Lean's document mode: status hook, the usage map, AR-10 row, response shape, Python relay and fuzz tests; Python's W2 schema twin leaves the live path | 5–6 | Lean, Python | no (statuses become Lean-computed) |
| JT-E1 | Experiment: do readers see which answers turn on which judgment? | 3 | experiment runner | gate for JT-3's wording |
| JT-3 | English: declaration line, legend line, catalogue rows for evaluative words, refusals | 4–5 | english-lean owner (texts from this plan) | no (readability) |
| JT-4 | Judgment atoms in WG-6's zone answers and records; deciders named; English through WG-7 | 4–5 | Lean, Python | no (answers at situations) |
| JT-5 | Pilots switch `judgments@0` on (UDHR's four parts, the constitution's main document) | 2–3 | pilot runner | statuses computed by Lean; 0 B |
| JT-E2 | Experiment (research JT-R1): judgments over propositions ("it is essential that …") | 4 | experiment runner | possible later bytes (upper bound 3,238 B, co-blocked) |
| JT-E3 | Experiment: can raters agree which open terms are judgments? | 2 | experiment runner | validates JT-0p's instrument |

**Order.** JT-0p now, then JT-0 → JT-1. JT-2 follows once `lf-16g` (Lean document mode) and AR-10's table are on
`main`. JT-E1 must pass before JT-3. JT-4 follows once WG-6 and WG-7 are on `main`, then JT-5. JT-E2 needs attitudes'
AT-3a; JT-E3 runs any time after JT-0p.

**What this plan does not build** (each has an owner, R1.3):
- degrees, comparatives and thresholds (quantities' `scales@0`);
- the three-valued enumeration, zone answers, decision records and precedents (weighing's WG-6, WG-7, WG-E2);
- knowing and likelihood (attitudes);
- attachment of "arbitrary" and "fair" inside act phrases (act-phrases);
- rendering and the source-word catalogue (english-lean);
- "unless there is good reason" (defeasible).

## 1. Decisions

| # | Decision | Why | Rejected |
|---|---|---|---|
| D1 | A judgment term is a W2 open term under the profile `judgments@0`. The nine-key record does not change | one record, one owner (W2, `docs/spec/document.md:79-83`); quantities' grades and attitudes' generated terms are already W2 open terms | a new `judgment` record or kind field (design C); a `class` field in the language (the class is a ledger annotation, D5) |
| D2 | **Binding.** Under the profile, every open term's `name` is a declared base predicate whose sorts are its `arguments`, and no rule regulates it. The predicate's template and description are the term's words | Lean can then compute everything else from content; rights already reads open names as predicate names (`lean/VE/Rights/Run.lean:159-162`) | a binding field (changes the nine-key schema); leaving the term unbound (design A) |
| D3 | **Integrity.** Lean computes the status. Content that depends on a bound judgment is OPEN, never CHECKED. `"meaning": "specified"` on such content is refused (`JudgmentNotChecked: <unit> <term>`); an `open` list must name every judgment the content depends on and no bound judgment it does not (`JudgmentNotListed`, `JudgmentListedUnused`) | "never present a judgment as checked" becomes a theorem (`status_never_checked`) instead of a translator's promise; today OPEN is author-declared (`Loader.lean:210-213`) | downgrading silently (hides a translator error) |
| D4 | **Dependence goes through definitions.** A unit depends on a judgment if its content uses it, or uses a W3-defined predicate whose definition reaches it | otherwise `wrongful_detention :↔ detention ∧ arbitrary` would let a judgment pass as CHECKED (fixture J-γ) | direct use only |
| D5 | **One construct for classification and judgment words.** "Slavery" and "arbitrary" are both bound open terms; for the checker they are the same. The judgment / classification / exception / attitude class is recorded by the pilots' ledgers (JT-0p) for measurement only | the class changes no check; JT-E3 tests whether it can be measured reliably | a language-level class with different semantics |
| D6 | **Criteria are sentences.** Under the profile, `necessary` and `sufficient` are empty (`JudgmentCriterionAsUnit: <term>`). A criterion the source states ("no arrest ordered by a court is arbitrary") is a unit with its span, so it binds and is audited | attribution's rule (`attribution.md:2512-2515`), one place for criteria; today the lists are typed and then dropped (`Loader.lean:387-398`), so a reader cannot tell whether they bind | making the record's lists premises (a second, span-less place for criteria). Soft norms' and rights' own condition premises are unchanged |
| D7 | **One spelling for "no one named".** Under the profile `decided_by` is a token; when the source names no decider it is `unresolved_decider` (attribution's and attitudes' value). `unstated` is refused with that rewrite (`JudgmentDecider: <term>`) | the pilots use both spellings for one meaning | accepting both (two spellings, one meaning) |
| D8 | **Answers at situations reuse WG-6.** The bound judgment names are added to WG-6's open names. "Settled whatever the judgment", "left to <decider>: this depends on whether …", "not said", "inconsistent", "unknown" and judgment records are WG-6's answers and records | one owner of three-valued completion (SYNTHESIS O18); WG-6 already takes an explicit `opens` list | a judgment table of its own (design C) |
| D9 | **Graded words are quantities'.** A `scales@0` grade must be a W2 open term, so under `judgments@0` it is bound too, and its atoms are judgment atoms in zone answers. Nothing else is added for degrees | one owner (SYNTHESIS O4, quantities §10 item 3) | penumbral premises written by this plan |
| D10 | **Subsective phrases are conjunctions.** "Arbitrary arrest" is written `arrest(x) ∧ arbitrary(x)`. No generated premise "every arbitrary arrest is an arrest" | it follows from the conjunction; act-phrases owns restrictive-modifier specialisation (AP-5b) | a generated subsection premise |
| D11 | **Asserted judgments are ordinary assertions** over a bound judgment, OPEN ("The family is a natural and fundamental group unit of society.") | NORTH-STAR row 10's two UDHR units; no new construct | a new "evaluative claim" kind |
| D12 | **English: plain words, no symbols.** Declaration: "Whether an arrest is arbitrary is a judgment; the text does not say who makes it." or "… is a judgment for the governance function." Legend and zone wording as in 2.4. The rows are english-lean's (DRI AT4; SYNTHESIS O15), with texts from this plan, gated by JT-E1 | zero-training English; open terms are "strict only" today (`document.md:143`) | identifiers in what people read |
| D13 | **Authoring may precisify, translation may not.** In authoring the editor offers two ways out of a judgment word: define it (W3, the author's signed reading) or name who decides it. In translation it never defines | readings from the words only (VISION section 3) | defining in translation (design D) |
| D14 | **Deleted or not duplicated.** Python's copy of the W2 schema check (`ve/openterms.py`, against `Loader.openTermNames`) leaves the live document path in JT-2. This plan adds no enumeration, scale, record type, precedent mechanism or English table | CLAUDE.md "one owner per piece of logic" | — |

## 2. The design

### 2.1 Wire

- The environment's profile list contains `judgments@0`. The front matter's `open_terms` keeps the nine keys.
- Example: u037, "No one shall be subjected to arbitrary arrest, detention or exile.", with the joined filler as
  act-phrases leaves it. The predicate `arbitrary` is declared in the environment with template `{0} is arbitrary`
  and sort `act`. The record:

  ```json
  {"name": "arbitrary", "arguments": ["act"], "decided_by": "unresolved_decider", "necessary": [], "sufficient": [],
   "factors": ["the Declaration gives no test for arbitrariness"], "precedents": [], "jurisdiction": "udhr",
   "version": 1}
  ```

  The unit's rule has the guard `arrest(a) ∧ arbitrary(a)` and the meaning `{"open": ["arbitrary"]}`.
- **Admission checks** (Lean; the first fault in record order wins, then unit order):
  1. `JudgmentUnbound: <term>`: no base predicate of that name.
  2. `JudgmentArguments: <term>`: the predicate's sorts are not `arguments`.
  3. `JudgmentRegulated: <term>`: a rule regulates the predicate.
  4. `JudgmentCriterionAsUnit: <term>`: `necessary` or `sufficient` is not empty.
  5. `JudgmentDecider: <term>`: `decided_by` is `unstated`.
  6. Then, per unit: `JudgmentNotChecked: <unit> <term>`, `JudgmentNotListed: <unit> <term>`,
     `JudgmentListedUnused: <unit> <term>`.

  W2's own schema check (`Loader.openTermNames`) runs first and keeps its texts.

### 2.2 Status

- A unit with content that depends on a bound judgment (D4) is OPEN.
- Without such content, the unit's status is today's `Loader.w2Status`.
- Reading sets keep their own rule (`w2SetStatus`): a candidate's content is checked with the same rule, and an
  authored set whose readings depend on a judgment is OPEN, not CHECKED.
- `residual.open_terms` is unchanged (declared terms).
- The document check gains one report field, `judgments`: for each bound judgment, the ids of the units that depend on
  it, plus the declared judgments that no unit uses. This is the static answer to "which rules depend on which
  judgment"; Lean computes it.

### 2.3 Checked, and not checked

**Checked by Lean:**
- the binding;
- the status rule;
- dependence through definitions;
- the usage map;
- consistency **whatever the judgments**. CONFLICT-FREE already quantifies over every base situation, so over every
  way of judging; `conflictFree_every_judgment` restates this so the English can say it.
- with JT-4, zone answers at a situation: whether the outcome there is settled whatever the judgments, or turns on
  named judgment atoms, each with its decider; and whether a record of judgments is admissible or ruled out by named
  premises.

**Never checked:**
- any judgment itself;
- whether a decider considered the factors;
- the standard behind the word;
- where a vague boundary lies.

A record of judgments is a set of findings with a decider; answers under it say "given <decider>'s judgment that …".

### 2.4 English (texts for english-lean's rows; JT-E1 gates them)

| Row | Text | When |
|---|---|---|
| declaration | "Whether <the template with 'something' or the sort noun> is a judgment; the text does not say who makes it." / "… is a judgment for <decider>." | the legend of every bound judgment; also the authoring line that declares one |
| legend, factors | "The text mentions these points: <factor>; <factor>." | when `factors` is not empty |
| unit status | "Open: this depends on whether <atom>." | an OPEN unit's line, beside the source |
| zone, settled | "Settled: whatever is judged here, the text requires …" | WG-7's settled answer when the cone has judgment atoms |
| zone, left to | "Left to <decider>: this depends on whether <atom>." / "Left to no one the text names: this depends on whether <atom>." | WG-7's `left to` with judgment atoms |
| record | "Given <decider>'s judgment that <atom>, the text requires …" / "Ruled out: this judgment that <atom> contradicts <premise sentence>." | WG-7's record answers |
| conflict | "Conflict-free, whatever is judged." / "These rules conflict where <atom>." | the document check's conflict line |
| catalogue | "reasonable", "appropriate(ly)", "arbitrary/arbitrarily", "fair", "just", "legitimate", "genuine(ly)", "adequate", "effective", "necessary", "due", "good judgment", "overly <adj>": in translation, a bound judgment; never a definition the checker chooses. "Overly cautious" is one judgment term, never "more cautious than appropriate" unless the text says "more … than". "Genuinely" with two readings ("genuinely arising": in fact arising; or arising in good faith) is a reading set. "Clearly" (evident, or a degree) is quantities' QX-2 row | english-lean's catalogue (O15) |
| refusal (authoring) | "'Reasonable' is a judgment. Say who decides it ('… is a judgment for the operator'), or define it ('In this document, a reasonable limit means …')." | an authored sentence that uses an undeclared evaluative word |

### 2.5 Zone answers with judgments (JT-4, on WG-6)

- At a situation `M`, the open atoms are WG-6's (decision atoms, unsaid atoms) plus the bound judgment atoms at every
  typed tuple of `M`.
- A **record** fixes some of them: a decider's findings.
- The answers, their evidence and budgets are WG-6's (`MAX_OPEN_ATOMS` 16; norm-defaults' status keeps 12).
- This plan adds three things:
  - the judgment names in `opens`;
  - the deciders of a `left to` answer, read from the records of the differing judgment atoms;
  - the theorem that every differing atom is a decision atom or a judgment atom.
- Fixture J-α (4.1): at an arrest `a`, "Left to no one the text names: this depends on whether the arrest is
  arbitrary." With the record `arbitrary(a)`, the answer is "settled: forbidden". With the record `¬arbitrary(a)`, it is
  "not said".

## 3. Lean statements

New files, in a new directory: `lean/VE/Judgments/Decl.lean`, `Status.lean`, `Examples.lean` (JT-1); `Zone.lean` and
`ZoneExamples.lean` (JT-4). Plain-words companion: `lean/JUDGMENTS.md`. Names have the prefix `VE.Judgments.`;
`Loader` is `VE.Discourse.Loader`; `UnitContent` is `VE.Service.Document.UnitContent`.

### 3.1 Records and admission (JT-1, `Decl.lean`)

```lean
import VE.Discourse.Loader
import VE.Closure.Paths

namespace VE.Judgments

/-- A bound judgment: a W2 open term whose name is a base predicate (D1, D2). `factors` are shown, never premises. -/
structure Judgment where
  name      : String
  arguments : List String
  decidedBy : String
  factors   : List String
  deriving DecidableEq, Repr

/-- One record as written, after W2's check: the judgment and the lengths of `necessary` and `sufficient`. -/
abbrev Rec := Judgment × Nat × Nat

/-- The records of `open_terms`. W2's `Loader.openTermNames` stays the one validator: `records` runs it first and only
    then reads the already-checked fields. -/
def records (rv : VE.Route.Wire.RouteVocabulary) (j : Json) (data : Bool)
    (formula : Option (Json → Except String Unit)) : Except String (List Rec)

theorem records_names (rv j data formula rs) (h : records rv j data formula = .ok rs) :
    VE.Discourse.Loader.openTermNames rv j (python := true) (data := data) (formula := formula) =
      .ok (rs.map (·.1.name))

theorem records_refuse (rv j data formula e)
    (h : VE.Discourse.Loader.openTermNames rv j (python := true) (data := data) (formula := formula) = .error e) :
    records rv j data formula = .error e

/-- `judgments@0`'s admission (2.1, faults 1–5, first fault in record order). `regulated` are the names the document's
    rules regulate. -/
def admit (E : VE.Environment) (regulated : List String) (rs : List Rec) : Except String (List Judgment)

theorem admit_ok (E regulated rs js) (h : admit E regulated rs = .ok js) :
    js = rs.map (·.1) ∧
    ∀ r ∈ rs, E.predicates r.1.name = some r.1.arguments ∧ r.1.name ∉ regulated ∧
      r.2.1 = 0 ∧ r.2.2 = 0 ∧ r.1.decidedBy ≠ "unstated"

/-- The fault is the first record's first failing check, in the order of 2.1. -/
theorem admit_first_fault (E regulated rs e) (h : admit E regulated rs = .error e) :
    ∃ pre r post, rs = pre ++ r :: post ∧ (∀ q ∈ pre, faultOf E regulated q = none) ∧ faultOf E regulated r = some e

def names (js : List Judgment) : List String := js.map (·.name)

end VE.Judgments
```

`faultOf` is the per-record check of 2.1, items 1–5, defined in the same file.

### 3.2 Dependence, status and the usage map (JT-1, `Status.lean`)

`Status.lean` does not import `VE.Service.Document`: the document mode calls it (JT-2), so the content type it reads is
its own, and the document mode maps its `UnitContent` onto it in one line.

```lean
import VE.Judgments.Decl
import VE.Norms.Tree
import VE.NormDefaults.Status

namespace VE.Judgments
open VE.Discourse

/-- What a unit's content reads: a formula, or a rule (its guard and carve-outs, as rights' `nodeOpen` reads them). -/
inductive Content
  | formula (φ : VE.Formula)
  | rule (N : VE.Norms.Node)

def Content.formulas : Content → List VE.Formula
  | .formula φ => [φ]
  | .rule N => N.guard :: N.carveOuts

/-- The definition graph: a defined name points at each predicate of its body. -/
def defEdges (defs : List VE.Definitions.Def) : List (String × String) :=
  defs.flatMap fun d => (VE.Norms.preds d.body).map (d.name, ·)

/-- The judgments a formula depends on (D4): used directly, or reached through W3 definitions. -/
def dependsOn (defs : List VE.Definitions.Def) (J : List String) (φ : VE.Formula) : List String :=
  J.filter fun j => (VE.Norms.preds φ).any fun p => p == j || VE.Closure.reachEval .plus (defEdges defs) p j

theorem dependsOn_iff (defs J φ j) :
    j ∈ dependsOn defs J φ ↔
      j ∈ J ∧ ∃ p ∈ VE.Norms.preds φ, p = j ∨
        VE.Closure.Reachable .plus (fun a b => (a, b) ∈ defEdges defs) p j

/-- The judgments a unit's content depends on. -/
def dependsOnC (defs J) (c : Content) : List String := (c.formulas.flatMap (dependsOn defs J)).eraseDups

/-- The status under `judgments@0` (D3). `meaning` is `Loader.meaningStatus`'s value; `listed` the names of an `open`
    meaning (empty otherwise). -/
def status (defs J) (unit : String) (content : Option Content) (meaning : String)
    (listed : List String) : Except String String

theorem status_never_checked (defs J unit c meaning listed s)
    (h : status defs J unit (some c) meaning listed = .ok s) (hd : dependsOnC defs J c ≠ []) : s = "OPEN"

theorem status_checked (defs J unit c meaning listed)
    (h : status defs J unit (some c) meaning listed = .ok "CHECKED") : dependsOnC defs J c = []

theorem status_listed (defs J unit c listed)
    (h : status defs J unit (some c) "open" listed = .ok "OPEN") :
    (∀ j ∈ dependsOnC defs J c, j ∈ listed) ∧ (∀ j ∈ listed, j ∈ J → j ∈ dependsOnC defs J c)

/-- Without bound judgments, today's status. -/
theorem status_legacy (defs unit content meaning listed) :
    status defs [] unit content meaning listed = .ok (Loader.w2Status content.isSome meaning)

/-- A reading set's status (2.2): today's `w2SetStatus`, but OPEN when any reading's content depends on a judgment. -/
def setStatus (defs J) (authored allAsserted : Bool) (readings : List Content) : String :=
  if readings.any (fun c => !(dependsOnC defs J c).isEmpty) then "OPEN"
  else Loader.w2SetStatus authored allAsserted

theorem setStatus_never_checked (defs J authored allAsserted readings c)
    (hc : c ∈ readings) (hd : dependsOnC defs J c ≠ []) : setStatus defs J authored allAsserted readings = "OPEN"

theorem setStatus_legacy (defs authored allAsserted readings) :
    setStatus defs [] authored allAsserted readings = Loader.w2SetStatus authored allAsserted

/-- Which units depend on which judgment, and the judgments no unit uses (2.2). -/
def usageMap (defs J) (units : List (String × Option Content)) :
    List (String × List String) × List String

theorem usageMap_sound (defs J units j ids)
    (h : (j, ids) ∈ (usageMap defs J units).1) (id) (hid : id ∈ ids) :
    ∃ c, (id, some c) ∈ units ∧ j ∈ dependsOnC defs J c

theorem usageMap_complete (defs J units id c j)
    (hu : (id, some c) ∈ units) (hj : j ∈ dependsOnC defs J c) :
    ∃ ids, (j, ids) ∈ (usageMap defs J units).1 ∧ id ∈ ids

theorem usageMap_unused (defs J units j) :
    j ∈ (usageMap defs J units).2 ↔ j ∈ J ∧ ∀ id c, (id, some c) ∈ units → j ∉ dependsOnC defs J c

section
open VE.NormDefaults VE.Norms VE.Route   -- as `NormDefaults/Status.lean` opens them

/-- "Conflict-free, whatever is judged" (2.3): today's theorem, restated over any judging of the bound names. -/
theorem conflictFree_every_judgment (U : UDoc) (h : WellFormedU U = true) (hc : ConflictFreeU.{u} U)
    (J : List String) (B : VE.Structure.{u}) (R : String → List B.Carrier → Prop)
    (hR : ∀ n, n ∉ J → ∀ vs, R n vs ↔ B.relation n vs)
    (hB : BaseAdmissible U.D { B with relation := R }) :
    ∃ S, Expansion3 U { B with relation := R } S
end

end VE.Judgments
```

**Proof notes.**
- `dependsOn_iff` is `List.mem_filter` with `reachEval_iff` (`lean/VE/Closure/Paths.lean:190`).
- `status_*` are by cases on the definition.
- `usageMap_*` are list lemmas.
- `conflictFree_every_judgment` is `VE.NormDefaults.conflictFreeU_consistent` (`lean/VE/NormDefaults/Status.lean:293`)
  at the base `{ B with relation := R }`. `hR` is not needed for the proof; it is kept so that the statement says what
  the English says.

### 3.3 Zone answers with judgments (JT-4, `Zone.lean`; after WG-6)

WG-6's plan states `zoneOf (L X M record r vs proposed)` with `openNames L := decisionNames L.D ++ unsaidNames L.U`
built in. This plan needs one change in WG-6's file: an explicit `opens` (request R1, section 11). WG-6's own answers
are the `opens = openNames L` instance.

```lean
import VE.Judgments.Decl
import VE.Weighing.Zone

namespace VE.Judgments

/-- The open names with judgments: WG-6's, then the bound judgments. -/
def opens (L : VE.NormDefaults.LayeredU) (J : List String) : List String := VE.Weighing.openNames L ++ J

/-- WG-6's zone answer with the judgment atoms open. -/
def zone (L : VE.NormDefaults.LayeredU) (X : List (String × VE.Formula)) (M : VE.FiniteModel α) (J : List String)
    (record : List ((String × List α) × Bool)) (r : VE.Norms.Regulated) (vs : List α)
    (proposed : List (List ((String × List α) × Bool))) : VE.Weighing.ZoneAnswer α :=
  VE.Weighing.zoneOfOpens L X M (opens L J) record r vs proposed

theorem zone_settled (L X M valid hb J record r hr vs typed proposed b w)
    (hz : zone L X M J record r vs proposed = .settled b w) :
    VE.Weighing.SettledZ L.U (X.map (·.2)) M (opens L J) record r vs b

theorem zone_leftTo (L X M valid hb J record r hr vs typed proposed differ w₁ w₂ ns)
    (hz : zone L X M J record r vs proposed = .notSettled (some (differ, w₁, w₂)) ns) :
    VE.Weighing.LeftToZ L.U (X.map (·.2)) M (opens L J) record r vs (VE.NormDefaults.unsaidNames L.U) ∧
    ∀ a ∈ differ, a.1 ∈ VE.Weighing.decisionNames L.D ∨ a.1 ∈ J

/-- Without judgments, WG-6's answer, byte for byte. -/
theorem zone_no_judgments (L X M record r vs proposed) :
    zone L X M [] record r vs proposed = VE.Weighing.zoneOf L X M record r vs proposed

/-- The deciders a `left to` answer names: each differing judgment atom's `decided_by`, in first-occurrence order. -/
def deciders (js : List Judgment) (differ : List (String × List α)) : List String

theorem deciders_sound (js differ d) (h : d ∈ deciders js differ) :
    ∃ a ∈ differ, ∃ j ∈ js, j.name = a.1 ∧ j.decidedBy = d

theorem deciders_complete (js differ a j) (ha : a ∈ differ) (hj : j ∈ js) (hn : j.name = a.1) :
    j.decidedBy ∈ deciders js differ

end VE.Judgments
```

On the plain norm-defaults route (the UDHR's companions), `zone` needs a `LayeredU` without packs (request R2,
section 11). Until it exists, JT-4's fixtures run on the layered route only.

### 3.4 What is not claimed

- No theorem says a judgment is right.
- No minimality of the judgments an answer lists: WG-6 lists the atoms on which two checked completions differ, not a
  minimal set.
- No completeness beyond WG-6's budget: beyond it the answer is UNKNOWN with the budget as reason.
- No claim that a criterion written as a unit is faithful to the source: that is the audit's job.

## 4. Fixtures

### 4.1 Synthetic (`#guard` in Lean, and the same through the service in Python)

| # | Document | Expected |
|---|---|---|
| J-α | sorts `person`, `act`; base `arrest(act)`, `arbitrary(act)` (bound, `unresolved_decider`); a rule forbidding `subjects(person, act)` where `arrest(a) ∧ arbitrary(a)`; meaning `{"open": ["arbitrary"]}` | status OPEN; usage map `arbitrary ↦ [u1]`. JT-4: at `M` = one person, one arrest: `left to` (no one named), differing atom `arbitrary(a)`; record `arbitrary(a)` → settled no; record `¬arbitrary(a)` → not said |
| J-β | J-α with meaning `"specified"` | `JudgmentNotChecked: u1 arbitrary` |
| J-γ | W3 `wrongful_detention(a) :↔ detention(a) ∧ arbitrary(a)`; a unit uses only `wrongful_detention`, meaning `"specified"` | `JudgmentNotChecked: u1 arbitrary` (dependence through a definition, D4) |
| J-δ | open term `reasonable_limitation`, no predicate of that name | `JudgmentUnbound: reasonable_limitation` |
| J-ε | predicate `arbitrary(act)`, record `arguments: ["person"]` | `JudgmentArguments: arbitrary` |
| J-ζ | J-α's record with `necessary` = one formula | `JudgmentCriterionAsUnit: arbitrary` |
| J-η | J-α's record with `decided_by: "unstated"` | `JudgmentDecider: arbitrary` |
| J-θ | constant `the_family`; base `natural_and_fundamental_group_unit(thing)` (bound); assertion of it at `the_family`; meaning open | OPEN; usage map lists the unit (row 10's form, D11) |
| J-ι | J-α plus a rule requiring the arrest where `court_ordered(a)` | CONFLICT, witness with `arbitrary(a)` true: "These rules conflict where an arrest ordered by a court is judged arbitrary." Adding the unit "No arrest ordered by a court is arbitrary." gives CONFLICT-FREE (D6) |
| J-κ | 17 bound judgments in one guard over one tuple | JT-4: `unknown`, budget (17 open atoms, limit 16) |
| J-λ | each of J-α to J-θ without `judgments@0` | statuses and diagnostics as today, byte-identical (`status_legacy`; the profile-off path never calls `status`); zone answers as WG-6's (`zone_no_judgments`) |
| J-μ | a rule guarded by `arrest(a)` only, beside J-α's judgment declared and unused | settled whatever is judged; usage map lists `arbitrary` as unused |
| J-ν | a `scales@0` grade `gives_serious_uplift` that is also a W2 open term | binding passes; its atoms are judgment atoms in JT-4's zone |
| J-ξ | a reading set whose two candidates both use `arbitrary` (u055's two scopes) | each candidate's status OPEN; the set OPEN even if authored (2.2) |

### 4.2 From the pilots (each sentence is the source text; ids from the run-20261012T1800Z ledgers)

| Unit | Sentence | Fixture use |
|---|---|---|
| U u037 | "No one shall be subjected to arbitrary arrest, detention or exile." | J-α's shape on the real translation once JT-5 runs; zone wording checked in JT-E1 |
| U u045a | "No one shall be subjected to arbitrary interference with his privacy, family, home or correspondence" | `arbitrary` reused across units; the usage map lists u037, u045a, u046, u055, u064 under one term |
| U u055 | "No one shall be arbitrarily deprived of his nationality nor denied the right to change his nationality." | J-ξ: a reading set over the adverb's scope (act-phrases' D9), both candidates OPEN |
| U u111 | "… meeting the just requirements of morality, public order and the general welfare in a democratic society." | five bound judgments in one unit; the budget is not reached at one tuple each |
| U u089 | "Everyone has the right to rest and leisure, including reasonable limitation of working hours and periodic holidays with pay." | the catalogue row for "reasonable" (JT-3); not unlocked (time, R2.3) |
| U u010 | "Whereas a common understanding of these rights and freedoms is of the greatest importance for the full realization of this pledge," | JT-0p and J-θ's binary form |
| U u060 | "The family is the natural and fundamental group unit of society" | JT-0p; "the … unit" stays presupposition's |
| C u0052.s01 | "Claude should always use good judgment when evaluating conversational inputs." | OPEN on `good_judgment`, a holistic judgment that is never decomposed |
| C u0168.s01 | "When faced with seemingly compelling arguments to cross these lines, Claude should remain firm." | OPEN on `seemingly_compelling_argument_to_cross_line`; zone at the 49 probe points after JT-4 |
| C u0031.s03 | "The risks of Claude being too unhelpful or overly cautious are just as real to us as the risk of Claude being too harmful or dishonest." | catalogue row for "overly": one judgment term; the comparison of risks stays quantities' and weighing's |
| Safety framework F18 | "It is reviewed more often when there are reasonable grounds." | a bound judgment with a named decider ("we"), `left to` names it |

## 5. Batches

Every batch lists its files. A **shared file** is one that another plan or in-flight branch also edits; the rest are
new. Generated files are regenerated with their own tool (`tools/regen_generated.py --write`, or `--resolve` after a
merge), never edited or merged by hand. Each batch plants a bug in each behaviour it claims, in each language it
changes, shows a failing test, and restores it (CLAUDE.md).

### JT-0p. Pilot: measure judgment terms; asserted judgments (2 h; pilot; first batch)

- **What.** Text for the DRI's merged pilot prompts (`manage-agents/prompts/pilot-additions.txt`,
  `udhr-additions.txt`, and their audit additions). No repository file.
  1. **Instrument, both ledgers.**
     - Each declared or annotated open term gets a class in `metrics.json` under `open_term_class`, by R2.1's rule:
       `judgment`, `classification`, `exception`, `attitude` or `proportion`.
     - Each unit gets `judgment_terms` (its open terms of class `judgment`).
     - `metrics.json` gets `judgment_term_units` and `judgment_term_bytes`, by status and by `missing_feature`.
  2. **UDHR u010 and u060 as asserted judgments.**
     - u010: binary `of_greatest_importance_for` between two named things.
     - u060: unary `natural_and_fundamental_group_unit_of_society` on `the_family`.
     - Both have `decided_by: "unresolved_decider"` and factors from the words. Each is a ground assertion with the
       meaning `{"open": [...]}`, so its status is OPEN.
     - u060's note says that "the" (uniqueness) is not represented and is presupposition's.
  3. **Audit addition.** A targeted blind audit of u010 and u060. On the sampled units, auditors also check that no
     CHECKED unit's content uses an open-term predicate.
- **Pre-registered bar.** The four UDHR parts load and check as before, with u010 and u060 OPEN.
  - **PASS** if the targeted audit finds both FAITHFUL: claimed bytes +198 (4,792 → 4,990 B, 43.90% → 45.71%).
  - **Partial** if only u010 is FAITHFUL: +132 B.
  - **FAIL** otherwise: the units revert and the reason is recorded.
  - The instrument has no bar; its numbers start a series. JT-E3 tests its reliability.
- **Bytes.** UDHR +132 to +198 B (**estimate**). Constitution 0 B.
- **Dependencies.** None in the repository; the next UDHR and constitution runs (06:00/18:00 UTC).
- **Conflicts.** None: prompts are merged by the DRI into one file per pilot (DRI SC2), and pilot runs are
  sequential.

### JT-0. Statement spec and stub (3–4 h; planner, then reviewers)

- **What.**
  - `docs/spec/judgment-terms.md`: the statements of section 3, elaborated against `main`.
  - A stub `lean/VE/Judgments/Stub.lean`, untracked, run with `lake env lean`. It records every change the
    elaboration forces (exact field names of `VE.Definitions.Def`, `UnitContent`, `VE.Norms.Node`, and WG-6's names).
  - Statement review: Sol stands in for Astra, Fable is arbiter (current DRI policy).
- **Gate.** The review passes, or each FIX is applied and re-checked once.
- **Files.** New: `docs/spec/judgment-terms.md`. Nothing shared.

### JT-1. Lean core (5–6 h; Lean)

- **What.** Section 3.1 and 3.2 in `lean/VE/Judgments/{Decl,Status,Examples}.lean`, with fixtures J-α to J-θ, J-λ,
  J-μ and J-ξ as `#guard`s, and `lean/JUDGMENTS.md`, every definition and theorem in plain words. Pure library: no
  route, no service change.
- **Shared files** (one hunk each):
  - `lean/VE.lean`: three imports;
  - `lean/VE/Audit.lean`: the theorem names of 3.1 and 3.2;
  - the generated statement, declaration and axiom inventories, regenerated by their generator.
- **Seeded bugs (Lean):**
  - `dependsOn` without the definition closure: J-γ fails;
  - `status` returning CHECKED for `specified` content that uses a judgment: J-β fails;
  - `admit` checking arguments before binding: J-δ's text changes.
- **Dependencies.** None in flight: the directory is new, and `Loader.lean`, `Closure/Paths.lean` and
  `NormDefaults/Status.lean` are only imported.
- **Consolidation.** Rights' `nodeOpen` (`lean/VE/Rights/Run.lean:159-162`) reads open names in a guard and its
  carve-outs as `dependsOnC` does with no definitions. The ledger of JT-1 records the overlap. Rights is switched to
  the shared function only in a later batch, after its frozen fixtures prove byte identity, so that no frozen
  behaviour moves in this batch.

### JT-2. `judgments@0` in Lean's document mode (5–6 h; Lean, Python)

- **Lean:**
  - In `lean/VE/Service/Document.lean`'s `check`, when the profile is on:
    - after `Loader.openTermNames`, `Judgments.records` and `Judgments.admit`;
    - `sourceUnit`'s `status := …` takes `Judgments.status`, with `UnitContent` mapped onto `Judgments.Content` (the
      profile-off path is unchanged, J-λ);
    - the reading-set statuses (W2 sets through `Loader.w2SetStatus`, and `readings@1`'s sets in `readingsSets`) take
      `Judgments.setStatus`;
    - the report gains `judgments` (the usage map).
  - The profile's row in AR-10's table (`lean/VE/Compose/Dispatch.lean`): it requires `documents@1` and composes with
    `norms@0`, `norm-defaults@0`, `readings@1`, `definitions@0`, and `scales@0` and `attitudes@0` when those land. It
    refuses nothing, and the batch proves the composition statement for each newly admitted combination (SYNTHESIS
    2.2).
  - The response shape of the document mode's new field, and its encoder theorem (`lean/ResponseShape/Schemas/` and
    `Encoders/`, the document mode's files).
- **Generated:** the document mode's JSON schema under `ve/backends/lean_service_schema/` via
  `uv run python tools/response_schemas.py --write`; the gate's inventories via `tools/regen_generated.py --write`.
- **Python:**
  - The relay checks the new field's schema and binding only: every unit id is a unit of the request, every name is a
    declared open term, and no row is empty or extra (R8).
  - Fuzz tests in `tests/test_judgments_answer.py`: each member dropped, emptied, retyped, duplicated or reordered, an
    id pushed out of range. Every mutant is `CheckerUnavailable` or changes nothing shown.
  - Fixtures recorded in `tests/data/route-cases.jsonl` by the recorder.
  - The live document path stops calling `ve/openterms.py`: Lean's diagnostic is relayed. The file stays only while
    `tests/frozen_speech/speech_document.py` (frozen) imports it; the layer policy entry says so.
- **Seeded bugs:**
  - Lean: the status hook skipped under the profile, so J-β passes as CHECKED and the test fails.
  - Python: the relay accepts an id outside the request, so the fuzz test fails.
- **Dependencies.**
  - `lf-16g` (Lean document mode owns `ve document`; SYNTHESIS 4.2 queue: after `lf-16g`, AT-3b, SC-1b, QT-A4,
    ET-5, WG-4, ME-10 "in landing order"; JT-2 joins that queue);
  - AR-10's table on `main`.
- **Shared files:**
  - `lean/VE/Service/Document.lean`: the unit status hook, the set status hook and the report field (three hunks);
  - `lean/VE/Compose/Dispatch.lean`: one table row;
  - the document mode's ResponseShape files;
  - `ve/document.py` while it exists (one call removed);
  - `tools/layer_policy.py` (one entry).

### JT-E1. Readability (3 h; experiment; before JT-3)

Pre-registered in section 6.

### JT-3. English rows (4–5 h; english-lean owner)

- **What.** The rows of 2.4, in english-lean's files (`lean/VE/EnglishGrammar/*`) and its catalogue:
  - the declaration line, parsed in authoring to a W2 record and its predicate;
  - the legend and status lines;
  - the catalogue rows for the evaluative words, with their refusals and rewrites.
- **Not this batch.** The zone, record and conflict wordings (2.4) are WG-7's display rows, extended in JT-4.
- **Queue.** english-lean's single queue on `lean/VE/EnglishGrammar/*` (SYNTHESIS 4.1 item 7: AT-5 → QT-A6 → ME-11 →
  QT-B3 → SC-7). JT-3 joins in landing order; it depends on none of them.
- **Seeded bug (Lean):** the legend line drops the decider; the row fixture fails.
- **Shared files:** english-lean's grammar and catalogue files, and nothing else.

### JT-4. Judgment atoms in zone answers (4–5 h; Lean, Python)

- **What.** Section 3.3 in `lean/VE/Judgments/{Zone,ZoneExamples}.lean`, with fixtures J-α (zone part), J-κ and J-ν.
  - WG-7's two kinds read `judgments@0`: with the profile on, `opens` includes the bound judgments.
  - The `left to` answer names the deciders (`deciders`).
  - The English rows of 2.4 for zone, record and conflict are added to WG-7's display.
- **Python:** the relay binds the deciders to the request's open-term records. Fuzz cases are added to WG-7's fuzz
  file.
- **Seeded bugs:**
  - Lean: `deciders` reads the first record only; `deciders_complete`'s fixture fails.
  - Python: a decider not in the request is accepted; the fuzz test fails.
- **Dependencies.** WG-6 and WG-7 on `main`, and request R1 (WG-6's explicit `opens`). R2 is needed for the UDHR's
  plain route; without it the UDHR waits.
- **Shared files:**
  - `lean/VE/Weighing/Zone.lean`: R1's parameter, if WG-6 has not already landed it;
  - WG-7's kind dispatch: one condition;
  - WG-7's ResponseShape file: a `deciders` member, if WG-7's shape lacks one;
  - `lean/VE.lean`, `lean/VE/Audit.lean`.

### JT-5. Pilots switch on (2–3 h; pilot)

- **What.** Prompt additions: both pilots add `judgments@0`, and each open term is bound to its predicate.
  - UDHR: rename either the predicate or the term where the two differ (for example `is_arbitrary` against
    `arbitrary`; act-phrases' digest), re-check the four parts and their companions, and record the usage map.
  - Constitution: the main document. The u0165.s01–s07 rules keep queue 4.4's text; only the profile and the binding
    change, at a run after the queue's current step.
- **Bar.** Every claimed unit keeps its status or moves from CHECKED to OPEN, and no unit moves the other way. Any
  move to OPEN is a finding: a judgment that was shown as checked, recorded unit by unit.
- **Bytes.** 0 claimed. Statuses are Lean-computed on the UDHR's 18 judgment-carrying units (1,945 B) and the
  constitution's CONSTITUTION-OPEN-JUDGMENT.
- **Dependencies.** JT-2 on `main` and in the pilots' green tag; JT-4 for the zone probes.
- **Conflicts.** None in the repository.

### JT-E2 and JT-E3 (experiments)

Pre-registered in section 6.

## 6. Experiments (pre-registered; each runs only under its own authorisation, with model calls budgeted by the DRI)

### JT-E1. Do readers see which answers turn on which judgment?

- **Design.** Sonnet 5.5 as the proxy reader, with only what a human gets, as in the readability eval of 2026-10-03.
  - 40 items: 20 UDHR (u037, u045a, u046, u055, u064, u111 and synthetic variants), 20 constitution (u0052.s01,
    u0168.s01, the hard constraints as QT-B4 leaves them, synthetic variants).
  - Two arms: today's rendering (identifiers, 'classified as "arbitrary"') and 2.4's English.
  - Each item asks which conclusions hold whatever is judged and which turn on a judgment, and on whose.
- **Bars.**
  - (a) At least 90% correct with 2.4's English, and at least 15 points above the identifier arm.
  - (b) At most 2% critical misreadings: an answer that turns on a judgment read as settled or checked.
- **Then.** If either bar fails, JT-3's wording is revised once and re-run on fresh items. If it fails again, JT-3
  lands with the legend line only and the zone rows wait.

### JT-E2. Judgments over propositions (research JT-R1)

- **Question.** Can "it is essential/important/better that P" be written faithfully, without new semantics, as an
  attitude guard node with the document as holder and the judgment as mode?
- **Items.** The 15 constitution units found by excerpt search (R5.2; 2,952 B) and UDHR u006 and u007 (286 B): 17
  units.
- **Protocol.**
  - A translator writes the candidate form under attitudes' content rules (quantifier-free content, one slot).
  - A different model audits blind.
  - Units whose other blockers are not yet met are written as partial companions and not claimed.
- **Bar.** At least 13 of 17 FAITHFUL, and none with invented content. AT-3a must be on `main`.
- **Then.** On PASS, a build batch is planned for the content-node reuse (shared piece S9). On FAIL, the units stay
  UNFORMALISED and the failure classes are recorded.

### JT-E3. Can the judgment class be measured?

- **Items.** 60 open terms, sampled stratified from both ledgers' instruments (JT-0p).
- **Protocol.** Two raters (two different models) classify each term by R2.1's rule, independently.
- **Bar.** Cohen's κ at least 0.7.
- **Then.** If the bar fails, the instrument reports only "open term", and judgment-term counts are not published as
  measured.

## 7. Dependencies and merge safety

| Item (branch) | Needed by | How this plan avoids conflicts |
|---|---|---|
| `lf-16e/f/g` (Lean document mode) | JT-2 | JT-2 starts after `lf-16g` merges, in SYNTHESIS 4.2's queue for `Service/Document.lean` |
| AR-10's profile table | JT-2 | one row, after the table lands (SYNTHESIS 4.3: "the table lands before any new profile row") |
| `rd-9/integrate` (RD-9), PK-1 | WG-6, hence JT-4 | JT adds no pack and no premise to X: bound judgments are declared base predicates, not generated ones, so PK-1's `packOrder` gains no row |
| WG-6, WG-7 (weighing plan) | JT-4 | JT-4 is a new file plus one parameter (R1) and one condition in WG-7's dispatch; if WG-6 lands with `opens` explicit, JT-4 edits no weighing file |
| english-lean's queue | JT-3 | joins the queue in landing order; touches no other file |
| `qa-q2`, `lean-first/b14b`–`b14d`, `lf-16e/f` (editors of `Protocol.lean` and `service_schema.py`) | none | JT adds no service mode (SYNTHESIS C9) |
| quantities (`scales@0`) | J-ν only | no shared file: a grade's binding is checked by JT's admission over the same W2 records |
| queue 4.4 (u0165.s01–s07) | JT-5 | JT changes none of those units' text; the profile switch runs at a pilot run after the queue's current step |

**Shared files, all batches:**
- `lean/VE.lean`, `lean/VE/Audit.lean`;
- `lean/VE/Service/Document.lean`;
- `lean/VE/Compose/Dispatch.lean`;
- the document mode's ResponseShape files;
- `lean/VE/Weighing/Zone.lean` (R1, only if needed);
- WG-7's dispatch and ResponseShape;
- `lean/VE/EnglishGrammar/*`;
- `ve/document.py` (while it exists);
- `tools/layer_policy.py`;
- the generated inventories (by their tools only).

## 8. Bytes, by batch

| Batch | Constitution (184,893 B) | UDHR (10,916 B) | Kind |
|---|---|---|---|
| JT-0p | 0 | +132 to +198 B claimed | **estimate**, until the targeted audit |
| JT-1 to JT-4 | 0 | 0 | integrity, answers, English |
| JT-5 | 0 claimed; Lean-computed status on CONSTITUTION-OPEN-JUDGMENT | 0 claimed; Lean-computed status on 18 units, 1,945 B (measured, R2.3) | integrity |
| JT-E2 (if PASS, then a build) | up to 2,952 B, co-blocked by norms, quantities, attribution, causation or modality | up to 286 B (u006, u007), co-blocked by modality | **estimate**, upper bound |

No sum across rows: the bytes overlap with other plans' claims, and NORTH-STAR's rule forbids summing.

## 9. Risks and limits

- **The need is small in bytes.** R2 measures that judgment terms block 198 B as a primary blocker. If the DRI ranks
  by bytes, this plan's build batches rank low; their case is integrity (D3), answers (JT-4) and English (JT-3).
- **JT-4 waits on a chain:** RD-9 SC-A, PK-1, WG-6 and WG-7. If the chain slips, JT-1, JT-2 and JT-3 still land and
  are useful alone.
- **Binding may break pilots** whose terms and predicates have different names. JT-5's bar makes every move a recorded
  finding, not a silent change.
- **The usage map is direct dependence through definitions,** not through rule chains: a rule whose conclusion feeds
  another rule's guard does not propagate in the map. The zone answer at a situation is the full answer.
- **JT-E3 may fail.** Then the published judgment-term counts are "open-term" counts, as before.
- **Budgets.** Five judgments in one unit (u111) at many tuples can exceed WG-6's 16 open atoms: the answer is then
  UNKNOWN with that reason.

## 10. Shared pieces

Abstractions several topics could share. Each has a proposed owner and the interface this plan needs.

| # | Piece | Proposed owner | Users | Interface |
|---|---|---|---|---|
| S1 | One W2 record for every named open predicate, decoded as records (not names) | W2 / the discourse loader (`Loader.openTermNames`) | judgments, attitudes (generated records), quantities (grades), events (causal links), weighing (WG-0's rank terms) | `records` over `openTermNames` (3.1); one day a records-returning `openTermNames` with the names as projection |
| S2 | Binding an open term to its base predicate | this plan (`judgments@0`) | quantities' `Grade` ("a unary predicate that is a W2 open term"), events' `LinkNotOpen`, attitudes' generated atoms | `admit` (3.1) |
| S3 | Status computed from content for every open atom | this plan for W2 units; rights already does it (`nodeOpen`) | rights, soft, attitudes, events, quantities | `dependsOnC` and `status` (3.2) |
| S4 | Zone answers parameterised by their open names | weighing (WG-6) | judgments (JT-4), quantities (grade atoms), events (link atoms), attitudes (attitude atoms) | `zoneOfOpens L X M opens …` (request R1) |
| S5 | Records of findings with a decider | weighing (WG-6's records) with W2 `support` | judgments, weighing, risk (decision records), events | WG-6's `record`; "given <decider>'s judgment that …" |
| S6 | One decider vocabulary (`unresolved_decider` for no one named; `unstated` and `null` retired) | W2 | soft (`unstated`/`null`), rights, alternatives, attribution, attitudes, judgments | a token, one spelling (D7) |
| S7 | One legend row kind for open atoms ("Whether … is a judgment; … decides it") | english-lean (DRI AT4) | every plan with open atoms | 2.4's declaration and legend rows |
| S8 | Catalogue rows for evaluative words | english-lean | judgments, quantities ("serious", "clearly"), act-phrases ("arbitrarily", "freely"), defeasible ("good reason") | rows only (O15) |
| S9 | Propositional content atoms ("it is essential that P") | attitudes (AT-3a's content nodes) | judgments (JT-E2), attribution, events (hedged causal claims) | a guard node with the document as holder |
| S10 | Precedential constraint over findings | weighing (WG-E2) | judgments, weighing | WG-E2's protocol, unchanged |
| S11 | Graded open terms (a W2 record plus a dimension and a direction) | quantities (its §10 item 3) | judgments (J-ν), attitudes ("quite likely") | `VE.Scales.Grade` |

## 11. Cross-plan issues for the DRI

- **R1 (to weighing, WG-6).** Please state `zoneOf` with an explicit `opens : List String`, so that WG-6's answers are
  the instance `opens = openNames L`, and state `zone_leftTo_sound`'s last conjunct as "every differing atom is in
  `opens` and not unsaid". Then JT-4 edits no weighing file.
- **R2 (to RD-9 / PK-1).** A `LayeredU` with no packs for a plain norm-defaults document, so that zone answers run on
  the UDHR's companions. Otherwise the UDHR's judgment answers wait.
- **R3 (to W2 / all plans).** One decider spelling (S6). This plan refuses `unstated` only under its own profile; other
  constructs are unchanged until their owners agree.
- **R4 (to quantities).** Under `judgments@0`, a grade must be bound (S2). `WellFormed E openTerms D` already requires
  a grade to be a W2 open term, so this adds only the sort check.
- **R5 (to NORTH-STAR).** Row 10 stays 0–198 B (UDHR). R2's measurement does not support listing judgment terms as a
  large coverage blocker on the constitution. Their value is integrity and answers, which NORTH-STAR does not score.

## Change log

| Date | Draft | Change |
|---|---|---|
| 2026-10-13 | 1 | First draft: design B of the research note; decisions D1–D14; Lean statements for records, admission, status, dependence through definitions, the usage map, "conflict-free whatever is judged", and zone answers on WG-6; fixtures J-α to J-ξ and eleven pilot sentences; batches JT-0p to JT-5 with three pre-registered experiments; eleven shared pieces; five cross-plan requests. Planning only. |
