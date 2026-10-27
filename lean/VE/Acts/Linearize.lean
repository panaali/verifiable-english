import VE.Acts.Syntax
import VE.Acts.Tree
import VE.Norms.Tree

/-! The normal form and the text of a simple act (docs/spec/act-phrases.md 5.5).

The normal form of an atom is `{0}`, *to*, *be*, its adverbs, its head, its object, its other arguments in their order
(marker words, then the filler; a joined filler as `A, B or C` after its marker once), then its prepositional
modifiers. Its text separates the tokens by spaces, attaches a comma to the token before it, and writes a fixed
phrase as declared (canonical). A part's act (`partAct`, used by the elaboration of 6.3) is that text, with *to*
exactly when its predicate is plain.
-/

namespace VE.Acts
open Lexical (Tok)

def joinWord : Join → String
  | .and => "and"
  | .or => "or"
  | .nor => "nor"

def Part.toks : Part → List Tok
  | .slot i => [.slot i]
  | .fixed i => [.fixed i]
  | .words ws => ws.map Tok.word

/-- "A", "A and B", "A, B and C". -/
def listToks (j : Join) : List Part → List Tok
  | [] => []
  | [p] => p.toks
  | [p, q] => p.toks ++ [Tok.word (joinWord j)] ++ q.toks
  | p :: rest => p.toks ++ [Tok.comma] ++ listToks j rest

def Filler.toks : Filler → List Tok
  | .one p => p.toks
  | .joined j ps => listToks j ps

def Atom.normal (a : Atom) : List Tok :=
  [Tok.slot 0] ++ (if a.toWord then [Tok.word "to"] else []) ++ (if a.beWord then [Tok.word "be"] else []) ++
  a.mods.flatMap (fun md => match md with | .adv w => [Tok.word w] | _ => []) ++ a.head.map Tok.word ++
  (a.args.filter (fun x => x.1 == "")).flatMap (fun x => x.2.toks) ++
  (a.args.filter (fun x => x.1 != "")).flatMap (fun x => (wordsOf x.1).map Tok.word ++ x.2.toks) ++
  a.mods.flatMap (fun md => match md with | .prep m p => (wordsOf m).map Tok.word ++ p.toks | _ => [])

def tokStr (fx : List String) : Tok → String
  | .word w => w
  | .slot i => "{" ++ toString i ++ "}"
  | .fixed i => Lexical.normal (fx.getD i "")
  | .comma => ","

def tokText (fx : List String) (ts : List Tok) : String :=
  ts.foldl (fun acc t => match t with
    | .comma => acc ++ ","
    | _ => if acc.isEmpty then tokStr fx t else acc ++ " " ++ tokStr fx t) ""

/-- `a` with *to* exactly when `inf = some true`, without it when `some false`, as read when `none`. -/
def Atom.withTo (inf : Option Bool) (a : Atom) : Atom := { a with toWord := inf.getD a.toWord }
def Atom.text (fx : List String) (inf : Option Bool) (a : Atom) : String := tokText fx (a.withTo inf).normal

/-- A part's act: its atom's text, with *to* exactly when its predicate is plain (read after *has the right*). -/
def partAct (fx : List String) (role : VE.Norms.Role) (a : Atom) : String := Atom.text fx (some (role == .plain)) a

end VE.Acts
