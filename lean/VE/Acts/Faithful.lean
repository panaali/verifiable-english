import VE.Acts.Elaborate

/-! Faithfulness of the elaboration (docs/spec/act-phrases.md 6.6, C17): each part means what the source rules mean,
read of the part. `IntendedActs` is stated over the source tree and the structure read through `readAs`, not over the
elaborated tree. -/

namespace VE.Acts
open VE.Norms VE.NormDefaults
universe u

/-- `S` with `p` read as `q`. -/
def readAs (p q : String) (S : VE.Structure.{u}) : VE.Structure.{u} :=
  { S with relation := fun r vs => if r = p then S.relation q vs else S.relation r vs }

/-- The source's meaning per the table: part i of `p` means what the source rules on `p` mean, read of `p__i`. -/
def IntendedActs (D : ActsDoc) (S : VE.Structure.{u}) : Prop :=
  ∀ r ∈ D.U.D.T.regulated, ∀ q ∈ partNames D r.name, VE.Norms.IntendedAt D.U.D.T r (readAs r.name q S)

end VE.Acts
