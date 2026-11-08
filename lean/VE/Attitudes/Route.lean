import VE.Attitudes.Frame
import VE.NormDefaults.Layered
import VE.Compose.Dispatch

/-! The route views of `attitudes@0` and its premise pack (docs/spec/attitudes.md section 2.9): the norm-defaults
view `toU`, `SettledAsX`, `UnsaidFree`, the `constraint` pack `attitudesPack` and the profile row `attitudesRow`,
defined here and registered by AT-3a. AT-2 adds its statements (spec 6.2) to this module; its `pointCheck`,
`OriginsExact`, `packEntry` and `furtherEntries` go to `lean/VE/NormDefaults/Packs.lean`. -/

namespace VE.Attitudes
universe u

open VE.Norms (Regulated Sat envAt)
open VE.NormDefaults (UDoc SettledAs UndecidedAt FillTables withFill BaseAdmissibleU fill unsaidName)
open VE.NormDefaults.Wire (BaseAdmissibleX UndecidedAtX)

/-- The norm-defaults view of an attitudes document. -/
def toU (A : AttDoc) (unspec : List String) : Option UDoc := (toNorms A).map (fun D => ⟨D, unspec⟩)

/-- SETTLED over the fillings that also satisfy `X` (the counterpart of `UndecidedAtX`). -/
def SettledAsX (U : UDoc) (X : List VE.Formula) (B : VE.Structure.{u}) (r : Regulated) (vs : List B.Carrier)
    (b : Bool) : Prop :=
  ∀ F : FillTables U B, BaseAdmissibleX U X (withFill U B F) →
    ((VE.Norms.outcomeBase (fill U) r.name).denote (withFill U B F) (VE.Norms.tupleVal vs) ↔ b = true)

/-- A premise that reads no `unsaid__` table of `U`. -/
def UnsaidFree (U : UDoc) (φ : VE.Formula) : Prop := ∀ p ∈ U.unspec, unsaidName p ∉ VE.Norms.preds φ

/-- AT-2's stand-in (spec section 0; reviews/dri-decisions-20261108-at-1c.md item 1): a frame label's request
    occurrence. AT-2 writes the body and AT-3a fixes the paths; until then every origin is the root, and no route
    registers the pack (Examples.lean's guard on `labelOriginStandInUnread`). -/
def labelOrigin (_A : AttDoc) (_l : String) : VE.NormDefaults.Packs.RequestPath := []

/-- The `attitudes` pack (edit 6), restated against PK-1 as built (refresh, RF-5): a `constraint` pack with no
    generated names; each key's name is declared once, by `envAtt A` (section 2.4). `labelOrigin` gives each frame
    label's full request occurrence; a key's origin (holder term, mode, content, slot, enclosing rule and guard
    location, A6; for a reading-set part's key, at-rev AT-R1, its set, reading and part: PC's `candidateAt` place) is
    `keyOrigin`, carried by `attitudes-elaborate`'s answer (section 4). AT-3a fixes the paths, PC-11 a part's. -/
def attitudesPack (A : AttDoc) : VE.NormDefaults.Packs.Pack :=
  { id := "attitudes", kind := .constraint, decls := [], consts := [],
    labelled := (frameLabels A).zip (framePremises A),
    origins := (frameLabels A).map (fun l => (l, labelOrigin A l)), conditions := [] }

/-- `attitudes@0`'s row in AR-10's table (edit 7), its admission aligned with `attitudes_row_composes` (refresh,
    RF-7), registered by AT-3a with the slot `pack` and the interface `.pack "attitudes"` (profile-composition PC-3;
    synthesis round 2). The refusal gives the reason text only; `gateOf` alone writes the `UnsupportedProfile:`
    prefix. -/
def attitudesRow : VE.Compose.ProfileRow :=
  { profile := "attitudes@0", requires := ["norm-defaults@0", "norms@0"],
    refuses := [("reports@0", "attitudes@0 with reports@0 is not admitted")],
    slot := "pack", interface := .pack "attitudes" }

end VE.Attitudes
