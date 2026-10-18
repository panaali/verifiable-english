import VE.Syntax

/-! The one wording of a conflict witness's kind: a declared pair (`r->m`) or a strict collision. The soft-norms
and rights runners and the readings route's superposed verdicts read it from here. -/
namespace VE.Norms

def witnessKind (t : String × List String × VE.Formula) : String :=
  if (t.1.splitOn "->").length > 1 then s!"pair conflict on {t.1}" else s!"strict collision on {t.1}"

end VE.Norms
