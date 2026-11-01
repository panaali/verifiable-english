import VE.Discourse.Positions

/-! # Fixtures of 14.8 that need no composed admission (docs/spec/discourse.md 14.8)

Over 10's α: sorts `service`, `person`; `web_api : service`, `alice : person`; `review_required`, `deployed`, `api :
service`, `owns : person × service`, `notify_required : person`. Each content is the one the fence compiler yields
with its slots (14.3 step 2); the fence compiler itself is cmp-s4's. -/
namespace VE.Discourse.PositionsExamples
open VE.Discourse
open VE.Compose (Content)

def E : VE.Environment where
  sorts := ["service", "person"]
  predicates p := [("review_required", ["service"]), ("deployed", ["service"]), ("api", ["service"]),
    ("owns", ["person", "service"]), ("notify_required", ["person"])].lookup p
  constants c := [("web_api", "service"), ("alice", "person")].lookup c

def manifest (ms : List Mention) : Manifest :=
  ⟨"", "", [], [], [], ms, [], [], [], [], [], [], []⟩

def mention (id : String) (form : Form) (t : Target) (r : Option VE.Formula := none) (rd : Option Reading := none)
    (span : Nat × Nat := (0, 2)) : Mention :=
  ⟨id, "u1", span, form, t, r, rd, none, none, span⟩

def node (name pred : String) (guard : VE.Formula) (over : List String := []) : VE.SoftNorms.SoftNode :=
  { name, pred, sign := true, guard, carveOuts := [], over, mode := .strict, rank := none, alterable := [],
    exception := none, hard := false }

def slot (m : String) : VE.Term := .const (slotName m)
def okIs {α} [BEq α] (r : Except String α) (a : α) : Bool := match r with | .ok b => b == a | .error _ => false
def errIs {α} (r : Except String α) (e : String) : Bool := match r with | .error e' => e' == e | .ok _ => false

/-! S4-4: `rule review-it: for every service x0, (x0 review_required) if (x0 equals it).`, `it` → `web_api`. -/
def s4_4 : Content := .norm (node "review-it" "review_required" (.eq (.var 0) (slot "m1")))
def k4 : Manifest := manifest [mention "m1" .pronoun (entityTarget "web_api")]
def written4 : Content := .norm (node "review-it" "review_required" (.eq (.var 0) (.const "web_api")))
#guard okIs (resolveContent E k4 "u1" s4_4) written4
#guard positions E s4_4 = [(["service"], .eq (.var 0) (slot "m1"))]
#guard withPositions E written4 ((positions E s4_4).map (·.2)) == some s4_4
#guard withPositions E s4_4 [.top, .top] == none

/-! S4-5: english fence "It must be reviewed.", the header slot: binder `x0`, guard conjunct `x0 equals @web_api`. -/
def header5 := headerSlot E (mention "m1" .pronoun (entityTarget "web_api")) 0 (node "review-it" "review_required" .top)
#guard okIs header5 (node "review-it" "review_required" (.eq (.var 0) (slot "m1")))
#guard match header5 with
  | .ok N => okIs (resolveContent E k4 "u1" (.norm N)) written4
  | .error _ => false
#guard okIs (headerSlot E (mention "m1" .pronoun (entityTarget "web_api")) 0
    (node "r" "review_required" (.unary "deployed" (.var 0))))
  (node "r" "review_required" (.and (.unary "deployed" (.var 0)) (.eq (.var 0) (slot "m1"))))

/-! S4-6: S4-5 with `It` → `binder:0`. -/
#guard errIs (headerSlot E (mention "m1" .pronoun (binderTarget 0)) 0 (node "review-it" "review_required" .top))
  "UnsupportedTarget: m1: rule header"

/-! S4-7: `rule notify: for every person x0, (x0 notify_required) if (x0 owns the API).`, a definite, assertive. -/
def m7 := mention "m1" .definite (binderTarget 0) (some (.unary "api" (.var 0))) (some .assertive)
def s4_7 : Content := .norm (node "notify" "notify_required" (.binary "owns" (.var 0) (slot "m1")))
#guard okIs (resolveContent E (manifest [m7]) "u1" s4_7) (.norm (node "notify" "notify_required"
  (.ex "service" (.and (.unary "api" (.var 0)) (.and (.all "service" (.implies (.unary "api" (.var 0))
    (.eq (.var 0) (.var 1)))) (.binary "owns" (.var 1) (.var 0)))))))
-- the presuppositional reading
#guard okIs (resolveContent E (manifest [{ m7 with reading := some .presuppositional }]) "u1" s4_7)
  (.norm (node "notify" "notify_required"
    (.all "service" (.implies (.unary "api" (.var 0)) (.binary "owns" (.var 1) (.var 0))))))

/-! S4-8: S4-7 with a second accessible description of the same sort that also type-checks. -/
def m8 := { m7 with restriction := some (.unary "deployed" (.var 0)) }
#guard errIs (uniqueTarget E (manifest [m7]) "u1" s4_7 m7 [m7, m8]) "AmbiguousReference: m1: the api, the deployed"
#guard okIs (uniqueTarget E (manifest [m7]) "u1" s4_7 m7 [m7]) ()
-- a second description that does not type-check (a `person` restriction where a `service` stands) is no competitor
#guard okIs (uniqueTarget E (manifest [m7]) "u1" s4_7 m7
  [m7, { m7 with restriction := some (.unary "notify_required" (.var 0)) }]) ()

/-! S4-9: `rule notify-owner: for every person x0, (x0 notify_required) if (she owns @web_api).`, `she` → `binder:0`. -/
#guard okIs (resolveContent E (manifest [mention "m1" .pronoun (binderTarget 0)]) "u1"
    (.norm (node "notify-owner" "notify_required" (.binary "owns" (slot "m1") (.const "web_api")))))
  (.norm (node "notify-owner" "notify_required" (.binary "owns" (.var 0) (.const "web_api"))))

/-! S4-10: an asserted fenced unit "It is deployed." with `It` → `binder:0`. -/
#guard errIs (resolveContent E (manifest [mention "m1" .pronoun (binderTarget 0)]) "u1"
  (.assertion (.unary "deployed" (slot "m1")))) "WitnessEscape: m1"

/-! S4-11: a header option "exception to the rule above" (`section_ref` → rule, no slot). -/
def m11 (r : String) := mention "m2" .sectionRef (namedTarget .rule r)
#guard okIs (headerOver ["review-it"] (m11 "review-it") (node "r2" "review_required" .top))
  (node "r2" "review_required" .top ["review-it"])
#guard errIs (headerOver ["review-it"] (m11 "missing-rule") (node "r2" "review_required" .top))
  "UnknownRule: missing-rule"
#guard formulaMentions (manifest [m11 "review-it"]) "u1" = []
#guard okIs (resolveContent E (manifest [m11 "review-it"]) "u1" (.norm (node "r2" "review_required" .top ["review-it"])))
  (.norm (node "r2" "review_required" .top ["review-it"]))

/-! S4-12: a mention inside a soft `rank` field. -/
#guard errIs (softFields k4 "u1" [(0, 6)]) "UnsupportedTarget: m1: soft"
#guard okIs (softFields k4 "u1" [(3, 6)]) ()

/-! S4-13: a JSON norm unit with a recorded `it` mention in its prose; without the mention, the unrecorded surface. -/
#guard errIs (jsonContent k4 "u1" ["[4, 6)"]) "MentionNotSlot: m1"
#guard errIs (jsonContent (manifest []) "u1" ["[4, 6)"]) "UnrecordedSlot: u1: [4, 6)"

/-! S4-15: a fence unit with no mention: the content as compiled. -/
#guard okIs (resolveContent E (manifest []) "u1" s4_4) s4_4
#guard withPositions E s4_7 ((positions E s4_7).map (·.2)) == some s4_7

/-! S4-19: an environment declaring the constant `ve__slot__x`. -/
#guard errIs (reservedNames (Lean.Json.mkObj [("vocabulary", Lean.Json.mkObj [("sorts", Lean.Json.mkObj []),
  ("predicates", Lean.Json.mkObj []), ("constants", Lean.Json.mkObj [("ve__slot__x", .null)])])]))
  "InvalidInput: reserved name ve__slot__x"
#guard okIs (reservedNames (Lean.Json.mkObj [("vocabulary", Lean.Json.mkObj [("constants",
  Lean.Json.mkObj [("web_api", .null)])])])) ()

/-! S4-24: S4-10 with `It` → `web_api`. -/
#guard okIs (resolveFormula E k4 "u1" (.unary "deployed" (slot "m1"))) (.unary "deployed" (.const "web_api"))
#guard okIs (resolveContent E k4 "u1" (.assertion (.unary "deployed" (slot "m1"))))
  (.assertion (.unary "deployed" (.const "web_api")))

/-! S4-26: a fence mention whose target is a document name. -/
#guard errIs (resolveContent E (manifest [mention "m1" .documentName (namedTarget .document "constitution")]) "u1"
  (.assertion (.unary "deployed" (slot "m1")))) "UnsupportedTarget: m1: document"

/-! Resolution steps 2 and 4: a mention without a slot, a slot without a mention, an ill-typed target. -/
#guard errIs (resolveContent E k4 "u1" (.assertion (.unary "deployed" (.const "web_api")))) "MentionNotSlot: m1"
#guard errIs (resolveContent E k4 "u1" (.assertion (.and (.unary "deployed" (slot "m1")) (.unary "api" (slot "m9")))))
  "MentionNotSlot: m9"
#guard errIs (resolveContent E (manifest [mention "m1" .pronoun (entityTarget "alice")]) "u1" s4_4)
  "IllTypedTarget: m1: alice"

end VE.Discourse.PositionsExamples
