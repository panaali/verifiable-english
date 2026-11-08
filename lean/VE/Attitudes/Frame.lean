import VE.Attitudes.Syntax

/-! The frame of `attitudes@0` (docs/spec/attitudes.md section 2.7, D-A4, read from the table): for keys on the same
subject, factivity for each `knows` key, `knows → believes`, `knows → thinks w` and `thinks w → thinks w2`, and
nothing else; with one distinct label per premise for the `attitudes` pack (2.9). -/

namespace VE.Attitudes
open VE.Reports (Act)

def entailsMode (A : AttDoc) : Mode → Mode → Bool
  | .knows, .act .believes => A.T.knowsBelieves.isSome
  | .knows, .thinks w => A.T.knowsThinks.any (fun p => A.scale.atLeast p.1 w)
  | .thinks w, .thinks w2 => w != w2 && A.scale.atLeast w w2
  | _, _ => false

def sameSubject (k k2 : Key) : Bool :=
  k.holderSort == k2.holderSort && k.slotSort == k2.slotSort && k.content == k2.content

def framePairs (A : AttDoc) : List (Key × Key) :=
  (keys A).flatMap (fun k =>
    ((keys A).filter (fun k2 => sameSubject k k2 && entailsMode A k.mode k2.mode)).map (k, ·))

/-- `∀h. body` or `∀h ∀x. body`: the slot is variable 0, the holder variable 1 (or 0 when closed). -/
def closeOver (k : Key) (body : VE.Formula) : VE.Formula :=
  match k.slotSort with
  | none => .all k.holderSort body
  | some s => .all k.holderSort (.all s body)

def atomAt (A : AttDoc) (k : Key) : VE.Formula :=
  match k.slotSort with
  | none => .unary (name A k) (.var 0)
  | some _ => .binary (name A k) (.var 1) (.var 0)

def knowsKeys (A : AttDoc) : List Key := (keys A).filter (·.mode == .knows)

def factive (A : AttDoc) (k : Key) : VE.Formula := closeOver k (.implies (atomAt A k) k.content)

def entails (A : AttDoc) (p : Key × Key) : VE.Formula :=
  closeOver p.1 (.implies (atomAt A p.1) (atomAt A p.2))

def framePremises (A : AttDoc) : List VE.Formula :=
  (knowsKeys A).map (factive A) ++ (framePairs A).map (entails A)

/-- One label per premise, distinct (PK-1 requires distinct labels). -/
def frameLabels (A : AttDoc) : List String :=
  (knowsKeys A).map (fun k => "attitude:factive:" ++ name A k) ++
    (framePairs A).map (fun p => "attitude:entails:" ++ name A p.1 ++ ":" ++ name A p.2)

end VE.Attitudes
