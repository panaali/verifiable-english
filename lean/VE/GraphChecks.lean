import VE.ClaimGraph

namespace VE.GraphChecks
open Graph

/-- A deliberately small, executable certificate language for regression checks:
exact committed named inputs plus either truth introduction or premise reuse.
This is not a Python certificate decoder or Lean proof-artifact replay path. -/
structure TestCertificate where
  premises : List Claim
  conclusion : Claim

def valid (certificate : TestCertificate) (premises : List Claim) (conclusion : Claim) : Prop :=
  certificate.premises = premises ∧ certificate.conclusion = conclusion ∧
    (conclusion.formula = .top ∨ conclusion.formula ∈ premises.map Claim.formula)

instance (certificate : TestCertificate) (premises : List Claim) (conclusion : Claim) :
    Decidable (valid certificate premises conclusion) :=
  by
    letI : BEq Formula := instBEqOfDecidableEq
    unfold valid
    infer_instance

/-- The test-only evidence predicate actually meets the abstract soundness
contract, independently of the executable test outcomes. -/
theorem testCertificate_sound (E : Environment) : CertificateSound E valid := by
  intro certificate premises conclusion h S _ hp
  rcases h.2.2 with he | hm
  · simp [he, Formula.denote]
  · exact hp conclusion.formula hm

private def env : Environment := ⟨[], fun _ => none, fun _ => none⟩
private def claim (name : String) (a : Formula := .top) : Claim := ⟨name, a⟩
private def leaf (c : Claim) : Node TestCertificate := ⟨c, none⟩
private def step (c : Claim) (ps : List Claim) : Node TestCertificate :=
  ⟨c, some ⟨ps.map Claim.name, ⟨ps, c⟩⟩⟩

private def diamond : ClaimGraph TestCertificate := ⟨[
  leaf (claim "a"),
  step (claim "left") [claim "a"],
  step (claim "right") [claim "a"],
  step (claim "root") [claim "left", claim "right", claim "left"]], "root"⟩

#guard check env valid diamond == some ⟨claim "root", [claim "a", claim "a", claim "a"]⟩
-- An explicit root assumption remains an assumption, even when it is true.
#guard check env valid ⟨[leaf (claim "root")], "root"⟩ ==
  some ⟨claim "root", [claim "root"]⟩
-- A checked empty-premise deduction has no undischarged assumptions.
#guard check env valid ⟨[step (claim "root") []], "root"⟩ == some ⟨claim "root", []⟩
-- A proof of true is not accepted as evidence for false.
#guard (check env valid ⟨[step (claim "root" .bottom) []], "root"⟩).isNone
-- Reject duplicate aliases, absent root, dangling references and forward order.
#guard (check env valid ⟨[leaf (claim "a"), leaf (claim "a")], "a"⟩).isNone
#guard (check env valid ⟨[leaf (claim "a")], "missing"⟩).isNone
#guard (check env valid ⟨[step (claim "root") [claim "missing"]], "root"⟩).isNone
#guard (check env valid ⟨[step (claim "root") [claim "a"], leaf (claim "a")], "root"⟩).isNone
-- Reject self-support and multi-node cycles.
#guard (check env valid ⟨[step (claim "root") [claim "root"]], "root"⟩).isNone
#guard (check env valid ⟨[step (claim "a") [claim "b"], step (claim "b") [claim "a"]], "a"⟩).isNone
-- Ill-typed nodes are rejected, including unreachable submitted nodes.
#guard (check env valid ⟨[leaf (claim "bad" (.eq (.var 0) (.var 0))),
  step (claim "root") []], "root"⟩).isNone
-- Exact premise ASTs and conclusion identities are passed to certificate checking.
#guard (check env valid ⟨[leaf (claim "a" .bottom),
  step (claim "root") [claim "a"]], "root"⟩).isNone
#guard (check env valid ⟨[⟨claim "root", some ⟨[], ⟨[], claim "stale"⟩⟩⟩], "root"⟩).isNone
-- Exact ordered premise lists, including duplicates, bind the certificate.
#guard (check env valid ⟨[leaf (claim "a"), leaf (claim "b"),
  ⟨claim "root", some ⟨["b", "a"], ⟨[claim "a", claim "b"], claim "root"⟩⟩⟩], "root"⟩).isNone
#guard (check env valid ⟨[leaf (claim "a"),
  ⟨claim "root", some ⟨["a", "a"], ⟨[claim "a"], claim "root"⟩⟩⟩], "root"⟩).isNone

end VE.GraphChecks
