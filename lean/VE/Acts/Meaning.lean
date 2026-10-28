import VE.Acts.Grammar
import VE.Acts.Tree

/-! The meaning of a derivation of an act phrase: its act tree (docs/spec/act-phrases.md 1.5, 5.3; plan D9 (i)).

The meaning is computed bottom-up: each node's **pieces** come from its children's and its rule. A rule's kind (5.2's
last column) is read from the rule itself, `closed (schema V)` at the node's index, which is the rule the grammar
numbered there: its left side, the shape of its right side, and, for the five edges whose two rules are alike, which
of the two it is (the first reads over the near end, the second over all). So the rule table stays the one owner of
the rules, and no kind is written twice. A derivation has no meaning when a joined filler whose marker is written once
has a first or last part of two or more words (D9 (i)), or when an atom does not fit its frame (`atomOk`).
-/

namespace VE.Acts
open Lexical (Tok)
open VE.Grammar (Tree Meaning)

/-- Which atoms an element reads over (5.3): its own item's (an edge's near end: the first item, or the last item or
part), or all. -/
inductive Att | own | all
  deriving DecidableEq, Repr
/-- An argument (marker and filler) or a modifier of an atom. -/
inductive Elt | arg (m : String) (fl : Filler) | mod (md : Modifier)
  deriving DecidableEq, Repr
/-- A node's meaning before its act: words, parts, join words, function words, a head, a list of parts, an
element, a split construct (its join, whether a split marker's, one element per member), an item or an act. -/
inductive Piece
  | w (s : String) | part (p : Part) | j (j : Join) | fw (to be : Bool) | head (ws : List String)
  | list (j : Join) (ps : List Part) | elt (e : Elt) (a : Att) | split (j : Join) (sp : Bool) (es : List Elt)
  | item (fw : Option (Bool × Bool)) (h : List String) (es : List Piece) | act (A : Act)
  deriving Repr
/-- The atom with one more argument or modifier, after the others. -/
def Atom.add (a : Atom) : Elt → Atom
  | .arg m fl => { a with args := a.args ++ [(m, fl)] }
  | .mod md => { a with mods := a.mods ++ [md] }
/-- Atoms `as` with the piece `p` of atom `k` added: to `k` alone or, read over all, to every atom; a split construct
makes one atom per member. -/
def addPiece (k : Nat) (as : List Atom) : Piece → List Atom
  | .elt e a => as.mapIdx (fun i x => if a == .all || i == k then x.add e else x)
  | .split _ _ es => as.flatMap (fun x => es.map x.add)
  | _ => as
/-- A join of atoms (1.5): *and* is `all`, *or* and *nor* are `any`. -/
def joinAct (shared sp : Bool) : Join → List Atom → Act
  | .and => .all shared sp
  | .or => .any false sp
  | .nor => .any true sp
/-- An item's atom before its elements: its function words and head. -/
def baseAtom (fw : Option (Bool × Bool)) (h : List String) : Atom :=
  ⟨(fw.map (·.1)).getD false, (fw.map (·.2)).getD false, h, [], []⟩
/-- A single item (5.3, `singleAct`): its elements in order, each added to the last atom or to all; a split construct
makes the parts. -/
def singleAct : Piece → Option Act
  | .item fw h es =>
    let as := es.foldl (fun as p => addPiece (as.length - 1) as p) [baseAtom fw h]
    match es.findSome? (fun | .split j sp _ => some (j, sp) | _ => none), as with
    | some (j, sp), _ => some (joinAct true sp j as)
    | none, [a] => some (.one a)
    | none, _ => none
  | _ => none
/-- A coordination (5.3, `coordAct`): one atom per item, later items taking the first's function words when they are
shared; each element is added to its own item's atom, or to all. -/
def coordAct (shared : Bool) (j : Join) (its : List Piece) : Option Act := do
  let its ← its.mapM (fun | .item fw h es => some (fw, h, es) | _ => none)
  let fw0 := its.head?.bind (·.1)
  let as := its.map (fun (fw, h, _) => baseAtom (if shared then fw0 else fw) h)
  pure (joinAct shared false j (its.zipIdx.foldl (fun as ((_, _, es), i) => es.foldl (addPiece i) as) as))
/-- A list's join word (exactly one) and its members, the other pieces. -/
def listOf (cs : List Piece) : Option (Join × List Piece) :=
  match cs.filterMap (fun | .j j => some j | _ => none) with
  | [j] => some (j, cs.filter (!· matches .j _))
  | _ => none
/-- An item from its pieces: its one head, its function words, and its pieces in order (`addPiece` reads the
elements). -/
def itemOf (cs : List Piece) : Option Piece :=
  match cs.filterMap (fun | .head h => some h | _ => none) with
  | [h] => some (.item (cs.findSome? (fun | .fw t b => some (t, b) | _ => none)) h cs)
  | _ => none
/-- A node's pieces from its children's and its rule `r`. `second` says the rule equals the one before it: only an
edge's two rules are written alike (5.2), and the second reads over all. -/
def applyRule (r : RuleS) (second : Bool) (cs : List Piece) : Option (List Piece) :=
  let att := if second then Att.all else .own
  let words := cs.filterMap (fun | .w s => some s | _ => none)
  let part : Piece → Option Part := fun | .part p | .elt (.arg _ (.one p)) _ => some p | _ => none
  let toAll : Piece → Piece := fun | .elt (.arg m f) .own => .elt (.arg m f) .all | p => p
  match r.lhs, r.rhs, cs with
  | _, [.t (.adv _)], [.w v] => some [.elt (.mod (.adv v.toLower)) att]
  | .F _ (.AR m), _, [.part p] => some [.elt (.arg m (.one p)) .own]
  | .F _ (.OL _), _, _ => some cs
  | _, [.n (.MK m), _], [.part p] => some [.elt (.mod (.prep m p)) att]
  | .MK _, _, _ => some []
  | .J, _, [.w v] => ([("and", Join.and), ("or", .or), ("nor", .nor)].lookup v.toLower).map ([.j ·])
  | .FW, _, _ => some [.fw ((words.map (·.toLower)).contains "to") ((words.map (·.toLower)).contains "be")]
  | .F _ .HD, _, _ => some [.head (words.map (·.toLower))]
  | .F _ .FL, _, _ => some (if words.length == cs.length && !cs.isEmpty then [.part (.words words)] else cs)
  | .F _ .PL, _, _ | .F _ (.RL _), _, _ => do
    let (j, ms) ← listOf cs
    let ps ← ms.mapM part
    -- D9 (i): a marker written once (`PL`) refuses a first or last part of two or more words
    let long : Option Part → Bool := fun | some (.words (_ :: _ :: _)) => true | _ => false
    if r.lhs matches .F _ .PL && (long ps.head? || long ps.getLast?) then none else some [.list j ps]
  | .F _ (.LST m true), _, [.list j ps] => some [.split j true (ps.map (.arg m ∘ .one))]
  | .F _ (.LST m false), _, [.list j ps] => some [.elt (.arg m (.joined j ps)) .own]
  | .F _ .O, _, [.part p] => some [.elt (.arg "" (.one p)) .own]
  | .F _ .O, _, [.list j ps] => some [.elt (.arg "" (.joined j ps)) .own]
  | .F _ .OS, _, [.list j ps] => some [.split j true (ps.map (.arg "" ∘ .one))]
  | .F _ .MG, _, _ => do
    let (j, ms) ← listOf cs
    some [.split j false (← ms.mapM (fun | .elt e _ => some e | _ => none))]
  | .F _ .PX, _, _ | .C .rnr, _, _ => some (cs.map toAll)
  | .SINGLE, _, _ => do some [.act (← singleAct (← itemOf cs))]
  | .F1 _ _, _, _ | .L _ _, _, _ => do some [← itemOf cs]
  | .COORD, .n (.F1 own _) :: _, _ => do
    let (j, its) ← listOf cs
    some [.act (← coordAct (!own) j its)]
  | .S, _, _ => some (cs.filter (· matches .act _))                     -- the subject `{0}` is dropped here
  | _, _, _ => some cs
mutual
/-- The pieces of a derivation: a word token is a word, a slot or fixed phrase a part, a comma nothing. -/
def piecesOf (rs : Array RuleS) : Tree Tok → Option (List Piece)
  | .leaf (.word v) => some [.w v]
  | .leaf (.slot i) => some [.part (.slot i)]
  | .leaf (.fixed i) => some [.part (.fixed i)]
  | .leaf .comma => some []
  | .node i kids => do
    let r ← rs[i]?
    applyRule r (0 < i && rs[i - 1]? == some r) (← piecesKids rs kids)
def piecesKids (rs : Array RuleS) : List (Tree Tok) → Option (List Piece)
  | [] => some []
  | k :: ks => do pure ((← piecesOf rs k) ++ (← piecesKids rs ks))
end
/-- An atom fits its frame (5.3): its head is declared; it has an object exactly when the frame lists `""`; every
argument marker is the frame's, every modifier marker one of its modifier markers, every adverb declared. -/
def atomOk (V : Vocab) (a : Atom) : Bool :=
  match V.frames.find? (·.head == a.head) with
  | none => false
  | some f =>
    (a.args.filter (·.1 == "")).length == (if f.markers.contains "" then 1 else 0) &&
    a.args.all (f.markers.contains ·.1) &&
    a.mods.all (fun | .adv w => V.adverbs.contains w | .prep m _ => f.mods.contains m)
/-- Every atom fits its frame, and a join has at least two. -/
def actOk (V : Vocab) : Act → Bool
  | .one a => atomOk V a
  | .all _ _ ps | .any _ _ ps => 2 ≤ ps.length && ps.all (atomOk V)
/-- The meaning of a derivation (5.3): its act tree, or no meaning. -/
def meaning (V : Vocab) : Meaning Tok Unit String Act :=
  let rs := (closed (schema V)).toArray
  fun _ t => match piecesOf rs t with
    | some [.act A] => if actOk V A then .ok (A, false, ()) else .error "InvalidInput: an atom does not fit its frame"
    | _ => .error "InvalidInput: this derivation has no meaning"

end VE.Acts
