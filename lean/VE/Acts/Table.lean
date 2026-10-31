import VE.Acts.Linearize

/-! The modal × connective table and the paraphrases of readings (docs/spec/act-phrases.md 1.7, 6.1, 6.2; plan 2.3).

A rule's op is fixed by its predicate's role and its sign. For an op and an act tree the table gives the readings, each
the list of simple acts the rule stands for: `[]` is no reading (refused), two or more make the English ambiguous.
The table holds the distribution equations of the five deontic modals only; it is never used for `intends` or
`believes`. Its equations stay provisional until the experiment AP-7 passes (decision D3).
-/

namespace VE.Acts

/-- A simple act of a reading: an atom, or a whole join read as one act. -/
inductive Simple | atom (a : Atom) | whole (A : Act)
  deriving DecidableEq, Repr

inductive Op | must | needNot | may | mustNot | right
  deriving DecidableEq, Repr

/-- The op of a rule with `sign` on `r`; a plain predicate with sign false has none (1.7). -/
def opOf (r : VE.Norms.Regulated) (sign : Bool) : Option Op :=
  match r.role, sign with
  | .obligation, true => some .must
  | .obligation, false => some .needNot
  | .permission, true => some .may
  | .permission, false => some .mustNot
  | .plain, true => some .right
  | .plain, false => none

/-- *may* and *has the right to*. -/
def freeTable : Act → List (List Simple)
  | .one a => [[.atom a]]
  | .all false _ ps => [ps.map Simple.atom]
  | .all true true ps => [ps.map Simple.atom]
  | .all true false ps => [ps.map Simple.atom, [.whole (.all true false ps)]]
  | .any true _ _ => []
  | .any false true ps => [ps.map Simple.atom]
  | .any false false ps => [ps.map Simple.atom, [.whole (.any false false ps)]]

/-- The plan's 2.3, for the five deontic modals only. -/
def table : Op → Act → List (List Simple)
  | _, .one a => [[.atom a]]
  | .needNot, _ => []
  | .must, .all _ _ ps => [ps.map Simple.atom]
  | .must, .any nor sp ps => if nor || sp then [] else [[.whole (.any nor sp ps)]]
  | .mustNot, .any _ _ ps => [ps.map Simple.atom]
  | .mustNot, .all s sp ps => if sp then [ps.map Simple.atom] else [ps.map Simple.atom, [.whole (.all s sp ps)]]
  | .may, A => freeTable A
  | .right, A => freeTable A

/-! ### The table's equations (6.2) -/

theorem table_one (op : Op) (a : Atom) : table op (.one a) = [[.atom a]] := by
  cases op <;> rfl
theorem table_must_all (s sp : Bool) (ps : List Atom) : table .must (.all s sp ps) = [ps.map Simple.atom] := rfl
theorem table_must_any (ps : List Atom) : table .must (.any false false ps) = [[.whole (.any false false ps)]] := rfl
theorem table_must_any_refused (n sp : Bool) (ps : List Atom) (h : n = true ∨ sp = true) :
    table .must (.any n sp ps) = [] := by
  rcases h with h | h <;> subst h <;> simp [table]
theorem table_mustNot_any (n sp : Bool) (ps : List Atom) : table .mustNot (.any n sp ps) = [ps.map Simple.atom] := rfl
theorem table_mustNot_all (s : Bool) (ps : List Atom) :
    table .mustNot (.all s false ps) = [ps.map Simple.atom, [.whole (.all s false ps)]] := rfl
theorem table_mustNot_all_split (s : Bool) (ps : List Atom) :
    table .mustNot (.all s true ps) = [ps.map Simple.atom] := rfl
theorem table_free_all_own (op : Op) (hop : op = .may ∨ op = .right) (sp : Bool) (ps : List Atom) :
    table op (.all false sp ps) = [ps.map Simple.atom] := by
  rcases hop with h | h <;> subst h <;> rfl
theorem table_free_all_shared (op : Op) (hop : op = .may ∨ op = .right) (ps : List Atom) :
    table op (.all true false ps) = [ps.map Simple.atom, [.whole (.all true false ps)]] := by
  rcases hop with h | h <;> subst h <;> rfl
theorem table_free_all_split (op : Op) (hop : op = .may ∨ op = .right) (ps : List Atom) :
    table op (.all true true ps) = [ps.map Simple.atom] := by
  rcases hop with h | h <;> subst h <;> rfl
theorem table_free_any (op : Op) (hop : op = .may ∨ op = .right) (ps : List Atom) :
    table op (.any false false ps) = [ps.map Simple.atom, [.whole (.any false false ps)]] := by
  rcases hop with h | h <;> subst h <;> rfl
theorem table_free_any_split (op : Op) (hop : op = .may ∨ op = .right) (ps : List Atom) :
    table op (.any false true ps) = [ps.map Simple.atom] := by
  rcases hop with h | h <;> subst h <;> rfl
theorem table_free_nor (op : Op) (hop : op = .may ∨ op = .right) (sp : Bool) (ps : List Atom) :
    table op (.any true sp ps) = [] := by
  rcases hop with h | h <;> subst h <;> rfl
theorem table_needNot (A : Act) (h : ∀ a, A ≠ .one a) : table .needNot A = [] := by
  cases A with
  | one a => exact absurd rfl (h a)
  | all => rfl
  | any => rfl

/-! ### Paraphrases (2.2, 5.5, 6.2) -/

/-- "A", "A and B", "A, B and C". -/
def listText (j : String) : List String → String
  | [] => ""
  | [x] => x
  | [x, y] => x ++ " " ++ j ++ " " ++ y
  | x :: rest => x ++ ", " ++ listText j rest

/-- A tree rendered from its atoms: each atom's text after its `{0} `, as a list joined by the tree's join word. -/
def Act.text (fx : List String) (inf : Option Bool) : Act → String
  | .one a => Atom.text fx inf a
  | .all _ _ ps => "{0} " ++ listText "and" (ps.map (fun a => (Atom.text fx inf a).drop 4))
  | .any nor _ ps => "{0} " ++ listText (if nor then "nor" else "or") (ps.map (fun a => (Atom.text fx inf a).drop 4))

def Simple.text (fx : List String) (inf : Option Bool) : Simple → String
  | .atom a => Atom.text fx inf a
  | .whole A => Act.text fx inf A

/-- *To* after *has the right* and *is entitled*, never after *must*, *need not*, *may* or *must not*. -/
def Op.inf : Op → Bool
  | .right => true
  | _ => false

/-- "must", "need not", "may", "must not"; for `.right`, the declaration's form ("has the right" when none). -/
def modalText : Op → Option Lexical.Form → String
  | .must, _ => "must"
  | .needNot, _ => "need not"
  | .may, _ => "may"
  | .mustNot, _ => "must not"
  | .right, f => (f.getD .right).text

/-- One simple act under a modal: the subject, the modal words, the act in the modal's form. -/
def sentence (fx : List String) (op : Op) (f : Option Lexical.Form) (x : Simple) : String :=
  "{0} " ++ modalText op f ++ " " ++ (Simple.text fx (some op.inf) x).drop 4

/-- 2.2: one simple act; a split (", and " for two, "; …; and " for more); a whole join with its gloss. -/
def paraphrase (fx : List String) (op : Op) (f : Option Lexical.Form) : List Simple → String
  | [.whole (.all s sp ps)] => sentence fx op f (.whole (.all s sp ps)) ++ ", as one act done together (not each on its own)."
  | [.whole A] => sentence fx op f (.whole A) ++ ", as one act done in any one of these ways (not each way on its own)."
  | [x] => sentence fx op f x ++ "."
  | [x, y] => sentence fx op f x ++ ", and " ++ sentence fx op f y ++ "."
  | xs => "; ".intercalate ((xs.dropLast).map (sentence fx op f)) ++ "; and " ++
      (xs.getLast?.map (sentence fx op f)).getD "" ++ "."

/-- "1. t₁ 2. t₂ …": each text numbered from 1, separated by one space. -/
def numbered (ts : List String) : String :=
  " ".intercalate ((List.range ts.length).zip ts |>.map (fun (i, t) => toString (i + 1) ++ ". " ++ t))

/-- The first pair `(i, j)`, `i < j`, counted from `k`, of equal texts. -/
def firstEqualPair : Nat → List String → Option (Nat × Nat)
  | _, [] => none
  | k, t :: ts => if ts.contains t then some (k, k + 1 + ts.idxOf t) else firstEqualPair (k + 1) ts

/-- The texts of one listing, refused when two coincide (D-32 names the first such pair, from 1). -/
def distinctTexts (what : String) (ts : List String) : Except String (List String) :=
  match firstEqualPair 1 ts with
  | some (i, j) => .error s!"InvalidInput: readings {i} and {j} of {what} read the same in English; rephrase the act"
  | none => .ok ts

/-- The paraphrases of a listing of readings (D-23). -/
def paraphrases (fx : List String) (op : Op) (f : Option Lexical.Form) (what : String) (Rs : List (List Simple)) :
    Except String (List String) :=
  distinctTexts what (Rs.map (paraphrase fx op f))

/-- The texts of a listing of meanings, with no modal (D-15). -/
def meaningTexts (fx : List String) (what : String) (As : List Act) : Except String (List String) :=
  distinctTexts what (As.map (fun A => (Act.text fx none A).drop 4 ++ "."))

theorem firstEqualPair_none : ∀ (k : Nat) (ts : List String), firstEqualPair k ts = none ↔ ts.Nodup
  | _, [] => by simp [firstEqualPair]
  | k, t :: ts => by
    rw [firstEqualPair, List.nodup_cons, ← firstEqualPair_none (k + 1) ts]
    by_cases h : t ∈ ts <;> simp [h]

theorem distinctTexts_ok (what : String) (ts us : List String) :
    distinctTexts what ts = .ok us ↔ us = ts ∧ ts.Nodup := by
  unfold distinctTexts
  cases h : firstEqualPair 1 ts with
  | some p =>
    obtain ⟨i, j⟩ := p
    simp only [reduceCtorEq, false_iff, not_and]
    intro _ hn
    rw [(firstEqualPair_none 1 ts).mpr hn] at h
    cases h
  | none =>
    simp only [Except.ok.injEq]
    exact ⟨fun e => ⟨e.symm, (firstEqualPair_none 1 ts).mp h⟩, fun ⟨e, _⟩ => e.symm⟩

theorem paraphrases_nodup {fx op f what Rs ps} (h : paraphrases fx op f what Rs = .ok ps) :
    ps = Rs.map (paraphrase fx op f) ∧ ps.Nodup := by
  obtain ⟨e, hn⟩ := (distinctTexts_ok what _ ps).mp h
  exact ⟨e, e ▸ hn⟩

end VE.Acts
