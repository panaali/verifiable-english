import VE.Discourse.Positions

/-! # Fixtures of 14.8 that need no composed admission (docs/spec/discourse.md 14.8)

Over 10's α: sorts `service`, `person`; `web_api : service`, `alice : person` (and `bob : person` for a plural); `review_required`, `deployed`, `api :
service`, `owns : person × service`, `notify_required : person`. Each content is the one the fence compiler yields
with its slots (14.3 step 2); the fence compiler and the steps around it (S4-5, S4-6, S4-8, S4-11's header option,
S4-12, S4-13, S4-19) are cmp-s4ab's. -/
namespace VE.Discourse.PositionsExamples
open VE.Discourse
open VE.Compose (Content)

def E : VE.Environment where
  sorts := ["service", "person"]
  predicates p := [("review_required", ["service"]), ("deployed", ["service"]), ("api", ["service"]),
    ("owns", ["person", "service"]), ("notify_required", ["person"])].lookup p
  constants c := [("web_api", "service"), ("alice", "person"), ("bob", "person")].lookup c  -- `bob`: the plural

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

/-! S4-9: `rule notify-owner: for every person x0, (x0 notify_required) if (she owns @web_api).`, `she` → `binder:0`. -/
#guard okIs (resolveContent E (manifest [mention "m1" .pronoun (binderTarget 0)]) "u1"
    (.norm (node "notify-owner" "notify_required" (.binary "owns" (slot "m1") (.const "web_api")))))
  (.norm (node "notify-owner" "notify_required" (.binary "owns" (.var 0) (.const "web_api"))))

/-! S4-10: an asserted fenced unit "It is deployed." with `It` → `binder:0`. -/
#guard errIs (resolveContent E (manifest [mention "m1" .pronoun (binderTarget 0)]) "u1"
  (.assertion (.unary "deployed" (slot "m1")))) "WitnessEscape: m1"

/-! S4-11, `resolve_identity`'s half: the rule target of "exception to the rule above" (`section_ref` → rule) is no
slot, so the node with `over = ["review-it"]` resolves to itself. -/
def m11 (r : String) := mention "m2" .sectionRef (namedTarget .rule r)
#guard formulaMentions (manifest [m11 "review-it"]) "u1" = []
#guard okIs (resolveContent E (manifest [m11 "review-it"]) "u1" (.norm (node "r2" "review_required" .top ["review-it"])))
  (.norm (node "r2" "review_required" .top ["review-it"]))

/-! S4-15: a fence unit with no mention: the content as compiled. -/
#guard okIs (resolveContent E (manifest []) "u1" s4_4) s4_4
#guard withPositions E s4_7 ((positions E s4_7).map (·.2)) == some s4_7

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

/-! Coverage (no 14.8 row): positions and their write-back over every content kind, each row of resolution step 3,
and the order of the slots. -/
def g (p : String) : VE.Formula := .unary p (.var 0)
def nodeX : VE.SoftNorms.SoftNode := { (node "r" "review_required" (g "api")) with
  carveOuts := [g "deployed", .bottom], mode := .default,
  exception := some ⟨none, [g "review_required", .top], [.top, g "api"], []⟩ }
#guard (positions E (.norm nodeX)).map (·.2) =
  [g "api", g "deployed", .bottom, g "review_required", .top, .top, g "api"]
#guard withPositions E (.norm nodeX) [.top, .bottom, .top, g "api", .bottom, g "deployed", .top] == some (.norm
  { nodeX with guard := .top, carveOuts := [.bottom, .top], exception := some ⟨none, [g "api", .bottom],
    [g "deployed", .top], []⟩ })
def lineX : VE.Rights.SourceLine :=
  ⟨.power, none, some (node "lib" "deployed" (g "api")), some (node "rec" "owns" .top), [], none, []⟩
def rightX : Content := .right ⟨"rt", "person", g "notify_required", [lineX, { lineX with liberty := none }]⟩
#guard positions E rightX = [(["person"], g "notify_required"), (["service"], g "api"), (["service", "person"], .top),
  (["service", "person"], .top)]
-- A claim line's norm node, then a power line's liberty and recognition nodes, each line in order.
def claimX : VE.Rights.SourceLine := ⟨.claim, some (node "cl" "notify_required" .bottom), none, none, [], none, []⟩
#guard positions E (.rightLines "rt" [claimX, lineX]) =
  [(["person"], .bottom), (["service"], g "api"), (["service", "person"], .top)]
#guard withPositions E (.rightLines "rt" [claimX, lineX]) [.top, .bottom, .top] == some (.rightLines "rt"
  [{ claimX with norm := some (node "cl" "notify_required" .top) },
   { lineX with liberty := some (node "lib" "deployed" .bottom) }])
#guard withPositions E rightX [.bottom, .top, g "deployed", .bottom] == some (.right ⟨"rt", "person", .bottom,
  [{ lineX with liberty := some (node "lib" "deployed" .top), recognition := some (node "rec" "owns" (g "deployed")) },
   { lineX with liberty := none, recognition := some (node "rec" "owns" .bottom) }]⟩)
#guard positions E (.rightLines "rt" [lineX]) = ((positions E rightX).drop 1).take 2
#guard positions E (.limitation ⟨"l", none, none, none, [], []⟩) = []
#guard slotName "m1" = "ve__slot__m1"

-- A predicate slot (`such`): the slot predicate symbol becomes the target's, in a unary and a binary atom.
#guard okIs (resolveContent E (manifest [mention "m1" .such (predTarget "deployed")]) "u1"
  (.assertion (.unary (slotName "m1") (.const "web_api")))) (.assertion (.unary "deployed" (.const "web_api")))
#guard okIs (resolveContent E (manifest [mention "m1" .such (predTarget "owns")]) "u1"
  (.assertion (.binary (slotName "m1") (.const "alice") (.const "web_api"))))
  (.assertion (.binary "owns" (.const "alice") (.const "web_api")))
-- A distributive plural: one conjunct per member.
#guard okIs (resolveContent E (manifest [mention "m1" .plural (listTarget ["alice", "bob"]) (rd := some .distributive)])
  "u1" (.assertion (.unary "notify_required" (slot "m1"))))
  (.assertion (.and (.unary "notify_required" (.const "alice")) (.unary "notify_required" (.const "bob"))))
-- `binder:<i>` over `owns`: the context is `[service, person]`, so `binder:0` is variable 1 and `binder:1` variable 0,
-- each lifted under the quantifiers of the position; `binder:2` escapes.
def mb (i : Nat) (id : String) (span : Nat × Nat) := mention id .pronoun (binderTarget i) (span := span)
#guard okIs (resolveContent E (manifest [mb 0 "m1" (0, 2), mb 1 "m2" (3, 5)]) "u1" (.norm (node "o" "owns"
    (.and (.binary "owns" (slot "m1") (slot "m2")) (.ex "service" (.binary "owns" (slot "m1") (.var 0)))))))
  (.norm (node "o" "owns" (.and (.binary "owns" (.var 1) (.var 0)) (.ex "service" (.binary "owns" (.var 2) (.var 0))))))
#guard errIs (resolveContent E (manifest [mb 2 "m1" (0, 2)]) "u1"
  (.norm (node "o" "owns" (.binary "owns" (slot "m1") (.var 0))))) "WitnessEscape: m1"
#guard errIs (resolveContent E (manifest [mb 10 "m1" (0, 2)]) "u1"
  (.norm (node "o" "owns" (.binary "owns" (slot "m1") (.var 0))))) "WitnessEscape: m1"
-- Two descriptions in one position: the one written first (`m1`, a person) takes the wider scope, whatever the
-- manifest order.
def dPerson := mention "m1" .definite (binderTarget 0) (some (g "notify_required")) (some .assertive)
def dService := mention "m2" .definite (binderTarget 0) (some (g "api")) (some .assertive) (span := (3, 5))
def twoDescriptions : VE.Formula :=
  assertive "person" (g "notify_required") (assertive "service" (g "api") (.binary "owns" (.var 1) (.var 0)))
#guard okIs (resolveContent E (manifest [dService, dPerson]) "u1" (.assertion (.binary "owns" (slot "m1") (slot "m2"))))
  (.assertion twoDescriptions)
#guard okIs (resolveContent E (manifest [dPerson, dService]) "u1" (.assertion (.binary "owns" (slot "m1") (slot "m2"))))
  (.assertion twoDescriptions)
-- A mention nested in a description's span (its possessive) is no separate slot; one outside the span needs one.
#guard okIs (resolveContent E (manifest [m7, mention "m3" .possessive (entityTarget "alice") (span := (0, 1))]) "u1" s4_7)
  (.norm (node "notify" "notify_required" (assertive "service" (g "api") (.binary "owns" (.var 1) (.var 0)))))
#guard errIs (resolveContent E (manifest [m7, mention "m3" .possessive (entityTarget "alice") (span := (3, 4))]) "u1" s4_7)
  "MentionNotSlot: m3"
-- Step 4's position without a slot, and step 3's other kinds.
#guard errIs (resolveContent E k4 "u1" (.norm { (node "review-it" "review_required" (.eq (.var 0) (slot "m1"))) with
  carveOuts := [.unary "owns" (.var 0)] })) "InvalidInput: u1: position 1"
#guard errIs (resolveContent E (manifest [mention "m1" .pronoun (namedTarget .rule "review-it")]) "u1"
  (.assertion (.unary "deployed" (slot "m1")))) "TargetKindMismatch: m1: pronoun, rule"
#guard errIs (resolveContent E (manifest [mention "m1" .demonstrative (namedTarget .claim "c1")]) "u1"
  (.assertion (.unary "deployed" (slot "m1")))) "UnsupportedTarget: m1: claim"
#guard errIs (resolveContent E (manifest [{ m7 with reading := none }]) "u1" s4_7) "IllTypedTarget: m1: binder:0"

end VE.Discourse.PositionsExamples
