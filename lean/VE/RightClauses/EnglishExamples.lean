import VE.RightClauses.English
import VE.RightClauses.Examples

/-! RC1 to RC4 through W7 (docs/spec/right-clauses.md 2, 9.3's English line; cmp-s3-cfr-1d): one instance each, RC3
also with `s_a = s_b` and slot o before the holder slot, RC4's two forms and its byte form for each trigger, and
G6 and G9 over every rendered sentence (composition.md 10.4, 13.20: quoted source text included). Each `#guard`
pins the exact bytes `english` returns; the build fails if one is false. Environment: `VE.RightClauses.Examples`'
(`r21`, holder person, the claim `equal-access` on `public_service_access_required(state, person)`, act `{0} grant {1}
access`), with the base predicates `adult(person)` and `lives_in(person, state)`. -/
namespace VE.RightClauses.EnglishExamples
open VE.RightClauses VE.RightClauses.English
open VE.RightClauses.Examples (r21Doc cline charged rel trig)
open VE.Rights.Examples (mkRights block strictNode line)

def lexicon : VE.EnglishGrammar.Lexicon :=
  { nouns := [("person", "person"), ("state", "state")], letters := [("person", "P"), ("state", "S")],
    wordings := [("adult", "{0} is adult"), ("charged", "{0} is charged"), ("country_of", "{0} is the country of {1}"),
      ("lives_in", "{0} lives in {1}"), ("parent_of", "{0} is a parent of {1}"), ("odd", "{0} is such that {1} odd"),
      ("forbidden", "{0} may not see {1}")],
    negatives := [], aliases := [], spellings := [] }

def source : String :=
  "Everyone has equal access to public service. This may not be denied. Officials said \"yes\" to it. " ++
  "Form rd-2 applies. Café rules."

def base : List (String × List String) :=
  [("adult", ["person"]), ("lives_in", ["person", "state"]), ("odd", ["state", "person"]),
   ("forbidden", ["state", "person"])]
def adult (i : Nat) : VE.Formula := .unary "adult" (.var i)

def doc (L : CLine) (D : VE.Rights.RightsDoc := r21Doc (base := base)) : ClauseDoc :=
  ⟨D, [("r21", "equal-access", L)], []⟩

/-- The shown rows as (frame, text), or the refusal as `("error", text)`. -/
def shownText (D : ClauseDoc) : List (String × String) :=
  match english D lexicon source with
  | .ok rows => rows.map fun r => (r.frame, r.text)
  | .error e => [("error", e)]

/-! ## RC1 and RC2: relation first, then the guard, then the clauses in wire order -/

def rc1Line : CLine := cline [trig (charged 0) 10 20] (some (rel (0, 1))) [(0, 8)] (adult 0)

#guard shownText (doc rc1Line) ==
  [("RC1", "Claim of right 1. Every state must grant each person access, where that state is the country of that " ++
     "person, if that person is adult and that person is charged."),
   ("RC4", "This line leaves out: \"Everyone\".")]

-- RC2 in the predicate's argument order: `lives_in(person, state)` on slots (1, 0).
#guard shownText (doc (cline [] (some (rel (1, 0) (pred := "lives_in"))) [])) ==
  [("RC1", "Claim of right 1. Every state must grant each person access, where that person lives in that state."),
   ("RC4", "This line leaves out nothing.")]

/-! ## RC3: the holder first -/

#guard shownText (doc (cline [] (some (rel (0, 1) (some 1))) [])) ==
  [("RC1", "Claim of right 1. Every state must grant each person access, where that state is the country of that " ++
     "person."),
   ("RC3", "For every person there is at least one state such that that state is the country of that person."),
   ("RC4", "This line leaves out nothing.")]

-- The right's holder guard `H` after `that`.
#guard shownText (doc (cline [] (some (rel (0, 1) (some 1))) []) (r21Doc (adult 0) (base := base))) ==
  [("RC1", "Claim of right 1. Every state must grant each person access, where that state is the country of that " ++
     "person."),
   ("RC3", "For every person that that person is adult there is at least one state such that that state is the " ++
     "country of that person."),
   ("RC4", "This line leaves out nothing.")]

/-- `s_a = s_b`, slot o (0) before the holder slot (1): the holder is `the first person` whatever the slot order. -/
def pubDoc : VE.Rights.RightsDoc :=
  mkRights ["state", "person"] [("parent_of", ["person", "person"])]
    [VE.Norms.Checks.oblig "publish_required" ["person", "person"] false none "{0} publish about {1}"]
    [] block [⟨"r12", "person", .top, [line .claim (strictNode "publish" "publish_required" true) (some 1)]⟩] [] []

def pubLine : CLine :=
  ⟨line .claim (strictNode "publish" "publish_required" true) (some 1), [], some (rel (0, 1) (some 1) "parent_of"),
    [], (0, 100)⟩

#guard (shownText ⟨pubDoc, [("r12", "publish", pubLine)], []⟩).map (·.2) ==
  ["Claim of right 1. Every first person must publish about each second person, where the first person is a parent " ++
    "of the second person.",
   "For every first person there is at least one second person such that the second person is a parent of the " ++
    "first person.",
   "This line leaves out nothing."]

/-! ## RC4: quoted source bytes, and `bytes [<a>, <b>)` for each trigger -/

#guard shownText (doc (cline [] none [(0, 8), (29, 43), (116, 128)])) ==
  [("RC4", "This line leaves out: \"Everyone\"; \"public service\"; \"Café rules.\".")]
-- "may not", a double quote, a G6 substring.
#guard shownText (doc (cline [] none [(45, 68)])) == [("RC4", "This line leaves out: bytes [45, 68).")]
#guard shownText (doc (cline [] none [(69, 96)])) == [("RC4", "This line leaves out: bytes [69, 96).")]
#guard shownText (doc (cline [] none [(97, 115)])) == [("RC4", "This line leaves out: bytes [97, 115).")]
-- Not UTF-8 text (inside `é`): the byte form; outside the source: refused.
#guard shownText (doc (cline [] none [(116, 120)])) == [("RC4", "This line leaves out: bytes [116, 120).")]
#guard shownText (doc (cline [] none [(120, 129)])) ==
  [("error", "InvalidInput: equal-access: elided span [120, 129) is outside the source")]

/-! ## The gate, G6 and G9 -/

-- A wording that makes RC3 read two ways (` such that ` twice after the lead) is refused, never shown.
#guard shownText (doc (cline [] (some (rel (0, 1) (some 1) "odd")) [])) ==
  [("error", "CheckerUnavailable: the RC3 line of equal-access does not pass the all-derivations gate")]
#guard (gated "RC3" "For every person there is at least one state such that that state is such that that person odd.")
  == none
-- A wording with `may not` (G9) is refused; a missing word is not worded.
#guard shownText (doc (cline [] (some (rel (0, 1) (pred := "forbidden"))) [])) ==
  [("error", "CheckerUnavailable: the RC1 line of equal-access does not pass the all-derivations gate")]
#guard shownText (doc (cline [] (some (rel (0, 1) (pred := "missing"))) [])) ==
  [("error", "CheckerUnavailable: VE could not word the RC1 line of equal-access")]

/-- Every rendered sentence above: one derivation, its own frame's, and no G6 or G9 substring. -/
def rendered : List Row :=
  [doc rc1Line, doc (cline [] (some (rel (1, 0) (pred := "lives_in"))) []),
   doc (cline [] (some (rel (0, 1) (some 1))) []), doc (cline [] (some (rel (0, 1) (some 1))) []) (r21Doc (adult 0)
     (base := base)), ⟨pubDoc, [("r12", "publish", pubLine)], []⟩,
   doc (cline [] none [(0, 8), (29, 43), (116, 128)]), doc (cline [] none [(45, 68)]), doc (cline [] none [(69, 96)]),
   doc (cline [] none [(97, 115)]), doc (cline [] none [(116, 120)])].flatMap
    fun D => (english D lexicon source).toOption.getD []

#guard rendered.length == 18
#guard rendered.all fun r => (readings r.text).length == 1 && (gated r.frame r.text).isSome
#guard rendered.all fun r => ["ve__", "rd-", "soft__", "rights__", "may not"].all (!holds · r.text)
#guard (rendered.map (·.frame)).eraseDups == ["RC1", "RC4", "RC3"]
-- RC2's frames read each instance alone; the frames' leads are pairwise not prefixes of each other.
#guard ["that state is the country of that person", "the second person is a parent of the first person"].all
  (fun t => (gated "RC2" t).isSome)
#guard (rcFrames.map fun (_, ps) => match ps with | .lit s :: _ => s | _ => "").Pairwise
  fun a b => a ≠ "" && b ≠ "" && !a.toList.isPrefixOf b.toList && !b.toList.isPrefixOf a.toList

end VE.RightClauses.EnglishExamples
