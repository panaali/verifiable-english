import VE.Cardinality.Wire
import Std.Data.HashMap

/-! Cardinality documents: the claim graph (docs/spec/quantities.md 4.1, 4.3), following `VE.Time.Document`'s.

A document is `{"root": name, "nodes": [node, …]}`; a node is `{"name", "statement"}` with, for a deduction,
`"premises"` (names of earlier nodes) and `"certificate"`, which come together. Nodes are checked in submitted order:
names are unique, premises name earlier nodes, and each certificate is checked against exactly its premises'
statements and the node's. An entry rests on the leaves (nodes without a deduction) of its premises, each once: a
set of positions, so a graph that reuses a premise does not repeat its leaves, and a premise costs one lookup by name
and one join of at most `maxGraphNodes` bits, whatever the names' lengths. The report is the root's statement and
those leaves, in submitted order.

The certificate check is a parameter (`Checks`: an accepted certificate establishes its conclusion), so this module
sits below the runner, which supplies the cardinality check and defines `admitDocument` (`Run.lean`;
`admit_cardinality_report_sound` is in `RunTheorems.lean`). Every value is read once and charged: at most
`maxGraphNodes` nodes, and the statements the deductions' problems read, counted as S2 counts them, at most
`maxDeductionNodes` over the whole graph, charged before each problem is built. -/
namespace VE.Cardinality
universe v

/-- A Lean-admitted document's report: its root statement and the leaves it rests on. -/
structure CardReport where
  root : CFormula
  leaves : List CFormula

def CardReport.Sound (E : CEnv) (r : CardReport) : Prop := CEntails.{v} E r.leaves r.root

end VE.Cardinality

namespace VE.Cardinality.Document
universe v
open Lean
open VE.Bridge (exactFields stringField strings)

def maxGraphNodes : Nat := 1000
def maxDeductionNodes : Nat := 5 * VE.Limits.maxNodes

def graphRejected : String := "graph rejected: cycle, duplicate name, dangling premise or invalid certificate"
def nodeLimit : String := s!"ResourceLimit: At most {maxGraphNodes} claim graph nodes"
def deductionLimit : String :=
  s!"ResourceLimit: the claim graph's deductions read more than {maxDeductionNodes} statement nodes"

/-- A decoded node: its name, admitted statement, the statement's size (S2's node count) and its deduction. -/
structure CNode (w : CardEnv) (γ : Type) where
  name : String
  adm : CAdmission w
  size : Nat
  deduction : Option (List String × γ)

/-- A checked node and the leaves it rests on: bit `i` is the `i`th submitted node, so joining its premises' leaves
reads a fixed number of bits per premise (at most `maxGraphNodes`), whatever the names' lengths or how often a
premise is reused. -/
structure Entry (w : CardEnv) where
  name : String
  adm : CAdmission w
  size : Nat
  leaves : Nat

/-- An accepted certificate establishes its conclusion from exactly its premises. -/
def Checks {γ : Type} (w : CardEnv) (check : List (CAdmission w) → CAdmission w → γ → Except String Bool) : Prop :=
  ∀ ps c x, check ps c x = .ok true → CEntails.{v} w.env (ps.map (·.formula)) c.formula

/-- The entry's statement holds in every admissible structure where each submitted leaf it rests on holds. -/
def Entry.Sound {γ : Type} {w : CardEnv} (all : List (CNode w γ)) (e : Entry w) : Prop :=
  ∀ (α : Type v) (T : VE.Time.TStructure α), Admissible w.env T →
    (∀ (i : Nat) (n : CNode w γ), all[i]? = some n → n.deduction = none → e.leaves.testBit i = true →
      n.adm.formula.holds T) → e.adm.formula.holds T

/-- The checked nodes by name: one hash of the premise's name per lookup. -/
abbrev Entries (w : CardEnv) := Std.HashMap String (Entry w)

def lookup {w : CardEnv} (acc : Entries w) (p : String) : Except String (Entry w) :=
  match acc[p]? with
  | some e => .ok e
  | none => .error graphRejected

/-- The children's leaves, each once. -/
def union (sets : List Nat) : Nat :=
  sets.foldl (· ||| ·) 0

/-- Nodes in submitted order, the next at position `i`; `used` is the charge so far. A deduction's premise count,
then its statements' sizes, are charged before its premises are looked up and its problem is checked. -/
def checkGraph {γ : Type} (w : CardEnv) (check : List (CAdmission w) → CAdmission w → γ → Except String Bool) :
    List (CNode w γ) → Nat → Nat → Entries w → Except String (Entries w)
  | [], _, _, acc => .ok acc
  | n :: ns, i, used, acc =>
    if acc.contains n.name then .error graphRejected else
    match n.deduction with
    | none => checkGraph w check ns (i + 1) used (acc.insert n.name ⟨n.name, n.adm, n.size, 2 ^ i⟩)
    | some (ps, cert) =>
      if used + ps.length > maxDeductionNodes then .error deductionLimit else
      match ps.mapM (lookup acc) with
      | .error e => .error e
      | .ok children =>
        let cost := children.foldl (· + ·.size) (used + n.size)
        if cost > maxDeductionNodes then .error deductionLimit else
        match check (children.map (·.adm)) n.adm cert with
        | .ok true => checkGraph w check ns (i + 1) cost
            (acc.insert n.name ⟨n.name, n.adm, n.size, union (children.map (·.leaves))⟩)
        | .ok false => .error graphRejected
        | .error e => .error e

/-- An admitted graph: its nodes and the root's entry. -/
structure Graph (w : CardEnv) (γ : Type) where
  nodes : List (CNode w γ)
  root : Entry w

/-- The leaves the root rests on, in submitted order (only a leaf's position is ever set). -/
def Graph.leaves {w : CardEnv} {γ : Type} (g : Graph w γ) : List (CNode w γ) :=
  (g.nodes.zipIdx.filter fun (_, i) => g.root.leaves.testBit i).map (·.1)

def Graph.report {w : CardEnv} {γ : Type} (g : Graph w γ) : CardReport :=
  ⟨g.root.adm.formula, g.leaves.map (·.adm.formula)⟩

def decodeNode {γ : Type} (w : CardEnv) (decodeCert : Json → Except String γ) (j : Json) :
    Except String (CNode w γ) := do
  VE.Time.Wire.shape j ["name", "statement"] ["premises", "certificate"]
  let statement ← j.getObjVal? "statement"
  let adm ← Wire.decodeStatement w statement
  let deduction ← match j.getObjVal? "premises", j.getObjVal? "certificate" with
    | .ok ps, .ok c => pure (some (← strings ps, ← decodeCert c))
    | .error _, .error _ => pure none
    | _, _ => throw "premises and certificate come together"
  pure ⟨← stringField j "name", adm,
    VE.Time.Wire.jsonNodes (VE.Limits.maxJsonDepth + 1) (statement.getObjValD "formula"), deduction⟩

/-- The document's nodes, checked, and its root. -/
def admitGraph {γ : Type} (w : CardEnv) (decodeCert : Json → Except String γ)
    (check : List (CAdmission w) → CAdmission w → γ → Except String Bool) (d : Json) :
    Except String (Graph w γ) := do
  unless w.w6.profiles.contains "documents@1" do
    throw "UnsupportedProfile: cardinality documents require documents@1"
  exactFields d ["root", "nodes"]
  let root ← stringField d "root"
  let array ← (← d.getObjVal? "nodes").getArr?
  if array.size > maxGraphNodes then throw nodeLimit
  let nodes ← array.toList.mapM (decodeNode w decodeCert)
  let entries ← checkGraph w check nodes 0 0 ∅
  match entries[root]? with
  | some r => pure ⟨nodes, r⟩
  | none => throw graphRejected

/-! ## Soundness -/

theorem lookup_mem {w : CardEnv} {acc : Entries w} {p : String} {e : Entry w}
    (h : lookup acc p = .ok e) : acc[p]? = some e := by
  unfold lookup at h
  split at h
  · cases h
    assumption
  · cases h

theorem mapM_lookup_mem {w : CardEnv} {acc : Entries w} :
    ∀ {ps : List String} {cs : List (Entry w)}, ps.mapM (lookup acc) = .ok cs → ∀ c ∈ cs, ∃ p : String, acc[p]? = some c
  | [], cs, h => by
    simp only [List.mapM_nil, pure, Except.pure, Except.ok.injEq] at h
    subst h
    simp
  | p :: ps, cs, h => by
    simp only [List.mapM_cons, bind, Except.bind] at h
    split at h
    · cases h
    · rename_i e he
      split at h
      · cases h
      · rename_i es hes
        simp only [pure, Except.pure, Except.ok.injEq] at h
        subst h
        intro c hc
        rcases List.mem_cons.mp hc with rfl | hc
        · exact ⟨p, lookup_mem he⟩
        · exact mapM_lookup_mem hes c hc

theorem union_testBit : ∀ (sets : List Nat) (s : Nat) (i : Nat),
    (s.testBit i = true ∨ ∃ t ∈ sets, t.testBit i = true) → (sets.foldl (· ||| ·) s).testBit i = true
  | [], s, i, h => by simpa using h
  | t :: ts, s, i, h => by
    apply union_testBit ts
    rcases h with h | ⟨u, hu, hx⟩
    · exact .inl (by simp [Nat.testBit_or, h])
    · rcases List.mem_cons.mp hu with rfl | hu
      · exact .inl (by simp [Nat.testBit_or, hx])
      · exact .inr ⟨u, hu, hx⟩

theorem checkGraph_sound {γ : Type} {w : CardEnv} {check : List (CAdmission w) → CAdmission w → γ → Except String Bool}
    (hc : Checks.{v} w check) (all : List (CNode w γ)) :
    ∀ (ns : List (CNode w γ)) (i used : Nat) (acc out : Entries w), all.drop i = ns →
      (∀ (p : String) e, acc[p]? = some e → Entry.Sound.{v} all e) → checkGraph w check ns i used acc = .ok out →
      ∀ (p : String) e, out[p]? = some e → Entry.Sound.{v} all e
  | [], _, _, acc, out, _, hacc, h => by
    simp only [checkGraph, Except.ok.injEq] at h
    subst h
    exact hacc
  | n :: ns, i, used, acc, out, hns, hacc, h => by
    have hn : all[i]? = some n := by
      have := (List.getElem?_drop (xs := all) (i := i) (j := 0)).symm
      rw [hns, Nat.add_zero] at this
      exact this
    have hrest : all.drop (i + 1) = ns := by
      rw [← List.drop_drop, hns]
      rfl
    have hins : ∀ (x : Entry w), Entry.Sound.{v} all x → ∀ (p : String) e,
        (acc.insert n.name x)[p]? = some e → Entry.Sound.{v} all e := by
      intro x hx p e he
      rw [Std.HashMap.getElem?_insert] at he
      split at he
      · cases he
        exact hx
      · exact hacc p e he
    simp only [checkGraph] at h
    split at h
    · cases h
    split at h
    · rename_i hd
      refine checkGraph_sound hc all ns _ _ _ out hrest (hins _ ?_) h
      intro α T _ hx
      exact hx i n hn hd Nat.testBit_two_pow_self
    · split at h
      · cases h
      split at h
      · cases h
      rename_i children hch
      split at h
      · cases h
      split at h
      · rename_i hcert
        refine checkGraph_sound hc all ns _ _ _ out hrest (hins _ ?_) h
        have hmem := mapM_lookup_mem hch
        intro α T hT hx
        apply hc _ _ _ hcert α T hT
        intro a ha
        obtain ⟨b, hb, rfl⟩ := List.mem_map.mp ha
        obtain ⟨c, hcm, rfl⟩ := List.mem_map.mp hb
        obtain ⟨p, hp⟩ := hmem c hcm
        exact hacc p c hp α T hT fun j m hm hmd hml =>
          hx j m hm hmd (union_testBit _ _ _ (.inr ⟨c.leaves, List.mem_map_of_mem hcm, hml⟩))
      · cases h
      · cases h

/-- A decoded node's statement is the request node's, decoded by `decodeStatement`. -/
theorem decodeNode_statement {γ : Type} {w : CardEnv} {decodeCert : Json → Except String γ} {j : Json}
    {n : CNode w γ} (h : decodeNode w decodeCert j = .ok n) :
    ∃ s, j.getObjVal? "statement" = .ok s ∧ Wire.decodeStatement w s = .ok n.adm := by
  unfold decodeNode at h
  simp only [bind, Except.bind, pure, Except.pure] at h
  split at h; · cases h
  split at h; · cases h
  rename_i s hs
  split at h; · cases h
  rename_i a ha
  refine ⟨s, hs, ?_⟩
  suffices n.adm = a by rw [this]; exact ha
  split at h
  · iterate 3 (split at h; · cases h)
    cases h; rfl
  · split at h; · cases h
    cases h; rfl
  · cases h

/-- An admitted graph's report is sound: its root holds wherever its leaves hold. -/
theorem admitGraph_sound {γ : Type} {w : CardEnv} {decodeCert : Json → Except String γ}
    {check : List (CAdmission w) → CAdmission w → γ → Except String Bool} (hc : Checks.{v} w check) {d : Json}
    {g : Graph w γ} (h : admitGraph w decodeCert check d = .ok g) : CardReport.Sound.{v} w.env g.report := by
  unfold admitGraph at h
  simp only [bind, Except.bind, pure, Except.pure] at h
  split at h
  · iterate 4 (split at h; · cases h)
    split at h; · cases h
    split at h; · cases h
    rename_i nodes _
    split at h; · cases h
    rename_i entries hg
    split at h
    · rename_i r hr
      cases h
      have hroot := checkGraph_sound hc nodes nodes 0 0 ∅ entries List.drop_zero
        (fun _ _ h => by simp at h) hg _ r hr
      intro α T hT hleaves
      apply hroot α T hT
      intro i n hn _ hl
      apply hleaves
      refine List.mem_map.mpr ⟨n, List.mem_map.mpr ⟨(n, i), ?_, rfl⟩, rfl⟩
      exact List.mem_filter.mpr ⟨List.mem_zipIdx_iff_getElem?.mpr hn, hl⟩
    · cases h
  · cases h

end VE.Cardinality.Document
