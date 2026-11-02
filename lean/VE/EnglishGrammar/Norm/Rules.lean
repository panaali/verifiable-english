import VE.EnglishGrammar.Read
import VE.EnglishGrammar.Fixed.Norms
import VE.Norms.Wire
import VE.Grammar.Extension

/-! The norm grammar, its actions and types (docs/spec/english-lean-s6.md 2.5): `grammar E L` first and unchanged,
then the norm table (`Fixed/Norms.lean`, generated from `ve/english_grammar/norms@0.json`), then one consequence row
per wording `_consequence` and `_block_grammar` generate for a regulated predicate and a sign
(`ve/norm_english.py:90-109`, :216-228). A norm action reads its arguments once: the numerals, the rule list, the
consequence and the conditions, each condition in a fresh discourse state under the consequence's bindings (R4). -/

namespace VE.EnglishGrammar.Norm
open VE.Grammar VE.EnglishGrammar

/-- Whether a polarity is one that the role's consequence rows generate. It is here, not in `Value.lean`, so
that `Value.lean` imports only `Syntax.lean`. -/
def Polarity.fits : Polarity → VE.Norms.Role → Bool
  | .modal .must, .obligation => true
  | .modal .needNot, .obligation => true
  | .modal .may, .permission => true
  | .modal .mustNot, .permission => true
  | .plain _, .plain => true
  | _, _ => false

/-- R6: the regulated declarations, as the norms route decodes them (`decodeSource`, `Wire.lean:371`). -/
def regulatedOf (E : Env) : List VE.Norms.Regulated :=
  match VE.Norms.Wire.decodeNormsEnvironment E.source (acts := true) with
  | .ok ne => ne.regulated
  | .error _ => []

/-- `_bindings` (`norm_english.py:28-44`): the scope, innermost first, and each slot's display; none when a sort
has no noun or occurs three times. -/
def bindings (L : Lexicon) (sorts : List String) : Option (Scope × List String) := do
  let slots ← (List.range sorts.length).zip sorts |>.mapM fun (i, s) => do
    let noun ← L.nouns.lookup s
    match sorts.count s, (sorts.take i).count s with
    | 1, _ => pure ((s, "that " ++ noun), noun)
    | 2, 0 => pure ((s, "the first " ++ noun), "first " ++ noun)
    | 2, _ => pure ((s, "the second " ++ noun), "second " ++ noun)
    | _, _ => none
  pure ((slots.map (·.1)).reverse, slots.map (·.2))

/-- The force a role's consequence of sign `b` has (`norm_english.py:97-100`). -/
def Polarity.of : VE.Norms.Role → Bool → Polarity
  | .obligation, b => .modal (if b then .must else .needNot)
  | .permission, b => .modal (if b then .may else .mustNot)
  | .plain, b => .plain b

/-- `_consequence`'s wording of `r` with sign `b` over the displays `ds` and the bindings `σ`: the act with its
modal word, or the plain wording (its negative, or the universal form when no negative is selected). -/
def wording (L : Lexicon) (r : VE.Norms.Regulated) (σ : Scope) (ds : List String) (b : Bool) : Option String :=
  let fill (xs : List String) (w : String) := (fillHoles w fun k => xs.getD k "").2
  let subjects := ("Every " ++ ds.headD "") :: ds.tail.map ("each " ++ ·)
  let modal (m : String) := r.act.map fun a => fill subjects (replaceFirst a "{0} " ("{0} " ++ m ++ " "))
  match r.role with
  | .obligation => modal (if b then "must" else "need not")
  | .permission => modal (if b then "may" else "must not")
  | .plain =>
    match (if b then none else L.negatives.lookup r.name), L.wordings.lookup r.name with
    | some w, _ => some (fill subjects w)
    | none, some w =>
      if b then some (fill subjects w)
      else some (capitalise (", ".intercalate (("for every " ++ ds.headD "") :: ds.tail.map ("for each " ++ ·))) ++
        ", it is not the case that " ++ fill (σ.reverse.map (·.2)) w)
    | none, none => none

/-- The consequence rows (spec 2.5): for each regulated predicate with one or more arguments and each sign, each
variant of its wording that lexes as one sentence, with its clause skeleton and its bindings. -/
def consequences (E : Env) (L : Lexicon) : List (List (Sym Terminal) × Clause × Scope) :=
  (regulatedOf E).flatMap fun r => match r.sorts, bindings L r.sorts with
    | s1 :: _, some (σ, ds) => [true, false].flatMap fun b => match wording L r σ ds b with
      | none => []
      | some w =>
        let anyVariant := if ds.length == 2 then [w.replace ("each " ++ ds.getD 1 "") ("any " ++ ds.getD 1 "")] else []
        let noVariant := if r.role == .permission && !b then
          [replaceFirst w ("Every " ++ ds.headD "" ++ " must not ") ("No " ++ ds.headD "" ++ " may ")] else []
        (w :: anyVariant ++ noVariant).eraseDups.filterMap fun v => (textSyms v contentTerminal).map fun syms =>
          (syms, ⟨.every s1, .of r.role b, .strict, r.name, [], .top, [], []⟩, σ)
    | _, _ => []

/-- A norm row's symbol, with norm nonterminal `i` numbered `n + i`. -/
def NormSym.sym (n : Nat) : NormSym → Sym Terminal
  | .t a => .t a
  | .base m => .n m
  | .own i => .n (n + i)

/-- `grammar E L`'s rules first and unchanged, then the norm table's rows (`ve/english_grammar/norms@0.json`),
then the consequence rows generated from `regulatedOf E` and `L`. New nonterminals are numbered from
`(grammar E L).rank.size`; the start symbol is the norm sentence. -/
def normGrammar (E : Env) (L : Lexicon) : VE.Grammar.Grammar Terminal :=
  let n := (grammar E L).rank.size
  let k := (acts E L).size
  { rules := (grammar E L).rules ++
      normRows.mapIdx (fun i r => { lhs := n + r.lhs, rhs := r.rhs.map (·.sym n), act := k + i, tag := r.tag }) ++
      (consequences E L).toArray.mapIdx fun i (syms, c, _) =>
        { lhs := n + normConsequence, rhs := syms, act := k + normRows.size + i, tag := "consequence." ++ c.pred }
    start := n
    rank := (grammar E L).rank ++ normRanks }

/-- `ty E L` below `(grammar E L).rank.size`; the norm types above. -/
def normTy (E : Env) (L : Lexicon) : Nat → Ty :=
  fun i => if i < (grammar E L).rank.size then ty E L i else normTys.getD (i - (grammar E L).rank.size) .tok

/-- What a norm action reads from one argument: a numeral, a rule list, a consequence or a condition. -/
inductive Arg where
  | num (n : Nat)
  | refs (ns : List Nat)
  | cons (c : Clause) (σ : Scope)
  | cond (f : Sem .formula)

/-- The arguments a norm action reads, in order; a word or a mark is read as nothing. -/
def args : (τs : List Ty) → Args sig τs → List Arg
  | [], _ => []
  | .tok :: τs, (t, xs) => (match t with | .numeral v => [.num v.toNat] | _ => []) ++ args τs xs
  | .refs :: τs, (ns, xs) => .refs ns :: args τs xs
  | .consequence :: τs, ((c, σ), xs) => .cons c σ :: args τs xs
  | .formula :: τs, (f, xs) => .cond f :: args τs xs
  | _ :: τs, (_, xs) => args τs xs

def Arg.nums : Arg → List Nat
  | .num n => [n]
  | .refs ns => ns
  | _ => []

/-- A condition's value under the bindings `σ`, in a fresh discourse state (R4). -/
def Arg.read (σ : Scope) : Arg → Except Reject EFormula
  | .cond f => f { Ctx.start DState.init with scope := σ }
  | _ => .error .internal

/-- A norm sentence's piece and the next state (spec 2.3): a header or a precedence line closes the scope, a
clause opens its consequence's, an except-when sentence reads its condition under it. -/
def NormAct.step : NormAct → List Arg → NState → Except Reject (Piece × NState)
  | .header, .num n :: xs, _ => .ok (.header ⟨n, xs.flatMap Arg.nums⟩, ⟨none⟩)
  | .precedence, [.num n, .num m], _ => .ok (.precedence n m, ⟨none⟩)
  | .clause g, .cons c σ :: xs, _ => do
    let φs ← xs.mapM (·.read σ)
    let c := if g then { c with guard := φs.headD .top, carveOuts := φs.tail } else { c with carveOuts := φs }
    .ok (.clause c, ⟨some σ⟩)
  | .exceptWhen, [x], st => do .ok (.exceptWhen (← x.read (st.scope.getD [])), st)
  | _, _, _ => .error .internal

/-- A norm row's action over the argument types `τs`: a rule list, or a norm sentence whose mark is `false`. -/
def NormAct.action (τs : List Ty) : NormAct → Action sig
  | .refs => ⟨τs, .refs, fun xs => (args τs xs).flatMap Arg.nums⟩
  | a => ⟨τs, .norm, fun xs st => (fun (p, st2) => (p, false, st2)) <$> a.step (args τs xs) st⟩

/-- `acts E L` first and unchanged, then the norm actions. -/
def normActs (E : Env) (L : Lexicon) : Array (VE.Grammar.Action sig) :=
  let n := (grammar E L).rank.size
  acts E L ++ normRows.map (fun r => r.act.action (rhsTys (normTy E L) (r.rhs.map (·.sym n)))) ++
    (consequences E L).toArray.map fun (syms, c, σ) => constant .consequence (c, σ) (rhsTys (normTy E L) syms)

def prefixMap : VE.Grammar.RuleMap := ⟨id, id⟩

/-- The value of a norm sentence's tree: the start symbol's value applied to the state. -/
def normMeaning (G : VE.Grammar.Grammar Terminal) (acts : Array (VE.Grammar.Action sig)) :
    VE.Grammar.Meaning Tok NState Reject Piece :=
  fun st t => match t.sem G sig acts with
    | some ⟨.norm, f⟩ => f st
    | _ => .error .internal

end VE.EnglishGrammar.Norm
