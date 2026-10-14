import VE.Readings.SupVerdictsSound
import VE.Readings.Examples

namespace VE.Readings.SupVerdictsExamples
open VE.Readings

def E : VE.Environment := ⟨[], fun _ => none, fun _ => none⟩
def cert : VE.Tableau.Certificate := ⟨"ve-tableau-checker@1", "", [], "", .close⟩
def proof : SupProof := ⟨E, [], [], .bottom, cert⟩
def labels : VE.Compose.Labelled := [("unused", .top), ("needed", .bottom)]

#guard proof.check labels.formulas
#guard !proof.check []
#guard usedLabels proof.check [] labels [] == ["needed"]
#guard proof.check (blank labels (usedLabels proof.check [] labels []))

def c : Choice := [("s", 0)]
def d : Choice := [("s", 1)]
#guard foldEntailment [(c, .free), (d, .free)] [(c, .proved), (d, .proved)] == .all
#guard foldEntailment [(c, .free), (d, .free)] [(c, .proved), (d, .refuted)] == .some
#guard foldEntailment [(c, .free), (d, .free)] [(c, .refuted), (d, .refuted)] == .none
#guard foldEntailment [(c, .free), (d, .unknown)] [(c, .proved), (d, .proved)] == .unknown
#guard foldEntailment [] [] == .unknown
#guard foldPremises [] == .unknown

open VE.Readings.Run

def g : SupScope := { info := ⟨[], .free, .unknown, .unknown, []⟩ }
def p : SupScope := { info := ⟨[("rs1", 0)], .free, .proved, .unknown, []⟩ }
def m : SupScope := { info := ⟨[("rs1", 1)], .free, .refuted, .unknown, []⟩ }
def budget : SupBudget := {}
#guard strOf ((supResult Examples.K1 [] false "query" [] none [g, p, m] [] budget [c, d]).getObjValD "verdict") == "SOME"
#guard strOf ((supResult Examples.K1 [] false "query" [] none [g, m, { m with info := { m.info with choice := [("rs1", 0)] } }]
    [] budget [c, d]).getObjValD "verdict") == "NONE"
#guard (supIndependent Examples.K1 [] ["unsaid:pair:x,y"]).length == Examples.K1.sets.length

end VE.Readings.SupVerdictsExamples
