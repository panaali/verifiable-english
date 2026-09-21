import VE.ClaimGraph

namespace VE.TableauChecks
open Graph Tableau

private def env : Environment := ⟨[], fun _ => none, fun _ => none⟩
private def cert : Certificate := ⟨"ve-tableau-checker@1", "", [], "", .close⟩
private def leaf (name : String) : Node Certificate := ⟨⟨name, .top⟩, none⟩
private def step (name : String) (ps : List String) (f : Formula := .top) : Node Certificate :=
  ⟨⟨name, f⟩, some ⟨ps, cert⟩⟩
private def diamond : ClaimGraph Certificate := ⟨[
  leaf "a", step "left" ["a"], step "right" ["a"],
  step "root" ["left", "right", "left"]], "root"⟩

#guard checkTableau env diamond == some ⟨⟨"root", .top⟩,
  [⟨"a", .top⟩, ⟨"a", .top⟩, ⟨"a", .top⟩]⟩
#guard checkTableau env ⟨[step "root" []], "root"⟩ == some ⟨⟨"root", .top⟩, []⟩
#guard (checkTableau env ⟨[step "root" [] .bottom], "root"⟩).isNone
#guard (checkTableau env ⟨[step "root" ["missing"]], "root"⟩).isNone
#guard (checkTableau env ⟨[step "root" ["root"]], "root"⟩).isNone
#guard (checkTableau env ⟨[step "root" ["a"], leaf "a"], "root"⟩).isNone
#guard (checkTableau env ⟨[leaf "a", leaf "a"], "a"⟩).isNone
#guard (checkTableau env ⟨[leaf "a", step "bad" [] .bottom, step "root" []], "root"⟩).isNone

end VE.TableauChecks
