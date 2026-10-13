import VE.Readings.Verdicts
import VE.Readings.SupWire

/-! RD-7: dependency replay and set mentions belong to Lean. The generator may minimise a proposed trace;
only replay of that trace, including all conflict certificates, determines the conditions shown. -/
namespace VE.Readings
open VE.Norms (envAt size targets)
open VE.SoftNorms (soften)
open VE.Rights (correlate)

structure SupProof where
  E : VE.Environment
  pre : List VE.Formula
  post : List VE.Formula
  conclusion : VE.Formula
  cert : VE.Tableau.Certificate

def SupProof.check (p : SupProof) (middle : List VE.Formula) : Bool :=
  VE.Tableau.checkCertificate p.E (p.pre ++ middle ++ p.post) p.conclusion p.cert

def supProofs (D : Doc) (certs : List (Option VE.Tableau.Certificate))
    (proof : Option (List VE.Formula × VE.Formula × VE.Tableau.Certificate)) : List SupProof :=
  let X := correlate (sup D).1
  let base := envAt (soften X) 0
  let full := envAt (soften X) (size (soften X))
  ((targets (soften X)).zip certs).filterMap (fun (t, c) => c.map (fun cert =>
    SupProof.mk base (VE.SoftNorms.backgroundBase' X) [] (VE.Norms.targetConclusion t) cert)) ++
    (proof.toList.map (fun (Γ, φ, cert) => SupProof.mk full (VE.SoftNorms.background' X)
      (VE.Norms.elaborate (soften X).T ++ ((sup D).2 ++ Γ)) φ cert))

def traceUsed : VE.Tableau.Trace → List Nat
  | .close => []
  | .expand n _ children => n :: children.flatMap traceUsed

def supLiteral (f : VE.Formula) : Bool :=
  match (match f with | .not g => g | _ => f) with
  | .unary .. | .binary .. | .top | .bottom => true
  | _ => false

/-- Coherence leaves are reported in their producer's order, counting expanded and literal leaves. -/
def supCoherence (D : Doc) (ps : List SupProof) : List String :=
  let X := correlate (sup D).1
  ((VE.SoftNorms.collidingPairs X).map (fun (M, N) =>
    (VE.SoftNorms.Wire.cohLabel M N, VE.SoftNorms.cohPremise X M N))).filterMap (fun (l, f) =>
      if ps.any (fun p => (List.range p.pre.length).any (fun k => p.pre[k]? == some f &&
          ((traceUsed p.cert.trace).contains k || supLiteral f))) then some l else none)

def supReplayMiddle (D : Doc) (A : Choice) (ps : List SupProof) (middle : List VE.Formula) : Bool :=
  ps.all (fun p => p.check (middle.take (slotLabelled D).length ++ A.map (fun x => choiceAtom D x.1 x.2) ++
    middle.drop (slotLabelled D).length))

def supDependencies (D : Doc) (A : Choice) (Q : VE.Compose.Labelled)
    (certs : List (Option VE.Tableau.Certificate)) (proof : Option (List VE.Formula × VE.Formula × VE.Tableau.Certificate)) :
    List String := usedLabels (supReplayMiddle D A (supProofs D certs proof)) [] (slotLabelled D ++ Q) []

theorem greedy_replay_sound (check : List VE.Formula → Bool) (L : VE.Compose.Labelled)
    (h : check L.formulas = true) : check (blank L (usedLabels check [] L [])) = true := by
  unfold usedLabels
  simp only [List.nil_append, List.append_nil]
  suffices ∀ (ls keep : List String), check (blank L keep) = true →
      check (blank L (ls.foldl (fun keep l => if check (blank L (keep.erase l)) then keep.erase l else keep) keep)) = true from
    this _ _ (by rw [blank_all]; exact h)
  intro ls
  induction ls with
  | nil => exact fun _ h => h
  | cons l ls ih =>
    intro keep hk
    simp only [List.foldl_cons]
    apply ih
    split
    · assumption
    · exact hk

/-- All accepted traces still replay with exactly the displayed conditions; none is silently discarded. -/
theorem supDependencies_replay (D : Doc) (A : Choice) (Q : VE.Compose.Labelled)
    (certs : List (Option VE.Tableau.Certificate)) (proof : Option (List VE.Formula × VE.Formula × VE.Tableau.Certificate))
    (h : supReplayMiddle D A (supProofs D certs proof) (slotLabelled D ++ Q).formulas = true) :
    supReplayMiddle D A (supProofs D certs proof)
      (blank (slotLabelled D ++ Q) (supDependencies D A Q certs proof)) = true :=
  greedy_replay_sound _ _ h

def supMentions (D : Doc) (A : Choice) (Q : VE.Compose.Labelled) (labels : List String) : List String :=
  D.sets.filterMap (fun R =>
    if A.any (·.1 == R.id) || (slotLabelled D ++ Q).any (fun (l, f) => labels.contains l &&
      ((VE.Norms.preds f).any (fun p => (List.range (bitsOf R.candidates.length)).any (fun j =>
        p == bitName ((D.sets.findIdx? (·.id == R.id)).getD 0 + 1) j)))) then some R.id else none)

end VE.Readings
