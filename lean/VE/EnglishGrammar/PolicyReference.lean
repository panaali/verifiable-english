import VE.EnglishGrammar.Policy

/-! Spec 5.2's vocabulary policy as a reference for the optimised `Policy.lean` (`E2Examples.lean` `#guard`s).
The accepted-head table and the codes the fixed point settled come from `PolicyCtx.of`, so the fixed-point ownership
rule has one implementation.
Test-only: nothing on an admission path reads this reference. -/

namespace VE.EnglishGrammar.PolicyReference
open VE.EnglishGrammar

/-! Python's vocabulary policy (english.py:230–527, printer.py:183–338) -/
def sortNouns (E : Env) (O : Overlay) (s : SortDecl) : List String :=
  match E.declaredNoun O s.name with
  | some n => [n] ++ (E.pluralOf s.name).toList
  | none => []

/-- `template_checks` (printer.py:223–232): the length and sort-noun codes of a wording or a negative. -/
def templateCodes (E : Env) (O : Overlay) (value : String) : List String :=
  let nouns := E.declaredSorts.map (·.name) ++ E.declaredSorts.flatMap (sortNouns E O)
  let tw := tokens value
  (if value.length > 80 || (splitWs value).length > 8 then ["TEMPLATE_LENGTH"] else []) ++
  (if nouns.any (fun n => let ts := tokens n; !ts.isEmpty &&
      (List.range (tw.length + 1)).any fun i => (tw.drop i).take ts.length == ts) then ["SORT_NOUN"] else [])

/-- The lint codes of a declared wording `value` of predicate `name` (`_NaturalVocabulary`). -/
def lintCodesWithHeads (E : Env) (O : Overlay) (name value : String) (k : Nat)
    (heads : List (String × String)) : List String :=
  let predNames := E.declaredPreds.map (·.name)
  let names := E.declaredSorts.map (·.name) ++ predNames ++ E.declaredConsts.map (·.name)
  let nounTexts : List (String × String) := E.declaredSorts.flatMap fun s => (sortNouns E O s).map (·, s.name)
  let owned (w : String) : Bool :=
    names.any (fun x => x == w && x != name) || heads.any (fun (h, p) => h == w && p != name) ||
    nounTexts.any fun (n, s) => (tokens n).getLast? == some w && s != name
  let predicateHeads := predNames ++ heads.map (·.1)
  let negatedHeads := ["un", "non", "un-", "non-"].flatMap fun pre => predicateHeads.map (pre ++ ·)
  let forbidden := logicalWords ++ (if E.profiles.contains "closure@0" then closureWords else [])
  let phraseCodes (phrase : String) (conn : Bool) : List String :=
    let wds := tokens phrase
    let forb := if conn && phrase == "at" then forbidden.filter (· != "at") else forbidden
    (if wordsPhrase phrase then [] else ["PHRASE_SYNTAX"]) ++
    (if wds.any forb.contains then ["LOGICAL_WORD"] else []) ++
    (if wds.any variableWord then ["VARIABLE_TOKEN"] else []) ++
    (if wds.any owned then ["SYMBOL_COLLISION"] else []) ++
    (if wds.any negatedHeads.contains then ["NEGATED_HEAD"] else [])
  let dup := if (E.declaredPreds.filter fun d => E.declaredWording O d.name == some value).length > 1
    then ["DUPLICATE_TEMPLATE"] else []
  if k > 2 then
    let len := if value.length > 160 || (splitWs value).length > 24 then ["TEMPLATE_LENGTH"] else []
    match templateParts value k with
    | none => dup ++ ["TEMPLATE_SHAPE"] ++ len
    | some parts => dup ++ len ++ (parts.drop 1).flatMap fun ph =>
        let s := stripWs ph
        if s.isEmpty then [] else phraseCodes s true
  else
    let shape := match shapePhrase value k with
      | none => ["TEMPLATE_SHAPE"]
      | some phrase =>
        let pw := splitWs phrase
        phraseCodes phrase false ++
        (if k == 1 then
          (if pw.head? != some "is" || pw.length < 2 then ["TEMPLATE_SHAPE"]
           else if pw.length != 2 then ["UNARY_MODIFIER"] else [])
         else match pw.head?, pw.getLast? with
          | some first, some last =>
            (if auxiliaries.contains first then ["BINARY_AUXILIARY"] else []) ++
            (if converseEndings.contains last then ["BINARY_CONVERSE"] else []) ++
            (if !first.endsWith "s" then ["BINARY_VERB"] else [])
          | _, _ => [])
    (templateCodes E O value ++ dup ++ shape).eraseDups

def lintCodes (E : Env) (O : Overlay) (name value : String) (k : Nat) : List String :=
  lintCodesWithHeads E O name value k (PolicyCtx.of E O).lintHeads

def acceptedHeads (E : Env) (O : Overlay) : List (String × String) :=
  (PolicyCtx.of E O).lintHeads

/-- Step 4 of `acceptsDeclared` (english.py:368–372): the key of `p`'s declared wording or negative is the key of
another declared predicate's wording (its strict wording when it declares none) or declared negative. -/
def duplicateWording (E : Env) (O : Overlay) (p : String) : Bool :=
  let ownTexts (d2 : PredDecl) : List String :=
    [(E.declaredWording O d2.name).getD (strictWording d2.name d2.arity)] ++ (E.declaredNegative O d2.name).toList
  let mine := (E.declaredWording O p).toList ++ (E.declaredNegative O p).toList
  (E.declaredPreds.filter (·.name != p)).any fun d2 =>
    (ownTexts d2).any fun x => mine.any fun y => wordingKey x == wordingKey y

/-- Whether Python accepts the declared wording of `name` (english.py:264–372). -/
def acceptsDeclared (E : Env) (O : Overlay) (name : String) : Bool :=
  match E.predicate? name, E.declaredWording O name with
  | some d, some t =>
    let k := d.arity
    let heads := acceptedHeads E O
    let codes := ((PolicyCtx.of E O).settled.lookup name).getD (lintCodesWithHeads E O name t k heads)
    if k > 2 then codes.isEmpty else
    let idiom := (idioms k).contains t
    let p0 := if t.startsWith "{0} " then t.drop 4 else t
    let phrase := if k == 1 then p0 else if p0.endsWith " {1}" then p0.dropRight 4 else p0
    let shaped := t == "{0} " ++ phrase ++ (if k == 1 then "" else " {1}")
    let others := E.declaredPreds.filter (·.name != name)
    let collision :=
      ((E.declaredPreds.map (·.name) ++ E.declaredConsts.map (·.name)).filter (· != name)).any
        (wordOccurs · phrase) ||
      others.any fun d2 => match heads.find? (fun (_, p) => p == d2.name) with
        | some (h, _) => !["is", "was", "a", "an"].contains h && wordOccurs h phrase
        | none => false
    let isHeads := E.declaredPreds.filterMap fun d2 => match E.declaredWording O d2.name with
      | some v => if v.startsWith "{0} is " && heads.any (·.2 == d2.name) then (splitWs v)[2]? else none
      | none => none
    let negated := (splitWs phrase).any fun w =>
      (E.declaredPreds.map (·.name) ++ isHeads).any fun h => w == "un" ++ h || w == "non" ++ h
    let ms := (if k == 1 then complementPatterns else activePatterns).filterMap (matchPattern phrase)
    let nounWords := E.declaredSorts.map (·.name) ++ E.declaredSorts.flatMap fun s => (sortNouns E O s).flatMap splitWs
    let safeAdj := ms.all fun a => match a with
      | some w => !(reserved ++ auxiliaries ++ nounWords).contains w
      | none => true
    let rescue := shaped && codes.all eligibleCodes.contains && !collision && !negated && t.length ≤ 80 &&
      !ms.isEmpty && safeAdj
    let content := contentWords t
    let anchored := content.any (contentWords (name ++ " " ++ d.description)).contains
    let idiomCollision := E.declaredConsts.any (fun c => wordOccurs c.name phrase) ||
      others.any fun d2 =>
        let other := (E.declaredWording O d2.name).getD ""
        let head := (heads.find? (fun (_, p) => p == d2.name)).map (·.1)
        [some d2.name, head].any fun tok? => match tok? with
          | none => false
          | some tok =>
            !tok.isEmpty && !["is", "was", "a", "an", "has"].contains tok &&
            let shared := (name.splitOn "_").contains tok && (d2.name.splitOn "_").contains tok
            let headCollision := some tok == head && content.all (contentWords other).contains
            !shared && (tok == d2.name || headCollision) && wordOccurs tok phrase
    let converse := phrase.endsWith " by" && !name.endsWith "_by"
    let idiomOk := codes.all (eligibleCodes ++ ["VARIABLE_TOKEN"]).contains && anchored && !idiomCollision &&
      !converse && !negated && !codes.contains "DUPLICATE_TEMPLATE"
    let accepted1 := if !codes.isEmpty || idiom then (if idiom then idiomOk else rescue) else true
    let suggestedOk := E.suggestedPred name && k == 1 && match unaryPhrase t with
      | none => false
      | some ph =>
        let sHeads := (E.declaredPreds.map (·.name)) ++ heads.map (·.1)
        let negHeads := ["un", "non", "un-", "non-"].flatMap fun pre => sHeads.map (pre ++ asciiLower ·)
        let phWords := (runs (fun c => isLower c || isDigit c || c == '_' || c == '-') (pyLower ph)).filterMap
          fun w => let cs := w.toList.dropWhile (fun c => !isLower c)
                   if cs.isEmpty then none else some (String.mk cs)
        !E.declaredConsts.any (fun c => wordOccursI c.name ph) &&
        !E.declaredPreds.any (fun d2 => d2.name != name &&
          ((E.declaredWording O d2.name).map wordingKey) == some (wordingKey t)) &&
        !phWords.any negHeads.contains && !codes.contains "NEGATED_HEAD"
    let accepted2 := accepted1 || suggestedOk
    let accepted3 := accepted2 && (idiom || !(runs isLower t).any extraReserved.contains)
    let accepted4 := accepted3 && !(E.profiles.contains "order@0" &&
      (runs isLower (pyLower t)).any comparisonWords.contains)
    accepted4 && !duplicateWording E O name
  | _, _ => false

/-- Python's wording and negative for a predicate before the profile steps (english.py:264–389). -/
def mainSelection (E : Env) (O : Overlay) (d : PredDecl) : String × Option String :=
  let k := d.arity
  match E.declaredWording O d.name with
  | none =>
    if k > 2 then (strictWording d.name k, none)
    else if lowerWord d.name && !reserved.contains d.name && (k == 1 || mechanicalVerbs.contains d.name) then
      (strictWording d.name k, none)
    else ((fallbackWording d.name k).getD (strictWording d.name k), none)
  | some t =>
    if k > 2 then (if acceptsDeclared E O d.name then (t, none) else (strictWording d.name k, none))
    else if acceptsDeclared E O d.name then
      let neg := match E.declaredNegative O d.name with
        | some n => if negativeTemplate t k == some n && n.length ≤ 120 && (splitWs n).length ≤ 18 then some n else none
        | none => none
      (t, neg)
    else ((fallbackWording d.name k).getD t, none)

/-- Python's selected wording and negative of a predicate (english.py:390–527). -/
def policyPredicate (E : Env) (O : Overlay) (p : String) : Option (String × Option String) :=
  let F := E.forms
  match E.predicate? p with
  | none => none
  | some d =>
    let (w, n) := mainSelection E O d
    let (w, n) := match F.wordings.lookup p with                  -- roles, the four words, risk forms
      | some fw => if E.modal p then (w, n) else (fw, n)
      | none => (w, n)
    let n := match F.negatives.lookup p with
      | some fn => some fn
      | none => n
    let exempt := E.roles.contains p || p.startsWith "risk__" || altWords.contains p   -- english.py:432–447
    let riskKeys := riskTemplates.map wordingKey
    let (w, n) :=
      if E.risk && !exempt && ([some w, n].any fun f => match f with
          | some x => riskKeys.contains (wordingKey x) | none => false) then
        ((fallbackWording p d.arity).getD w, none)
      else (w, n)
    if E.modal p then                                              -- english.py:521–527
      match F.wordings.lookup p with
      | some fw => some (fw, none)
      | none => some (w, none)
    else some (w, n)

def fallbackNoun (s : String) : String := "entity of sort " ++ jsonQuote s
def letterWords (s : String) : Bool := (s.splitOn " ").all fun w => !w.isEmpty && w.all isLetter

/-- Python's selected noun of every sort (english.py:239–252, :419). -/
def policyNouns (E : Env) (O : Overlay) : List (String × String) :=
  let symbols := E.declaredPreds.map (·.name) ++ E.declaredConsts.map (·.name)
  let first := E.declaredSorts.map fun s =>
    let base := (E.declaredNoun O s.name).getD s.name
    let ok := letterWords base && !(splitWs (asciiLower base)).any reserved.contains &&
      !symbols.contains (asciiLower base)
    (s.name, if ok then base else fallbackNoun s.name)
  let deduped := first.map fun (s, n) =>
    if (first.filter fun (_, m) => wordingKey m == wordingKey n).length > 1 then (s, fallbackNoun s) else (s, n)
  let generated := E.generatedSorts.map fun s => (s.name, fallbackNoun s.name)
  (deduped ++ generated).map fun (s, n) => (s, (E.forms.nouns.lookup s).getD n)

/-- The spelling forms of a constant's value whose keys are compared (english.py:492–498). -/
def spellingKeys (value : String) : List String :=
  let capital := if value.startsWith "the " then ["T" ++ value.drop 1] else []
  let article := if lowerWord value then ["the " ++ value] else []
  (([value] ++ capital ++ article).map wordingKey).eraseDups
def bareOk (c : String) : Bool := lowerWord c && !reserved.contains c && !["is", "has"].contains c

/-- Python's selected spelling of every constant (english.py:460–510). -/
def policySpellings (E : Env) (O : Overlay) : List (String × String) :=
  let nounKeys := (policyNouns E O).map fun (_, n) => wordingKey n
  let initial := E.constants.map fun c => (c.name, if bareOk c.name then c.name else jsonQuote c.name)
  let named (c : String) : Bool := (E.declaredSpelling O c).isSome        -- `self.declared_constants`
  let declared := E.declaredConsts.filterMap fun c => (E.declaredSpelling O c.name).map (c.name, ·)
  let quotedDeclared := initial.map fun (c, v) => if (declared.lookup c).isSome then (c, jsonQuote c) else (c, v)
  let candidates := declared.filter fun (_, form) =>
    letterWords form && !(splitWs (asciiLower form)).any (fun w => w != "the" && reserved.contains w) &&
    !nounKeys.contains (wordingKey form)
  let unique := candidates.filter fun (_, form) =>
    (candidates.filter fun (_, f2) => wordingKey f2 == wordingKey form).length == 1
  let start := quotedDeclared.map fun (c, v) => match unique.lookup c with
    | some form => (c, form)
    | none => (c, v)
  let step (cur : List (String × String)) : List (String × String) :=
    let owners := cur.flatMap fun (c, v) => (spellingKeys v).map (·, c)
    let collided := cur.filter fun (c, v) => named c && v != jsonQuote c &&
      (spellingKeys v).any fun key => ((owners.filter (·.1 == key)).map (·.2)).eraseDups.length > 1
    cur.map fun (c, v) => if collided.any (·.1 == c) then (c, jsonQuote c) else (c, v)
  (List.range (E.constants.length + 1)).foldl (fun cur _ => step cur) start

/-! V6 -/
def policyFailures (E : Env) (O : Overlay) (L : Lexicon) : List Failure :=
  let preds := E.predicates.map (·.name)
  let nouns := policyNouns E O
  let spellings := policySpellings E O
  (L.wordings.filterMap fun (p, w) =>
    if !preds.contains p then none else
    match policyPredicate E O p with
    | some (pw, _) => if w == pw || some w == fallbackWording p (E.arity p) then none else some ("V6", "predicate", p)
    | none => none) ++
  (L.negatives.filterMap fun (p, n) =>
    if !preds.contains p then none else
    match policyPredicate E O p with
    | some (pw, pn) => if pn == some n && L.wordings.lookup p == some pw then none else some ("V6", "negative", p)
    | none => none) ++
  (L.nouns.filterMap fun (s, n) =>
    match nouns.lookup s with
    | some pn => if n == pn || n == fallbackNoun s then none else some ("V6", "sort", s)
    | none => none) ++
  (L.spellings.filterMap fun (c, sp) =>
    match spellings.lookup c with
    | some ps => if sp == ps || sp == jsonQuote c then none else some ("V6", "constant", c)
    | none => none)

def policyOk (E : Env) (O : Overlay) (L : Lexicon) : Bool := (policyFailures E O L).isEmpty

/-! The overlay check: the producer's three refusals (english.py:373–375, :442–443, :511–517) -/

/-- Whether a wording or the negative of `d`'s main selection has the key of a risk template (english.py:437–441). -/
def riskKeyed (E : Env) (O : Overlay) (d : PredDecl) : Bool :=
  let (w, n) := mainSelection E O d
  ((w :: n.toList).map wordingKey).any (riskTemplates.map wordingKey).contains

/-- Whether a linter issue stays at the path of `d`'s declared negative once `d`'s declared wording is accepted
(printer.py:309–322, english.py:382–389): for one or two arguments when the negative is not selected; for more,
when the linter reports it. -/
def negativeLeft (E : Env) (O : Overlay) (d : PredDecl) : Bool :=
  match E.declaredNegative O d.name, E.declaredWording O d.name with
  | some n, some t =>
    if d.arity ≤ 2 then (mainSelection E O d).2 != some n
    else !(templateCodes E O n).isEmpty || negateVerb t != some n
  | _, _ => false

/-- The producer's first refusal of the overlay `O`, in Python's order: O1, a duplicate wording, in the main loop;
O2, a reused risk wording; O3, the final comparison, sort entries before predicate entries. `E` has `O` merged in
(`Env.decode`). A constant entry is never refused (english.py:471–508). -/
def overlayCheck (E : Env) (O : Overlay) : Option Failure :=
  let named (p : String) : Bool := O.predicates.any (·.1 == p)
  let exempt (p : String) : Bool := E.roles.contains p || p.startsWith "risk__" || altWords.contains p
  let duplicate := E.declaredPreds.find? fun d => named d.name && d.arity ≤ 2 && duplicateWording E O d.name
  let risk := E.declaredPreds.find? fun d => E.risk && named d.name && !exempt d.name && riskKeyed E O d
  let sortEntry := O.sorts.find? fun (s, noun) => (policyNouns E O).lookup s != some noun
  let predEntry := O.predicates.find? fun (p, _, _) => match E.predicate? p with
    | some d => !E.roles.contains p && (!acceptsDeclared E O p || negativeLeft E O d)
    | none => false
  match duplicate, risk, sortEntry, predEntry with
  | some d, _, _, _ => some ("O1", "predicate", d.name)
  | none, some d, _, _ => some ("O2", "predicate", d.name)
  | none, none, some (s, _), _ => some ("O3", "sort", s)
  | none, none, none, some (p, _, _) => some ("O3", "predicate", p)
  | none, none, none, none => none

end VE.EnglishGrammar.PolicyReference
