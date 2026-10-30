import VE.Calc.Csv
import VE.Calc.Jsonl
import VE.CertificateWire

/-! Counted values over pinned bytes (spec 4.3, plan 3.3): a table is read only from bytes whose SHA-256, recomputed
here, is the declared handle, and each counted value runs within the case's budget (statement review J2). -/

namespace VE.Calc

inductive Format where
  | csv | jsonl
  deriving Repr, DecidableEq

structure DataDecl where
  handle : String
  format : Format
  columns : List (String × ColType)

def decodeTable : Format → List (String × ColType) → ByteArray → Except String Table
  | .csv => decodeCsv
  | .jsonl => decodeJsonl

def Filter.columns : Filter → List String
  | .all => []
  | .isText c _ | .isNotText c _ | .equals c _ | .notEquals c _ | .isTrue c | .isFalse c => [c]
  | .and f g | .or f g => f.columns ++ g.columns

def Agg.columns : Agg → List String
  | .count => []
  | .sum c | .mean c | .min c | .max c => [c]

/-- The operational counted result of a declaration over the registered handles, within the budget `limit` (J2); an
error is a refusal (`UnknownHandle`, `DigestMismatch`, `TableFormat`, `UnknownColumn`). -/
def runCounted (limit : Nat) (handles : List (String × ByteArray)) (dd : DataDecl) (f : Filter) (a : Agg) :
    Except String Counted := do
  let some bytes := handles.lookup dd.handle | throw s!"UnknownHandle: {dd.handle}"
  unless VE.CertificateWire.sha256 bytes = dd.handle do throw s!"DigestMismatch: {dd.handle}"
  let T ← decodeTable dd.format dd.columns bytes
  match (f.columns ++ a.columns).find? (!T.columns.contains ·) with
  | some c => throw s!"UnknownColumn: {c}"
  | none => pure (match Agg.runB limit T f a with
    | some v => .ok v
    | none => .exhausted)

/-- The handle, digest and table a successful run read. -/
theorem runCounted_reads (limit : Nat) (handles : List (String × ByteArray)) (dd : DataDecl) (f : Filter) (a : Agg)
    (r : Counted) (h : runCounted limit handles dd f a = .ok r) :
    ∃ bytes T, handles.lookup dd.handle = some bytes ∧ VE.CertificateWire.sha256 bytes = dd.handle ∧
      decodeTable dd.format dd.columns bytes = .ok T ∧
      r = match Agg.runB limit T f a with | some v => .ok v | none => .exhausted := by
  unfold runCounted at h
  cases hl : handles.lookup dd.handle with
  | none => simp [hl] at h
  | some bytes =>
      simp only [hl] at h
      by_cases hd : VE.CertificateWire.sha256 bytes = dd.handle
      · cases ht : decodeTable dd.format dd.columns bytes with
        | error e => simp [hd, ht] at h; cases h
        | ok T =>
            simp only [hd, ht, ↓reduceIte, bind, Except.bind, pure, Except.pure] at h
            refine ⟨bytes, T, rfl, hd, ht, ?_⟩
            cases hc : List.find? (fun x => !T.columns.contains x) (f.columns ++ a.columns) <;>
              simp only [hc] at h
            · cases h; rfl
            · cases h
      · simp [hd] at h; cases h

/-- A counted value is computed only from bytes whose SHA-256 is the declared handle, and a completed result is the
aggregate's value, undefined included. -/
theorem counted_bound (limit : Nat) (handles : List (String × ByteArray)) (dd : DataDecl) (f : Filter) (a : Agg)
    (v : Option Rat) (h : runCounted limit handles dd f a = .ok (.ok v)) :
    ∃ bytes T, handles.lookup dd.handle = some bytes ∧ VE.CertificateWire.sha256 bytes = dd.handle ∧
      decodeTable dd.format dd.columns bytes = .ok T ∧ Agg.run T f a = v := by
  obtain ⟨bytes, T, hl, hd, ht, hr⟩ := runCounted_reads limit handles dd f a _ h
  refine ⟨bytes, T, hl, hd, ht, ?_⟩
  cases hb : Agg.runB limit T f a with
  | none => simp [hb] at hr
  | some w => simp only [hb, Counted.ok.injEq] at hr; exact (Agg.runB_sound limit T f a w hb ▸ hr).symm

/-- Exhaustion is reported only when the budgeted aggregate really did not complete. -/
theorem counted_exhausted (limit : Nat) (handles : List (String × ByteArray)) (dd : DataDecl) (f : Filter) (a : Agg)
    (h : runCounted limit handles dd f a = .ok .exhausted) :
    ∃ bytes T, handles.lookup dd.handle = some bytes ∧ VE.CertificateWire.sha256 bytes = dd.handle ∧
      decodeTable dd.format dd.columns bytes = .ok T ∧ Agg.runB limit T f a = none := by
  obtain ⟨bytes, T, hl, hd, ht, hr⟩ := runCounted_reads limit handles dd f a _ h
  refine ⟨bytes, T, hl, hd, ht, ?_⟩
  cases hb : Agg.runB limit T f a with
  | none => rfl
  | some w => simp [hb] at hr

end VE.Calc
