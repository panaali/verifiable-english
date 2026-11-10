import ResponseShape.DefaultsExamples

/-! rights-cfr-2/3 (docs/rights/rights-cfr-2/REPORT.md): the `rights` mode's answers that carry the new report parts
(`Run.findingJson`, `Run.conflictAnswerOf`, `Run.situationTables`, `Run.exhibit`) on fixtures, exact; each is accepted
by `rights.json`, and each with a member added, dropped or retyped (`DefaultsExamples.variants`) is refused. -/
namespace ResponseShape.RightsChecks
open Lean VE.Rights.Run
open ResponseShape.DefaultsExamples (variants)

def parse (s : String) : Json := (Json.parse s).toOption.getD .null
def env : Json := parse "{\"language\":\"ve.core@0.2\",\"profiles\":[\"norms@0\",\"relational-fol@0\",\"rights@0\",\"soft-norms@0\"],\"spec_revision\":\"ve-v0.2-expand2-2026-09-25\",\"vocabulary\":{\"sorts\":{\"state\":{\"description\":\"state\"},\"person\":{\"description\":\"person\"}},\"predicates\":{\"arrest_permitted\":{\"arguments\":[\"state\",\"person\"],\"description\":\"permission\",\"regulated\":{\"role\":\"permission\",\"default\":\"allow\",\"act\":\"{0} arrest {1}\"}},\"arbitrary_arrest\":{\"arguments\":[\"state\",\"person\"],\"description\":\"base\"},\"journalist\":{\"arguments\":[\"person\"],\"description\":\"base\"},\"deprive_required\":{\"arguments\":[\"state\",\"person\"],\"description\":\"obligation\",\"regulated\":{\"role\":\"obligation\",\"default\":\"deny\",\"act\":\"{0} deprive {1} of life\",\"permission\":\"deprive_permitted\"}},\"deprive_permitted\":{\"arguments\":[\"state\",\"person\"],\"description\":\"permission\",\"regulated\":{\"role\":\"permission\",\"default\":\"allow\",\"act\":\"{0} deprive {1} of life\"}}},\"constants\":{},\"rights\":{\"holders\":[\"person\"],\"bearers\":[\"state\",\"person\"],\"protected\":[\"arbitrary_arrest\"]}}}"
/-- Two rights in units s2 and t, the limitation in s4 and an uncited adopter exception of each in s5 and s6. -/
def spanned : Json := parse "[{\"source_units\":[\"s1\",\"s2\",\"t\",\"s4\",\"s5\",\"s6\"]},{\"right\":{\"name\":\"r9\",\"holder\":\"person\",\"lines\":[{\"kind\":\"claim\",\"norm\":{\"name\":\"no-arbitrary-arrest\",\"sign\":false,\"guard\":[\"binary\",\"arbitrary_arrest\",[\"var\",1],[\"var\",0]],\"unless\":[],\"over\":[],\"predicate\":\"arrest_permitted\"}}]}},{\"right\":{\"name\":\"r3\",\"holder\":\"person\",\"lines\":[{\"kind\":\"claim\",\"norm\":{\"name\":\"no-deprivation\",\"sign\":false,\"guard\":[\"binary\",\"arbitrary_arrest\",[\"var\",1],[\"var\",0]],\"unless\":[],\"over\":[],\"predicate\":\"deprive_permitted\"}}]}},{\"limitation\":{\"name\":\"l29\",\"scope\":\"all\",\"kinds\":\"all\",\"decided_by\":\"unstated\",\"conditions\":[{\"name\":\"determined_by_law\",\"role\":\"necessary\",\"verbalisation\":\"the limitation is determined by law\"},{\"name\":\"solely_for_permitted_purpose\",\"role\":\"necessary\",\"verbalisation\":\"the limitation is solely for permitted purpose\"}],\"factors\":[]}},{\"norm\":{\"name\":\"rule-7\",\"sign\":true,\"guard\":[\"unary\",\"journalist\",[\"var\",0]],\"unless\":[],\"over\":[\"no-arbitrary-arrest\"],\"predicate\":\"arrest_permitted\"}},{\"norm\":{\"name\":\"rule-8\",\"sign\":true,\"guard\":[\"top\"],\"unless\":[],\"over\":[\"no-deprivation\"],\"predicate\":\"deprive_permitted\"}}]"
/-- Two unranked default pairs (weighing points) and limitation 29 with a sufficient condition. -/
def weighed : Json := parse "[{\"right\":{\"name\":\"r9\",\"holder\":\"person\",\"lines\":[{\"kind\":\"claim\",\"norm\":{\"name\":\"no-arbitrary-arrest\",\"sign\":false,\"guard\":[\"binary\",\"arbitrary_arrest\",[\"var\",1],[\"var\",0]],\"unless\":[],\"over\":[],\"mode\":\"default\",\"exception\":{\"decided_by\":\"assistant\",\"sufficient\":[],\"necessary\":[],\"factors\":[]},\"predicate\":\"arrest_permitted\"}}]}},{\"limitation\":{\"name\":\"l29\",\"scope\":\"all\",\"kinds\":\"all\",\"decided_by\":\"unstated\",\"conditions\":[{\"name\":\"determined_by_law\",\"role\":\"necessary\",\"verbalisation\":\"the limitation is determined by law\"},{\"name\":\"diplomatic_immunity\",\"role\":\"sufficient\",\"verbalisation\":\"the limitation is diplomatic immunity\"}],\"factors\":[]}},{\"norm\":{\"name\":\"may-arrest\",\"sign\":true,\"guard\":[\"binary\",\"rights__cond__2\",[\"var\",1],[\"var\",0]],\"unless\":[],\"over\":[],\"predicate\":\"arrest_permitted\"}},{\"norm\":{\"name\":\"may-detain\",\"sign\":true,\"guard\":[\"top\"],\"unless\":[],\"over\":[],\"mode\":\"default\",\"exception\":{\"decided_by\":\"assistant\",\"sufficient\":[],\"necessary\":[],\"factors\":[]},\"predicate\":\"arrest_permitted\"}},{\"norm\":{\"name\":\"may-hold\",\"sign\":true,\"guard\":[\"top\"],\"unless\":[],\"over\":[],\"mode\":\"default\",\"exception\":{\"decided_by\":\"assistant\",\"sufficient\":[],\"necessary\":[],\"factors\":[]},\"predicate\":\"arrest_permitted\"}}]"
def case (kind : String) (doc : Json) (extra : List (String × Json)) : Json :=
  Json.mkObj ([("id", .str "c"), ("kind", .str kind), ("environment", env), ("document", doc)] ++ extra)
def answer (j : Json) : Json := (runCase j).toOption.getD .null
def accepts (j a : Json) : Bool :=
  (ResponseShape.decide Schemas.files (.ref "rights.json#/row") { value := j } a).toOption.isSome
def refusesAll (j a : Json) (n : Nat) : Bool := (variants [] n a).all (!accepts j ·)

def located : List (String × Json) := [("located", toJson ["s2", "t", "s4", "s5", "s6"])]
def elabCase : Json := case "rights-elaborate" spanned located
def scopeCase : Json := case "rights-scope" spanned (located ++ [("certificates", Json.mkObj [])])
def creq : Json := case "rights-conflict" weighed [("packages", Json.mkObj [])]
def situation : Json := parse "{\"complete\":true,\"domains\":{\"state\":[\"s\"],\"person\":[\"p\",\"q\"]},\"constants\":{},\"relations\":{\"arbitrary_arrest\":[],\"journalist\":[],\"soft__excepted__no_arbitrary_arrest\":[],\"soft__excepted__may_detain\":[[\"s\",\"p\"]],\"soft__excepted__may_hold\":[[\"s\",\"p\"],[\"s\",\"q\"]],\"rights__lim__1\":[],\"rights__cond__1\":[[\"s\",\"p\"],[\"s\",\"q\"]],\"rights__cond__2\":[]}}"
/-- A CONFLICT-FREE answer (every premise used), with the situation exhibited or not, and an UNKNOWN one. -/
def conflict (free : Bool) (shown : Bool) (uses : String → Bool := fun _ => true) : Option Json := do
  let src ← (VE.Rights.Wire.decodeRightsSource env weighed).toOption
  let M ← (exhibit src (Json.mkObj (if shown then [("situation", situation)] else []))).toOption
  pure (conflictAnswerOf "c" src.D free (if free then none else some "missing certificate for arrest_permitted")
    uses M)

def elabA : Json := answer elabCase
def scopeA : Json := answer scopeCase
def texts (a : Json) : Json := Json.arr ((a.getObjValD "located_findings").getArr?.toOption.getD #[] |>.map (·.getObjValD "text"))

-- Each finding beside its text, with its line's span (rights.md 8); without `located` the spans are null.
#guard elabA.getObjValD "located_findings" == parse "[{\"code\":\"ProtectedInCone\",\"right\":\"r9\",\"rule\":\"no-arbitrary-arrest\",\"span\":\"s2\",\"text\":\"ProtectedInCone: arbitrary_arrest in rule no-arbitrary-arrest on right r9\"},{\"code\":\"ProtectedInCone\",\"right\":\"r3\",\"rule\":\"no-deprivation\",\"span\":\"t\",\"text\":\"ProtectedInCone: arbitrary_arrest in rule no-deprivation on right r3\"}]"
#guard scopeA.getObjValD "located_findings" == parse "[{\"code\":\"UnlicensedLimitation\",\"right\":\"r9\",\"rule\":\"no-arbitrary-arrest\",\"span\":\"s2\",\"text\":\"UnlicensedLimitation: exception rule-7 of rule no-arbitrary-arrest on right r9\"},{\"code\":\"UnlicensedLimitation\",\"right\":\"r3\",\"rule\":\"no-deprivation\",\"span\":\"t\",\"text\":\"UnlicensedLimitation: exception rule-8 of rule no-deprivation on right r3\"}]" && scopeA.getObjValD "licensed" == .bool false
#guard elabA.getObjValD "findings" == texts elabA && scopeA.getObjValD "findings" == texts scopeA
#guard accepts elabCase elabA && accepts scopeCase scopeA && refusesAll scopeCase scopeA 3 && refusesAll elabCase elabA 1
#guard let plain := case "rights-elaborate" spanned []; accepts plain (answer plain)
#guard !accepts scopeCase (scopeA.setObjVal! "licensed" (.bool true))
-- One finding only (no rule-8): still not licensed.
def oneCase : Json := case "rights-scope" (Json.arr ((spanned.getArr?.toOption.getD #[]).extract 0 5))
  [("located", toJson ["s2", "t", "s4", "s5"])]
#guard (answer oneCase).getObjValD "licensed" == .bool false
-- A scope answer with no finding (no limitation in the document): `licensed`, and every variant refused.
#guard let none := case "rights-scope" (Json.arr ((spanned.getArr?.toOption.getD #[]).extract 0 3)) [];
  (answer none).getObjValD "licensed" == .bool true && refusesAll none (answer none) 2

-- rights.md 7.3's CONFLICT-FREE answer, with and without a situation, and an UNKNOWN one.
#guard conflict true true == some (parse "{\"budget\":10000,\"conditional_on\":[\"soft:coherence:may-detain,no-arbitrary-arrest\",\"soft:coherence:may-hold,no-arbitrary-arrest\",\"rights:limitation:l29:arrest_permitted:necessary:determined_by_law\",\"rights:limitation:l29:arrest_permitted:sufficient:diplomatic_immunity\"],\"id\":\"c\",\"situation\":[{\"predicate\":\"soft__excepted__no_arbitrary_arrest\",\"tuples\":[]},{\"predicate\":\"soft__excepted__may_detain\",\"tuples\":[[\"s\",\"p\"]]},{\"predicate\":\"soft__excepted__may_hold\",\"tuples\":[[\"s\",\"p\"],[\"s\",\"q\"]]},{\"predicate\":\"rights__lim__1\",\"tuples\":[]},{\"predicate\":\"rights__cond__1\",\"tuples\":[[\"s\",\"p\"],[\"s\",\"q\"]]},{\"predicate\":\"rights__cond__2\",\"tuples\":[]}],\"situation_exhibited\":true,\"status\":\"ok\",\"status_text\":\"CONFLICT-FREE among rules on the same act, conditional on 2 coherence premises and 2 limitation premises (soft:coherence:may-detain,no-arbitrary-arrest, soft:coherence:may-hold,no-arbitrary-arrest, rights:limitation:l29:arrest_permitted:necessary:determined_by_law, rights:limitation:l29:arrest_permitted:sufficient:diplomatic_immunity); 2 weighing points open; situation exhibited: yes\",\"targets\":[\"arrest_permitted\",\"deprive_permitted\",\"deprive_required\",\"deprive_required->deprive_permitted\"],\"verdict\":\"CONFLICT-FREE\",\"weighing_points\":[\"soft:coherence:may-detain,no-arbitrary-arrest\",\"soft:coherence:may-hold,no-arbitrary-arrest\"]}")
#guard conflict true false == some (parse "{\"budget\":10000,\"conditional_on\":[\"soft:coherence:may-detain,no-arbitrary-arrest\",\"soft:coherence:may-hold,no-arbitrary-arrest\",\"rights:limitation:l29:arrest_permitted:necessary:determined_by_law\",\"rights:limitation:l29:arrest_permitted:sufficient:diplomatic_immunity\"],\"id\":\"c\",\"situation\":null,\"situation_exhibited\":false,\"status\":\"ok\",\"status_text\":\"CONFLICT-FREE among rules on the same act, conditional on 2 coherence premises and 2 limitation premises (soft:coherence:may-detain,no-arbitrary-arrest, soft:coherence:may-hold,no-arbitrary-arrest, rights:limitation:l29:arrest_permitted:necessary:determined_by_law, rights:limitation:l29:arrest_permitted:sufficient:diplomatic_immunity); 2 weighing points open; situation exhibited: UNKNOWN (budget 10000)\",\"targets\":[\"arrest_permitted\",\"deprive_permitted\",\"deprive_required\",\"deprive_required->deprive_permitted\"],\"verdict\":\"CONFLICT-FREE\",\"weighing_points\":[\"soft:coherence:may-detain,no-arbitrary-arrest\",\"soft:coherence:may-hold,no-arbitrary-arrest\"]}")
#guard conflict false true == some (parse "{\"conditional_on\":[],\"detail\":\"missing certificate for arrest_permitted\",\"id\":\"c\",\"status\":\"ok\",\"status_text\":\"UNKNOWN: missing certificate for arrest_permitted, budget 10000\",\"targets\":[\"arrest_permitted\",\"deprive_permitted\",\"deprive_required\",\"deprive_required->deprive_permitted\"],\"verdict\":\"UNKNOWN\"}")
#guard (conflict true false (·.startsWith "rights:")).map (·.getObjValD "status_text") == some (.str "CONFLICT-FREE among rules on the same act, conditional on 0 coherence premises and 2 limitation premises (rights:limitation:l29:arrest_permitted:necessary:determined_by_law, rights:limitation:l29:arrest_permitted:sufficient:diplomatic_immunity); 2 weighing points open; situation exhibited: UNKNOWN (budget 10000)")
#guard ((conflict true false (·.startsWith "soft:")).map (·.getObjValD "status_text")).any
  (·.getStr?.toOption.any (·.startsWith "CONFLICT-FREE among rules on the same act, conditional on 2 coherence premises and 0"))
#guard [conflict true true, conflict true false, conflict false true].all
  fun a => a.any fun a => accepts creq a && refusesAll creq a 6
#guard match conflict true true, conflict true false, conflict false true with
  | some shown, some bare, some unknown =>
    ["weighing_points", "situation_exhibited", "budget", "situation"].all
      (fun k => !accepts creq (unknown.setObjVal! k (shown.getObjValD k))) &&
    !accepts creq (shown.setObjVal! "situation" .null) &&
    !accepts creq (bare.setObjVal! "situation" (shown.getObjValD "situation")) &&
    !accepts creq (shown.setObjVal! "detail" (.str "missing certificate for arrest_permitted")) &&
    !accepts creq (shown.setObjVal! "status_text" (unknown.getObjValD "status_text")) &&
    !accepts creq (unknown.setObjVal! "status_text" (shown.getObjValD "status_text")) &&
    !accepts creq (unknown.setObjVal! "detail" (.str "ghost")) &&
    !accepts creq (unknown.setObjVal! "conditional_on" (shown.getObjValD "conditional_on"))
  | _, _, _ => false

end ResponseShape.RightsChecks
