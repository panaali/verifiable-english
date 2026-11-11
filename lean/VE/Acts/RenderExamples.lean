import VE.Acts.MeaningExamples
import VE.Acts.NormalUnique

/-! Fixtures of the rendering round trip (docs/spec/act-phrases.md 5.5, 5.6 `read_normal`, 11.2, 11.2a).

Each atom's normal form text and what `read` gives it at the production limits: G6's render pair and N1 to N5 read
back as `one` of the atom in canonical order; `Atom.canon`'s reordering; `normalOk` on both sides of each of its
conditions, with the review's counterexamples FR3 to FR5 and C1 to C4 (docs/act-phrases/ap-2bb/QUESTION-read_normal.md)
on the refused side. Each family is an instance of `read_normal` and of its existence half `NormalProofs.normal_derived`
(ap-2bc), under the `framesOk` and `normalOk` the `#guard`s check.
-/

namespace VE.Acts.RenderExamples
open VE.Acts VE.Acts.Examples VE.Acts.RuleExamples VE.Acts.TableExamples

/-- What the normal form of `a` reads back as, at the production limits. -/
def back (V : Vocab) (a : Atom) : ReadOutcome Act := read V rawCap stepBudget a.normal.toArray
/-- `read_normal`'s conclusion for `a`, at the production limits. -/
def roundTrip (V : Vocab) (a : Atom) : Bool := back V a == .ok (.one a.canon)
def text (fx : List String) (a : Atom) : String := tokText fx a.normal
def noTo (a : Atom) : Atom := { a with toWord := false }

/-! ### G6's render pair and N1 to N5 (11.2) -/

#guard [torture, cruel].map (text fx6) ==
  ["{0} be subjected to torture", "{0} be subjected to cruel, inhuman or degrading treatment or punishment"]
#guard [torture, cruel].all (fun a => normalOk V6 a && roundTrip V6 a)                                       -- G6
def n1 : Atom := ⟨false, false, ["form"], [("", .one (w "trade unions"))], []⟩
#guard [n1, noTo join, form true].map (text []) == ["{0} form trade unions",
  "{0} join trade unions for the protection of their interests",
  "{0} to form trade unions for the protection of their interests"]                                        -- N1-N3
#guard [n1, noTo join, form true].all (fun a => normalOk V12 a && roundTrip V12 a)
#guard [noTo directly, noTo through].map (text fx11) ==
  ["{0} directly take part in {1}", "{0} take part in {1} through freely chosen representatives"]          -- N4, N5
#guard [noTo directly, noTo through].all (fun a => normalOk V11 a && roundTrip V11 a)

/-! ### `Atom.canon`: the object first, the adverbs before the prepositional modifiers -/

def Vk : Vocab := ⟨[fr "give" ["to", ""] [] ["at", "in", "on"], fr "deceive" ["", "about"] [] []], ["now", "then"]⟩
def give (args : List (String × Filler)) (mods : List Modifier) : Atom := ⟨true, false, ["give"], args, mods⟩
def help : Filler := .one (w "help")
def mixed : Atom := give [("to", .one (.slot 1)), ("", help)] [.prep "at" (.slot 2), .adv "now", .prep "in" (w "time")]
#guard mixed.canon ==
  give [("", help), ("to", .one (.slot 1))] [.adv "now", .prep "at" (.slot 2), .prep "in" (w "time")]
#guard text [] mixed == "{0} to now give help to {1} at {2} in time"
#guard normalOk Vk mixed && roundTrip Vk mixed && back Vk mixed != .ok (.one mixed)
-- already in order: `canon` keeps it; two adverbs and two modifiers keep their own order
def ordered : Atom := give [("", help), ("to", .one (.fixed 0))] [.adv "then", .adv "now", .prep "on" (.slot 1),
  .prep "at" (.slot 2)]
#guard ordered.canon == ordered && normalOk Vk ordered && roundTrip Vk ordered

/-! ### `normalOk`, each condition accepted and refused (`atomOk` holds on both sides) -/

def obj (fl : Filler) : Atom := give [("", fl), ("to", .one (.slot 1))] []
def atMod (p : Part) : Atom := give [("", help)] [.prep "at" p]
-- a words part: non-empty, of the frame's filler words (not a join or function word, an adverb, the first word of
-- one of its markers, or the first word of a head; in any case), in the object, a joined filler and a modifier
#guard [obj (.one (.words [])), atMod (.words [])].all (fun a => atomOk Vk a && !normalOk Vk a)
#guard [["help", "now"], ["on", "time"], ["help", "to"], ["deceive"], ["help", "and"], ["Then"]].all (fun ws =>
  atomOk Vk (obj (.one (.words ws))) && !normalOk Vk (obj (.one (.words ws))) && !normalOk Vk (atMod (.words ws)))
#guard [obj (.one (w "help about time")), atMod (w "about"), obj (.joined .or [.slot 2, w "about"])].all
  (fun a => normalOk Vk a && roundTrip Vk a)
#guard !normalOk Vk (obj (.joined .or [.slot 2, .words ["now"]]))
-- the subject slot, in an argument (FR3), a joined filler and a modifier (FR4); `{1}` is accepted at each
def seek (args : List (String × Filler)) (mods : List Modifier) : Atom := ⟨true, false, ["seek"], args, mods⟩
def fr3 : Atom := seek [("", .one (.slot 0))] []
def fr4 : Atom := seek [("", .one (w "asylum"))] [.prep "in" (.slot 0)]
#guard [fr3, fr4].all (fun a => atomOk V5 a && !normalOk V5 a && back V5 a == .none)                       -- FR3, FR4
#guard text [] fr3 == "{0} to seek {0}" && text [] fr4 == "{0} to seek asylum in {0}"
#guard [seek [("", .one (.slot 1))] [], seek [("", .one (w "asylum"))] [.prep "in" (.slot 1)]].all
  (fun a => normalOk V5 a && roundTrip V5 a)
#guard !normalOk Vk (obj (.joined .or [.slot 2, .slot 0])) && normalOk Vk (obj (.joined .or [.slot 2, .slot 3]))
-- a repeated argument marker (FR5); two distinct markers are accepted
def participate (args : List (String × Filler)) : Atom := ⟨true, false, ["participate"], args, []⟩
def fr5 : Atom := participate [("in", .one (.fixed 0)), ("in", .one (.fixed 1))]
#guard atomOk V8 fr5 && !normalOk V8 fr5                                                                   -- FR5
#guard normalOk V8 (participate [("in", .one (.fixed 0))]) && roundTrip V8 (participate [("in", .one (.fixed 0))])
#guard !normalOk Vk (give [("", help), ("to", .one (.slot 1)), ("to", .one (.slot 2))] []) &&
  roundTrip Vk (give [("", help), ("to", .one (.slot 1))] [])
-- a joined filler under a split marker, or as a split object; under a plain marker, or a plain object, accepted
def toBoth : Atom := ⟨false, true, ["subjected"], [("to", .joined .or [w "torture", .fixed 0])], []⟩
#guard atomOk V6 toBoth && !normalOk V6 toBoth && back V6 toBoth != .ok (.one toBoth)
def Vs : Vocab := frames [fr "seek" [""] [""] [], fr "keep" [""] [] []]
def joinedObj (h : String) : Atom := ⟨true, false, [h], [("", .joined .and [.slot 1, .slot 2])], []⟩
#guard atomOk Vs (joinedObj "seek") && !normalOk Vs (joinedObj "seek")
#guard normalOk Vs (joinedObj "keep") && roundTrip Vs (joinedObj "keep")
#guard normalOk Vk (obj (.joined .and [.slot 2, .fixed 0])) && roundTrip Vk (obj (.joined .and [.slot 2, .fixed 0]))
-- every argument and every modifier is checked, the refused one first or last
#guard [give [("", help), ("to", .one (.slot 0))] [], give [("", .one (.slot 0)), ("to", .one (.slot 1))] []].all
  (!normalOk Vk ·)
#guard [[.prep "at" (.slot 1), .prep "in" (.slot 0)], [.prep "in" (.slot 0), .prep "at" (.slot 1)],
  [.adv "now", .prep "in" (.slot 0)]].all (fun ms => !normalOk Vk (give [("", help)] ms))
#guard normalOk Vk (give [("", help)] [.adv "now", .prep "at" (.slot 1), .prep "in" (.slot 2)])
-- two split markers: a joined filler under either is refused, under the plain marker accepted
def V2s : Vocab := frames [fr "send" ["", "to", "by", "with"] ["to", "by"] []]
def send (m : String) : Atom := ⟨true, false, ["send"], [("", help), (m, .joined .or [.slot 1, .slot 2])], []⟩
#guard framesOk V2s && !normalOk V2s (send "to") && !normalOk V2s (send "by")
#guard normalOk V2s (send "with") && roundTrip V2s (send "with")
-- `atomOk` refused: an undeclared head, a missing object
#guard !normalOk Vk ⟨true, false, ["take"], [], []⟩ && !normalOk Vk (give [("to", .one (.slot 1))] [])

/-! ### A joined filler: two or more parts, and D9 (i) at its ends (C1 to C4)

C1 to C4 are the atoms that passed `normalOk` as spec 5.5 wrote it and do not read back (QUESTION-read_normal.md);
the DRI's decision of 2026-10-30 (ap-2bb) adds the two conditions that refuse them. Each fits its frame. -/

def Vo : Vocab := frames [fr "form" [""] [] []]
def c2 : Atom := ⟨false, false, ["form"], [("", .joined .and [w "trade unions", .slot 1])], []⟩
def heldBy1 (ps : List Part) : Atom := ⟨false, true, ["held"], [("by", .joined .or ps)], []⟩
#guard framesOk V7 && framesOk Vo
#guard text fx7 held == "{0} be held by secret vote or equivalent free voting procedures"
#guard atomOk V7 held && !normalOk V7 held && back V7 held == .none                                       -- C1 (G7)
#guard read V7 rawCap stepBudget (MeaningExamples.toks fx7
  "{0} be held by secret vote or by equivalent free voting procedures") == .ok g7    -- G7, the marker repeated
#guard text [] c2 == "{0} form trade unions and {1}" && atomOk Vo c2 && !normalOk Vo c2 && back Vo c2 == .none -- C2
#guard atomOk V7 (heldBy1 [.slot 1]) && !normalOk V7 (heldBy1 [.slot 1]) &&
  back V7 (heldBy1 [.slot 1]) == .ok (.one ⟨false, true, ["held"], [("by", .one (.slot 1))], []⟩)          -- C3
#guard atomOk V7 (heldBy1 []) && !normalOk V7 (heldBy1 []) && back V7 (heldBy1 []) == .none               -- C4
-- the last part long is refused too; two or three parts with one-word ends, a long middle part, are accepted
#guard !normalOk V7 (heldBy1 [.slot 1, w "secret vote"]) && back V7 (heldBy1 [.slot 1, w "secret vote"]) == .none
def held2 : List (List Part) := [[w "secret", .fixed 0], [.slot 1, w "secret"], [.slot 1, w "secret vote", .fixed 0]]
#guard held2.all (fun ps => normalOk V7 (heldBy1 ps) && roundTrip V7 (heldBy1 ps))
#guard [[w "help", w "advice"], [w "help", w "good advice", w "time"]].all (fun ps =>
  normalOk Vk (obj (.joined .and ps)) && roundTrip Vk (obj (.joined .and ps)))
-- a later argument's joined filler is checked too; `longEnd` on a one-part list and at each end
#guard !normalOk Vk (give [("", help), ("to", .joined .or [.slot 1])] []) &&
  normalOk Vk (give [("", help), ("to", .joined .or [.slot 1, .slot 2])] [])
#guard [[w "secret vote"], [w "secret vote", .slot 1], [.slot 1, w "secret vote"]].all longEnd &&
  ![[], [w "secret"], [.slot 1], [w "secret", w "free voting", .slot 1]].any longEnd
#guard !normalOk Vk (obj (.joined .and [w "help", w "good advice"])) &&
  !normalOk Vk (obj (.joined .and [.slot 2])) && !normalOk Vk (obj (.joined .and []))

/-! ### `read_normal` and `normal_derived` at each family (ap-2bc)

`read_normal` (deliverable (4) of ap-2bc): the normal form reads back as the canonical atom from some cap and budget
on; and its existence half, a derivation of the normal form that means the canonical atom. The `#guard`s above and
below check `framesOk` and `normalOk` by evaluation (`decide` cannot evaluate `String.toLower`); each `example`
applies the theorem under them, and the round-trip `#guard`s check the same atoms at the production limits. -/

-- `Vk` declares the reserved clause word *then* as an adverb, so it is not `framesOk` and its fixtures above are
-- outside the theorem; `Vk1` is `Vk` without it, and `mixed` (whose one adverb is *now*) reads back under it too
def Vk1 : Vocab := ⟨Vk.frames, ["now"]⟩
#guard [V6, V12, V11, Vk1, V5, V8, Vs, V2s, V7].all framesOk && !framesOk Vk
#guard normalOk Vk1 mixed && roundTrip Vk1 mixed && back Vk1 mixed != .ok (.one mixed)
example (hV : framesOk V6 = true) (h : normalOk V6 torture = true) :
    Derived V6 torture.normal (.one torture.canon) := NormalProofs.normal_derived V6 hV torture h            -- G6
example (hV : framesOk V12 = true) (h : normalOk V12 n1 = true) :
    Derived V12 n1.normal (.one n1.canon) := NormalProofs.normal_derived V12 hV n1 h                       -- N1-N3
example (hV : framesOk V11 = true) (h : normalOk V11 (noTo through) = true) :
    Derived V11 (noTo through).normal (.one (noTo through).canon) := NormalProofs.normal_derived V11 hV _ h -- N4, N5
example (hV : framesOk Vk1 = true) (h : normalOk Vk1 mixed = true) :
    Derived Vk1 mixed.normal (.one mixed.canon) := NormalProofs.normal_derived Vk1 hV mixed h              -- canon
example (hV : framesOk V7 = true) (h : normalOk V7 (heldBy1 [.slot 1, w "secret vote", .fixed 0]) = true) :
    Derived V7 (heldBy1 [.slot 1, w "secret vote", .fixed 0]).normal
      (.one (heldBy1 [.slot 1, w "secret vote", .fixed 0]).canon) :=
  NormalProofs.normal_derived V7 hV _ h                                                     -- a joined filler, D9 (i)

/-- `read_normal`'s conclusion for `a` under `V`. -/
def ReadsBack (V : Vocab) (a : Atom) : Prop :=
  ∃ N0 b0, ∀ N b, N0 ≤ N → b0 ≤ b → read V N b a.normal.toArray = .ok (.one a.canon)
example (hV : framesOk V6 = true) (h : normalOk V6 torture = true) : ReadsBack V6 torture := read_normal V6 hV _ h
example (hV : framesOk V6 = true) (h : normalOk V6 cruel = true) : ReadsBack V6 cruel := read_normal V6 hV _ h -- G6
example (hV : framesOk V12 = true) (h : normalOk V12 n1 = true) : ReadsBack V12 n1 := read_normal V12 hV _ h
example (hV : framesOk V12 = true) (h : normalOk V12 (form true) = true) : ReadsBack V12 (form true) :=
  read_normal V12 hV _ h                                                                                    -- N1-N3
example (hV : framesOk V11 = true) (h : normalOk V11 (noTo directly) = true) : ReadsBack V11 (noTo directly) :=
  read_normal V11 hV _ h                                                                                    -- N4, N5
example (hV : framesOk Vk1 = true) (h : normalOk Vk1 mixed = true) : ReadsBack Vk1 mixed := read_normal Vk1 hV _ h
example (hV : framesOk V5 = true) (h : normalOk V5 (seek [("", .one (.slot 1))] []) = true) :
    ReadsBack V5 (seek [("", .one (.slot 1))] []) := read_normal V5 hV _ h                                  -- FR3's pair
example (hV : framesOk V8 = true) (h : normalOk V8 (participate [("in", .one (.fixed 0))]) = true) :
    ReadsBack V8 (participate [("in", .one (.fixed 0))]) := read_normal V8 hV _ h                           -- FR5's pair
example (hV : framesOk Vs = true) (h : normalOk Vs (joinedObj "keep") = true) : ReadsBack Vs (joinedObj "keep") :=
  read_normal Vs hV _ h                                                                       -- a joined object
example (hV : framesOk V2s = true) (h : normalOk V2s (send "with") = true) : ReadsBack V2s (send "with") :=
  read_normal V2s hV _ h                                                       -- a joined filler beside split markers
example (hV : framesOk V7 = true) (h : normalOk V7 (heldBy1 [.slot 1, w "secret vote", .fixed 0]) = true) :
    ReadsBack V7 (heldBy1 [.slot 1, w "secret vote", .fixed 0]) := read_normal V7 hV _ h      -- a joined filler, D9 (i)
-- the hypotheses of the instances above, by evaluation
#guard [normalOk V6 torture, normalOk V6 cruel, normalOk V12 n1, normalOk V12 (form true), normalOk V11 (noTo directly),
  normalOk Vk1 mixed, normalOk V5 (seek [("", .one (.slot 1))] []), normalOk V8 (participate [("in", .one (.fixed 0))]),
  normalOk Vs (joinedObj "keep"), normalOk V2s (send "with"),
  normalOk V7 (heldBy1 [.slot 1, w "secret vote", .fixed 0])].all id

end VE.Acts.RenderExamples
