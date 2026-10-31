import VE.Acts.MeaningExamples

/-! Fixtures of `phraseReadings` and the edge rule (docs/spec/act-phrases.md 7, 11.4; plan 2.4, AP-4, G5).

A5, A8 to A12 are the pilot's phrases (P5 to P12 of 11.4) under the modal their source rule uses, each with exactly the
readings the audit asks for; P12n and P9m the table's other cells on them; `phraseReadings_exact` by value on P11 in
both directions; the limits at both sides (N − 1 and N raw derivations on G5, 64 lists listed and more refused, an
exhausted step budget, a saturated raw cap); and the edge rule's kinds on the rule table.
-/

namespace VE.Acts.ReadingsExamples
open VE.Acts VE.Acts.Examples VE.Acts.RuleExamples VE.Acts.TableExamples VE.Acts.MeaningExamples

def pr (V : Vocab) (op : Op) (fx : List String) (s : String) (N := rawCap) (b := stepBudget) : Listing (List Simple) :=
  phraseReadings V op N b (toks fx s)
/-- The number of readings; `none` is the limit outcome. -/
def np (V : Vocab) (op : Op) (fx : List String) (s : String) (N := rawCap) : Option Nat :=
  match pr V op fx s N with | .ok Rs => some Rs.length | .limit => none

def g9s := "{0} be arbitrarily deprived of their nationality nor denied the right to change their nationality"
def fx9 : List String := ["the right to change their nationality"]
def g10s := "{0} to security in the event of unemployment, sickness, disability, widowhood, old age or other lack of " ++
  "livelihood in circumstances beyond their control"
def g11s := "{0} to take part in {1} directly or through freely chosen representatives"
def g12s := "{0} to form and to join trade unions for the protection of their interests"

/-! ### The pilot's phrases: exactly two readings each -/

def atoms (A : Act) : List Simple := match A with
  | .one a => [.atom a] | .all _ _ ps | .any _ _ ps => ps.map .atom
-- A5 (u051): `in other countries` on `enjoy`, or on both
#guard pr V5 .right fx5 g5 == .ok [atoms (.all false false [obj5 "seek" false, obj5 "enjoy" true]),
  atoms (.all false false [obj5 "seek" true, obj5 "enjoy" true])]
-- A8 (u105): *freely* on `participate`, or on all three; never on a middle item alone (the seeded bug's guard)
#guard pr V8 .right fx8 g8 == .ok [atoms (g8t [true, false, false]), atoms (g8t [true, true, true])]
-- A9 (u055): *must not*: `deprivation_only`, then `both_acts`
#guard pr V9 .mustNot fx9 g9s == .ok [atoms (g9 false), atoms (g9 true)]
#guard pr V9 .may fx9 g9s == .ok []                                                                      -- P9m: D-22
-- A10 (u092): the split's six causes, the modifier on the last or on all
#guard pr V10 .right ["other lack of livelihood"] g10s == .ok [atoms (g10 false), atoms (g10 true)]
-- A11 (u076): each way, or one act
#guard pr V11 .right fx11 g11s == .ok [atoms g11, [.whole g11]]
-- A12 (u087): *for the protection …* on `join`, or on both
#guard pr V12 .right [] g12s == .ok [atoms (g12 false), atoms (g12 true)]
#guard np V12 .mustNot [] g12s == some 4                                                                 -- P12n
#guard [np V5 .right fx5 g5, np V8 .right fx8 g8, np V9 .mustNot fx9 g9s,
  np V10 .right ["other lack of livelihood"] g10s, np V11 .right fx11 g11s, np V12 .right [] g12s] ==
  [some 2, some 2, some 2, some 2, some 2, some 2]

-- `phraseReadings_exact` both ways on P11: both readings are derived; "only through …" (one atom) is neither
#guard [atoms g11, [.whole g11]].all (fun R => (meanings V11 fx11 g11s).any (fun A => (table .right A).contains R))
#guard !(match pr V11 .right fx11 g11s with | .ok Rs => Rs.contains [.atom through] | .limit => true) &&
  !(meanings V11 fx11 g11s).any (fun A => (table .right A).contains [.atom through])

/-! ### Phrases with no edge modifier read as AP-2 read them, through the table -/

#guard pr V6 .must fx6 "{0} be subjected to torture or to cruel, inhuman or degrading treatment or punishment" ==
  .ok [] &&                                                                                              -- split *or*
  pr V7 .must fx7 "{0} be held by secret vote or by equivalent free voting procedures" == .ok [[.atom held]]
#guard pr V14 .mustNot ["its core identity or principles", "to be human",
  "genuinely deceptive tactics that could harm users", "health or safety", "Anthropic’s guidelines"]
  ("{0} abandon its core identity or principles, claim to be human, use genuinely deceptive tactics that could harm " ++
  "users, endanger health or safety, or act against Anthropic’s guidelines") == .ok [atoms g14v]          -- G14v

/-! ### The limits at both sides -/

-- G5 has 2 raw derivations: N = 3 lists both readings, N = 2 is saturated and refused (G5)
#guard np V5 .right fx5 g5 3 == some 2 && np V5 .right fx5 g5 2 == none
-- the step budget: none left is a refusal
#guard pr V5 .right fx5 g5 (b := 0) == .limit
-- the table's lists are charged: L5's 32 meanings give 64 under *must not* (listed), L6's 64 give 128 (refused);
-- under *has the right to* L6 gives 64 (listed); L7 is over the limit and L8 saturates the raw cap (256)
#guard [5, 6, 7, 8].map (fun k => np V5 .mustNot cities (ln k)) == [some 64, none, none, none]
#guard [6, 7, 8].map (fun k => np V5 .right cities (ln k)) == [some 64, none, none]
#guard rawOf V5 cities (ln 8) == some rawCap && pr V5 .right cities (ln 8) == .limit

/-! ### The edge rule's kinds on the table (2.4) -/

/-- Every left side the table gives an edge kind, each once. -/
def edgeSides (V : Vocab) : List (NT × Attach) :=
  firsts ((schema V).filterMap (fun r => (attachOf r.kind).map (r.lhs, ·)))
-- `first` only at `E1X`; `last` at the four trailing edges; `all` at all five; no other left side
#guard edgeSides V5 == [(.E1X, .first), (.E1X, .all), (.F 0 .TE, .last), (.F 0 .TE, .all), (.F 0 .RE, .last),
  (.F 0 .RE, .all), (.F 0 .REt, .last), (.F 0 .REt, .all), (.F 0 .PX, .last), (.F 0 .PX, .all), (.F 1 .TE, .last),
  (.F 1 .TE, .all), (.F 1 .RE, .last), (.F 1 .RE, .all), (.F 1 .REt, .last), (.F 1 .REt, .all), (.F 1 .PX, .last),
  (.F 1 .PX, .all)]

end VE.Acts.ReadingsExamples
