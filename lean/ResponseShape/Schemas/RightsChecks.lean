import ResponseShape.DefaultsExamples

/-! rights-cfr-2/3 (docs/rights/rights-cfr-2/REPORT.md): the `rights` mode's answers that carry the new report parts
(`Run.findingJson`, `Run.conflictAnswerOf`, `Run.situationTables`, `Run.exhibit`) on fixtures, exact; each is accepted
by `rights.json`, and each with a member added, dropped or retyped (`DefaultsExamples.variants`) is refused. -/
namespace ResponseShape.RightsChecks
open Lean VE.Rights.Run
open ResponseShape.DefaultsExamples (variants)

def parse (s : String) : Json := (Json.parse s).toOption.getD .null
def env : Json := parse "{\"language\":\"ve.core@0.2\",\"profiles\":[\"norms@0\",\"relational-fol@0\",\"rights@0\",\"soft-norms@0\"],\"spec_revision\":\"ve-v0.2-expand2-2026-09-25\",\"vocabulary\":{\"sorts\":{\"state\":{\"description\":\"state\"},\"person\":{\"description\":\"person\"}},\"predicates\":{\"arrest_permitted\":{\"arguments\":[\"state\",\"person\"],\"description\":\"permission\",\"regulated\":{\"role\":\"permission\",\"default\":\"allow\",\"act\":\"{0} arrest {1}\"}},\"arbitrary_arrest\":{\"arguments\":[\"state\",\"person\"],\"description\":\"base\"},\"journalist\":{\"arguments\":[\"person\"],\"description\":\"base\"},\"deprive_required\":{\"arguments\":[\"state\",\"person\"],\"description\":\"obligation\",\"regulated\":{\"role\":\"obligation\",\"default\":\"deny\",\"act\":\"{0} deprive {1} of life\",\"permission\":\"deprive_permitted\"}},\"deprive_permitted\":{\"arguments\":[\"state\",\"person\"],\"description\":\"permission\",\"regulated\":{\"role\":\"permission\",\"default\":\"allow\",\"act\":\"{0} deprive {1} of life\"}}},\"constants\":{},\"rights\":{\"holders\":[\"person\"],\"bearers\":[\"state\",\"person\"],\"protected\":[\"arbitrary_arrest\"]}}}"
/-- Two rights in units s2 and s3, the limitation in s4 and an uncited adopter exception in s5. -/
def spanned : Json := parse "[{\"source_units\":[\"s1\",\"s2\",\"s3\",\"s4\",\"s5\"]},{\"right\":{\"name\":\"r9\",\"holder\":\"person\",\"lines\":[{\"kind\":\"claim\",\"norm\":{\"name\":\"no-arbitrary-arrest\",\"sign\":false,\"guard\":[\"binary\",\"arbitrary_arrest\",[\"var\",1],[\"var\",0]],\"unless\":[],\"over\":[],\"predicate\":\"arrest_permitted\"}}]}},{\"right\":{\"name\":\"r3\",\"holder\":\"person\",\"lines\":[{\"kind\":\"claim\",\"norm\":{\"name\":\"no-deprivation\",\"sign\":false,\"guard\":[\"binary\",\"arbitrary_arrest\",[\"var\",1],[\"var\",0]],\"unless\":[],\"over\":[],\"predicate\":\"deprive_permitted\"}}]}},{\"limitation\":{\"name\":\"l29\",\"scope\":\"all\",\"kinds\":\"all\",\"decided_by\":\"unstated\",\"conditions\":[{\"name\":\"determined_by_law\",\"role\":\"necessary\",\"verbalisation\":\"the limitation is determined by law\"},{\"name\":\"solely_for_permitted_purpose\",\"role\":\"necessary\",\"verbalisation\":\"the limitation is solely for permitted purpose\"}],\"factors\":[]}},{\"norm\":{\"name\":\"rule-7\",\"sign\":true,\"guard\":[\"unary\",\"journalist\",[\"var\",0]],\"unless\":[],\"over\":[\"no-arbitrary-arrest\"],\"predicate\":\"arrest_permitted\"}}]"
/-- An unranked default pair (a weighing point) and limitation 29 with a sufficient condition. -/
def weighed : Json := parse "[{\"right\":{\"name\":\"r9\",\"holder\":\"person\",\"lines\":[{\"kind\":\"claim\",\"norm\":{\"name\":\"no-arbitrary-arrest\",\"sign\":false,\"guard\":[\"binary\",\"arbitrary_arrest\",[\"var\",1],[\"var\",0]],\"unless\":[],\"over\":[],\"mode\":\"default\",\"exception\":{\"decided_by\":\"assistant\",\"sufficient\":[],\"necessary\":[],\"factors\":[]},\"predicate\":\"arrest_permitted\"}}]}},{\"limitation\":{\"name\":\"l29\",\"scope\":\"all\",\"kinds\":\"all\",\"decided_by\":\"unstated\",\"conditions\":[{\"name\":\"determined_by_law\",\"role\":\"necessary\",\"verbalisation\":\"the limitation is determined by law\"},{\"name\":\"diplomatic_immunity\",\"role\":\"sufficient\",\"verbalisation\":\"the limitation is diplomatic immunity\"}],\"factors\":[]}},{\"norm\":{\"name\":\"may-arrest\",\"sign\":true,\"guard\":[\"binary\",\"rights__cond__2\",[\"var\",1],[\"var\",0]],\"unless\":[],\"over\":[],\"predicate\":\"arrest_permitted\"}},{\"norm\":{\"name\":\"may-detain\",\"sign\":true,\"guard\":[\"top\"],\"unless\":[],\"over\":[],\"mode\":\"default\",\"exception\":{\"decided_by\":\"assistant\",\"sufficient\":[],\"necessary\":[],\"factors\":[]},\"predicate\":\"arrest_permitted\"}}]"
def case (kind : String) (doc : Json) (extra : List (String × Json)) : Json :=
  Json.mkObj ([("id", .str "c"), ("kind", .str kind), ("environment", env), ("document", doc)] ++ extra)
def answer (j : Json) : Json := (runCase j).toOption.getD .null
def accepts (j a : Json) : Bool :=
  (ResponseShape.decide Schemas.files (.ref "rights.json#/row") { value := j } a).toOption.isSome
def refusesAll (j a : Json) (n : Nat) : Bool := (variants [] n a).all (!accepts j ·)

def located : List (String × Json) := [("located", toJson ["s2", "s3", "s4", "s5"])]
def elabCase : Json := case "rights-elaborate" spanned located
def scopeCase : Json := case "rights-scope" spanned (located ++ [("certificates", Json.mkObj [])])
def creq : Json := case "rights-conflict" weighed [("packages", Json.mkObj [])]
def situation : Json := parse "{\"complete\":true,\"domains\":{\"state\":[\"s\"],\"person\":[\"p\"]},\"constants\":{},\"relations\":{\"arbitrary_arrest\":[],\"journalist\":[],\"soft__excepted__no_arbitrary_arrest\":[],\"soft__excepted__may_detain\":[[\"s\",\"p\"]],\"rights__lim__1\":[],\"rights__cond__1\":[[\"s\",\"p\"]],\"rights__cond__2\":[]}}"
/-- A CONFLICT-FREE answer (every premise used), with the situation exhibited or not, and an UNKNOWN one. -/
def conflict (free : Bool) (shown : Bool) : Option Json := do
  let src ← (VE.Rights.Wire.decodeRightsSource env weighed).toOption
  let M ← (exhibit src (Json.mkObj (if shown then [("situation", situation)] else []))).toOption
  pure (conflictAnswerOf "c" src.D free (if free then none else some "missing certificate for arrest_permitted")
    (fun _ => true) M)

def elabA : Json := answer elabCase
def scopeA : Json := answer scopeCase

-- Each finding beside its text, with its line's span (rights.md 8).
#guard elabA.getObjValD "located_findings" == parse "[{\"code\":\"ProtectedInCone\",\"right\":\"r9\",\"rule\":\"no-arbitrary-arrest\",\"span\":\"s2\",\"text\":\"ProtectedInCone: arbitrary_arrest in rule no-arbitrary-arrest on right r9\"},{\"code\":\"ProtectedInCone\",\"right\":\"r3\",\"rule\":\"no-deprivation\",\"span\":\"s3\",\"text\":\"ProtectedInCone: arbitrary_arrest in rule no-deprivation on right r3\"}]"
#guard scopeA.getObjValD "located_findings" == parse "[{\"code\":\"UnlicensedLimitation\",\"right\":\"r9\",\"rule\":\"no-arbitrary-arrest\",\"span\":\"s2\",\"text\":\"UnlicensedLimitation: exception rule-7 of rule no-arbitrary-arrest on right r9\"}]" && scopeA.getObjValD "licensed" == .bool false
#guard accepts elabCase elabA && accepts scopeCase scopeA && refusesAll scopeCase scopeA 3 && refusesAll elabCase elabA 1

-- rights.md 7.3's CONFLICT-FREE answer, with and without a situation, and an UNKNOWN one.
#guard conflict true true == some (parse "{\"budget\":10000,\"conditional_on\":[\"soft:coherence:may-detain,no-arbitrary-arrest\",\"rights:limitation:l29:arrest_permitted:necessary:determined_by_law\",\"rights:limitation:l29:arrest_permitted:sufficient:diplomatic_immunity\"],\"id\":\"c\",\"situation\":[{\"predicate\":\"soft__excepted__no_arbitrary_arrest\",\"tuples\":[]},{\"predicate\":\"soft__excepted__may_detain\",\"tuples\":[[\"s\",\"p\"]]},{\"predicate\":\"rights__lim__1\",\"tuples\":[]},{\"predicate\":\"rights__cond__1\",\"tuples\":[[\"s\",\"p\"]]},{\"predicate\":\"rights__cond__2\",\"tuples\":[]}],\"situation_exhibited\":true,\"status\":\"ok\",\"status_text\":\"CONFLICT-FREE among rules on the same act, conditional on 1 coherence premises and 2 limitation premises (soft:coherence:may-detain,no-arbitrary-arrest, rights:limitation:l29:arrest_permitted:necessary:determined_by_law, rights:limitation:l29:arrest_permitted:sufficient:diplomatic_immunity); 1 weighing points open; situation exhibited: yes\",\"targets\":[\"arrest_permitted\",\"deprive_permitted\",\"deprive_required\",\"deprive_required->deprive_permitted\"],\"verdict\":\"CONFLICT-FREE\",\"weighing_points\":[\"soft:coherence:may-detain,no-arbitrary-arrest\"]}")
#guard conflict true false == some (parse "{\"budget\":10000,\"conditional_on\":[\"soft:coherence:may-detain,no-arbitrary-arrest\",\"rights:limitation:l29:arrest_permitted:necessary:determined_by_law\",\"rights:limitation:l29:arrest_permitted:sufficient:diplomatic_immunity\"],\"id\":\"c\",\"situation\":null,\"situation_exhibited\":false,\"status\":\"ok\",\"status_text\":\"CONFLICT-FREE among rules on the same act, conditional on 1 coherence premises and 2 limitation premises (soft:coherence:may-detain,no-arbitrary-arrest, rights:limitation:l29:arrest_permitted:necessary:determined_by_law, rights:limitation:l29:arrest_permitted:sufficient:diplomatic_immunity); 1 weighing points open; situation exhibited: UNKNOWN (budget 10000)\",\"targets\":[\"arrest_permitted\",\"deprive_permitted\",\"deprive_required\",\"deprive_required->deprive_permitted\"],\"verdict\":\"CONFLICT-FREE\",\"weighing_points\":[\"soft:coherence:may-detain,no-arbitrary-arrest\"]}")
#guard conflict false true == some (parse "{\"conditional_on\":[],\"detail\":\"missing certificate for arrest_permitted\",\"id\":\"c\",\"status\":\"ok\",\"status_text\":\"UNKNOWN: missing certificate for arrest_permitted, budget 10000\",\"targets\":[\"arrest_permitted\",\"deprive_permitted\",\"deprive_required\",\"deprive_required->deprive_permitted\"],\"verdict\":\"UNKNOWN\"}")
#guard [conflict true true, conflict true false, conflict false true].all
  fun a => a.any fun a => accepts creq a && refusesAll creq a 4
#guard match conflict true true, conflict true false, conflict false true with
  | some shown, some bare, some unknown =>
    ["weighing_points", "situation_exhibited", "budget", "situation"].all
      (fun k => !accepts creq (unknown.setObjVal! k (shown.getObjValD k))) &&
    !accepts creq (shown.setObjVal! "situation" .null) &&
    !accepts creq (bare.setObjVal! "situation" (shown.getObjValD "situation"))
  | _, _, _ => false

end ResponseShape.RightsChecks
