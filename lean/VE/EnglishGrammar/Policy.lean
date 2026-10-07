import VE.EnglishGrammar.Rules


namespace VE.EnglishGrammar

-- SortDecl gains:   plural : Option String := none
--                   generated : Bool := false          -- the severity sort
-- PredDecl gains:   suggested : Bool := false
--                   generated : Bool := false          -- the four alternatives@0 words, the five risk__ predicates
-- ConstDecl gains:  generated : Bool := false          -- the severity classes
-- AltBlock gains:   optional : List String := []       -- inaction, taken, proximate, where present

def Env.roles (E : Env) : List String :=
  match E.alternatives with
  | some B => [B.available, B.leadsTo] ++ B.optional
  | none => []
def Env.pluralOf (E : Env) (s : String) : Option String := (E.sorts.find? (·.name == s)).bind (·.plural)
def Env.suggestedPred (E : Env) (p : String) : Bool := ((E.predicate? p).map (·.suggested)).getD false
/-- What Python enumerates (`_ProfilePredicates`, environment.py:126–146): the declared symbols. -/
def Env.declaredSorts (E : Env) : List SortDecl := E.sorts.filter (!·.generated)
def Env.declaredPreds (E : Env) : List PredDecl := E.predicates.filter (!·.generated)
def Env.declaredConsts (E : Env) : List ConstDecl := E.constants.filter (!·.generated)
def Env.generatedSorts (E : Env) : List SortDecl := E.sorts.filter (·.generated)

/-! Word lists (printer.py:93–105, english.py:31–49, :214, :283–285, :342; english_phrases.py:7–8) -/
def wordList (s : String) : List String := splitWs s
def logicalWords : List String := wordList "all any every some each no none not never neither nor
    and or both either if then unless except without only exists forall implies
    true false equal equals there such that case condition for at least most
    exactly does do must may can cannot should shall will would whenever when
    implies iff otherwise always sometimes one two three four five six seven
    eight nine ten a an the lacks nothing nobody everything everybody just solely
    many several another but plus few might"
def closureWords : List String := wordList "reachable reachability steps satisfying zero more from"
def auxiliaries : List String := wordList "is are was were be been being gets got"
def converseEndings : List String := wordList "by to of from with for"
def ordinals : List String := wordList "first second third fourth fifth sixth seventh eighth"
def extraReserved : List String := wordList "this it holds impossible classified recorded relation entity sort named
    first second following hold who where step steps source destination from reachable using starting ending
    definition end therefore so hence" ++ ordinals
def reserved : List String := logicalWords ++ extraReserved
def comparisonWords : List String := wordList "less more than least most same"
def contentStop : List String := wordList "a an the is was are be been being has have its in on at to of for from by
    with and or as that this recorded predicate first second"
def mechanicalVerbs : List String := wordList "owns audits undermines performs follows benefits outranks exceeds"
def eligibleCodes : List String := ["LOGICAL_WORD", "PHRASE_SYNTAX", "UNARY_MODIFIER", "TEMPLATE_SHAPE",
  "TEMPLATE_LENGTH", "SORT_NOUN", "SYMBOL_COLLISION", "BINARY_CONVERSE", "BINARY_AUXILIARY", "BINARY_VERB"]
def boundaryWords : List String := wordList "is does not and or if then that who which both either every some for"
def blockedWords : List String := wordList "than by no never longer neither nor without true false equals equal"
def naryHeads : List String := wordList "reports records has is at maps relates links"
def altWords : List String := ["avoidable", "unavoidable", "allows", "prevents"]
def riskTemplates : List String :=
  ["{0} might lead to {1}", "{0} cannot lead to {1}", "{0} might not lead to {1}", "{0} is {1}",
   "{0} is {1} or worse", "{0} has a less severe worst case than {1}", "{0} is more severe than {1}",
   "{0} might prevent {1}", "{0} does not lead to {1}", "{0} may lead to {1}", "{0} could lead to {1}",
   "{0} risks {1}", "{0} is likely to lead to {1}", "{0} increases the risk of {1}",
   "{0} certainly leads to {1}", "{0} prevents {1}", "{0} is safer than {1}"]

/-! The two pattern tables of the rescue (english.py:31–43) -/
inductive PatWord where
  | lit (w : String)
  | adj
  deriving DecidableEq, Repr
def lits (s : String) : List PatWord := (s.splitOn " ").map PatWord.lit
def complementPatterns : List (List PatWord) :=
  [lits "is subject to the jurisdiction of the United States", lits "is a citizen of the United States",
   lits "was born in the United States", lits "was naturalized in the United States"] ++
  (["fully", "newly", "currently", "publicly"].map fun a => [.lit "is", .lit a, .adj]) ++
  [[.lit "is", .adj, .lit "in", .lit "good", .lit "standing"], [.lit "is", .adj, .lit "under", .lit "review"]]
def activePatterns : List (List PatWord) :=
  ["affords due process of law to", "denies the equal protection of the laws to", "reports to",
   "contributes to", "responds to", "communicates with", "collaborates with", "has access to",
   "has authority over", "has responsibility for"].map lits

/-! Character classes and scanners -/
def isLower (c : Char) : Bool := 'a' ≤ c && c ≤ 'z'
def isUpper (c : Char) : Bool := 'A' ≤ c && c ≤ 'Z'
def isLetter (c : Char) : Bool := isLower c || isUpper c
def isDigit (c : Char) : Bool := '0' ≤ c && c ≤ '9'
def isTokChar (c : Char) : Bool := isLetter c || isDigit c || c == '_'
def isW (c : Char) : Bool := isTokChar c                                   -- Python's `\w`, on ASCII
-- `lowerWord` (a non-empty run of `a` to `z`) is `Rules.lean:210`'s

/-- The maximal runs of characters satisfying `p` (`re.findall('[a-z]+', s)` for `isLower`). -/
def runs (p : Char → Bool) (s : String) : List String :=
  let rec go : List Char → List Char → List String
    | [], cur => if cur.isEmpty then [] else [String.mk cur.reverse]
    | c :: cs, cur => if p c then go cs (c :: cur) else
        if cur.isEmpty then go cs [] else String.mk cur.reverse :: go cs []
  go s.toList []

/-- `_TOKENS.findall` (printer.py:102): `[A-Za-z][A-Za-z0-9_]*(?:-[A-Za-z]+)?`. -/
def tokens (s : String) : List String :=
  let rec go : Nat → List Char → List String
    | 0, _ => []
    | _ + 1, [] => []
    | n + 1, c :: rest =>
      if isLetter c then
        let body := rest.takeWhile isTokChar
        let after := rest.drop body.length
        match after with
        | '-' :: d :: more =>
          if isLetter d then
            let ls := (d :: more).takeWhile isLetter
            String.mk (c :: body ++ '-' :: ls) :: go n ((d :: more).drop ls.length)
          else String.mk (c :: body) :: go n after
        | _ => String.mk (c :: body) :: go n after
      else go n rest
  go (s.length + 1) s.toList

/-- Python's `str.lower` on what `[a-z]+` can see: ASCII capitals, the Kelvin sign, `İ`. -/
def pyLower (s : String) : String :=
  String.join (s.toList.map fun c =>
    if isUpper c then String.singleton (Char.ofNat (c.toNat + 32))
    else if c == '\u212A' then "k"                          -- the Kelvin sign
    else if c == '\u0130' then "i\u0307"                     -- `İ`: `i` and a combining dot
    else String.singleton c)
def asciiLower (s : String) : String := s.map fun c => if isUpper c then Char.ofNat (c.toNat + 32) else c

/-- `re.search(r'\b' + re.escape(tok) + r'\b', phrase)`, with `\w` on ASCII. -/
def wordOccurs (tok phrase : String) : Bool :=
  let t := tok.toList
  let p := phrase.toList
  let w (i : Nat) : Bool := match p[i]? with | some c => isW c | none => false
  let wb (i : Nat) : Bool := if i == 0 then false else w (i - 1)
  !t.isEmpty && (List.range (p.length + 1)).any fun i =>
    i + t.length ≤ p.length && (p.drop i).take t.length == t &&
    wb i != w i && wb (i + t.length) != w (i + t.length)

/-- `wordOccurs tok phrase`, where `phraseRuns` is `runs isW phrase`: a token of word characters occurs between word
boundaries exactly when it is one of the phrase's maximal runs of word characters, so the policy compares it with
those once computed; any other token is searched as `wordOccurs` searches. -/
def wordOccursIn (phraseRuns : List String) (phrase tok : String) : Bool :=
  if !tok.isEmpty && tok.all isW then phraseRuns.contains tok else wordOccurs tok phrase

/-- The letters `[A-Za-z]` matches under `re.I` beyond ASCII: `İ`, `ı`, `ſ` and the Kelvin sign. -/
def reIExtra : List Char := [Char.ofNat 0x130, Char.ofNat 0x131, Char.ofNat 0x17F, Char.ofNat 0x212A]
def reILetter (c : Char) : Bool := isLetter c || reIExtra.contains c
/-- The ASCII letter a character is matched as under `re.I`: `İ` and `ı` as `i`, `ſ` as `s`, the Kelvin sign as `k`. -/
def reIFold (c : Char) : Char :=
  if isUpper c then Char.ofNat (c.toNat + 32)
  else if c.toNat == 0x130 || c.toNat == 0x131 then 'i'
  else if c.toNat == 0x17F then 's'
  else if c.toNat == 0x212A then 'k'
  else c

/-- `re.search(r'\b' + re.escape(tok) + r'\b', phrase, re.I)` on a phrase of `unaryPhrase`: characters compared
as `reIFold` folds them, `reIExtra`'s letters counted as word characters. -/
def wordOccursI (tok phrase : String) : Bool :=
  let t := tok.toList.map reIFold
  let p := phrase.toList
  let w (i : Nat) : Bool := match p[i]? with | some c => isW c || reIExtra.contains c | none => false
  let wb (i : Nat) : Bool := if i == 0 then false else w (i - 1)
  !t.isEmpty && (List.range (p.length + 1)).any fun i =>
    i + t.length ≤ p.length && ((p.drop i).take t.length).map reIFold == t &&
    wb i != w i && wb (i + t.length) != w (i + t.length)

/-- `_content_words` (english.py:217–219). -/
def contentWords (text : String) : List String :=
  ((runs isLower (pyLower text)).filter (!contentStop.contains ·)).eraseDups.map fun w =>
    if w.endsWith "ing" then w.dropRight 3 else if w.endsWith "ed" then w.dropRight 2
    else if w.endsWith "s" then w.dropRight 1 else w

def wordsPhrase (s : String) : Bool := (s.splitOn " ").all lowerWord        -- `_WORDS`
def variableWord (w : String) : Bool :=                                      -- `_VARIABLE`
  match w.toList with
  | 'x' :: ds => ds.all isDigit
  | cs =>
    let up := cs.takeWhile isUpper
    !up.isEmpty && (cs.drop up.length).all isDigit

/-- `_template_head` (printer.py:176–180). -/
def templateHead (value : String) (k : Nat) : Option String :=
  let words := tokens value
  let words := if k == 1 && words.head? == some "is" then words.drop 1 else words
  words.head?

/-- Python's strict wording (printer.py:190–194), for every name. -/
def strictWording (name : String) (k : Nat) : String :=
  if k == 1 then "{0} is " ++ name
  else if k == 2 then "{0} " ++ name ++ " {1}"
  else "{0} has recorded relation " ++ name ++ " with " ++ " and ".intercalate
    ((List.range (k - 1)).map fun i =>
      "argument " ++ (["two", "three", "four", "five", "six"].getD i "") ++ " {" ++ toString (i + 1) ++ "}")

/-- The phrase of `\{0\} (.+)` (one argument) or `\{0\} (.+) \{1\}` (two); `.` excludes a line break. -/
def shapePhrase (v : String) (k : Nat) : Option String :=
  if !v.startsWith "{0} " then none else
  let rest := v.drop 4
  if k == 1 then (if rest.isEmpty || rest.contains '\n' then none else some rest)
  else if rest.endsWith " {1}" then
    let mid := rest.dropRight 4
    if mid.isEmpty || mid.contains '\n' then none else some mid
  else none

/-- `re.findall(r"\{[^{}]*\}", v)`. -/
def braceSlots (v : String) : List String :=
  let rec go : Nat → List Char → List String
    | 0, _ => []
    | _ + 1, [] => []
    | n + 1, c :: rest =>
      if c == '{' then
        let inner := rest.takeWhile fun d => d != '{' && d != '}'
        match rest.drop inner.length with
        | '}' :: more => String.mk ('{' :: inner ++ ['}']) :: go n more
        | _ => go n rest
      else go n rest
  go (v.length + 1) v.toList

/-- `re.split(r"\{[0-5]\}", v)`. -/
def splitSlots (v : String) : List String :=
  let rec go : Nat → List Char → List Char → List String
    | 0, _, cur => [String.mk cur.reverse]
    | _ + 1, [], cur => [String.mk cur.reverse]
    | n + 1, '{' :: d :: '}' :: rest, cur =>
      if '0' ≤ d && d ≤ '5' then String.mk cur.reverse :: go n rest [] else go n (d :: '}' :: rest) ('{' :: cur)
    | n + 1, c :: rest, cur => go n rest (c :: cur)
  go (v.length + 1) v.toList []

/-- `(?: [a-z]+)+ ?` (`trail`) and `(?: [a-z]+)+`, as full matches. -/
def connector (s : String) (trail : Bool) : Bool :=
  let s := if trail && s.endsWith " " && s.length ≥ 2 && !(s.dropRight 1).endsWith " " then s.dropRight 1 else s
  s.startsWith " " && ((s.drop 1).splitOn " ").all lowerWord

/-- `template_parts` (`ve/surface/nary.py:13–33`). -/
def templateParts (v : String) (k : Nat) : Option (List String) :=
  if braceSlots v != (List.range k).map (fun i => "{" ++ toString i ++ "}") then none else
  let parts := splitSlots v
  if parts.length != k + 1 then none else
  let mids := (parts.drop 1).take (k - 1)
  if !mids.all (·.startsWith " ") then none else
  let first := parts.headD ""
  if !(first.isEmpty || first == "the value of ") then none else
  if !mids.all (connector · true) then none else
  let last := parts.getLastD ""
  if !(last.isEmpty || connector last false) then none else
  if !((splitWs (parts.getD 1 "")).any naryHeads.contains || first.startsWith "the value of ") then none else
  some parts

/-- A phrase against a pattern: `some adjective?` when it matches. -/
def matchPattern (phrase : String) (pat : List PatWord) : Option (Option String) :=
  let parts := phrase.splitOn " "
  if parts.length != pat.length then none
  else if (parts.zip pat).all (fun (w, p) => match p with | .lit s => w == s | .adj => lowerWord w) then
    some ((parts.zip pat).findSome? fun (w, p) => match p with | .adj => some w | _ => none)
  else none

/-- `unary_phrase` (english_phrases.py:23–31). Its pattern is matched under `re.I`: `is` as `reIFold` folds it, and
`reILetter`'s letters. -/
def unaryPhrase (t : String) : Option String :=
  if t.length > 80 || !t.startsWith "{0} " then none else
  let rest := t.drop 4
  if (rest.take 3).toList.map reIFold != ['i', 's', ' '] then none else
  let body := rest.drop 3
  let tokOk (w : String) : Bool := match w.toList with
    | c :: cs => reILetter c && cs.all fun d => reILetter d || isDigit d || d == '_'
    | [] => false
  let phraseOk (s : String) : Bool := !s.isEmpty && ((s.splitOn " ").flatMap (·.splitOn "-")).all tokOk
  let candidates : List String :=
    (if asciiLower (body.take 2) == "a " then [body.drop 2] else []) ++
    (if asciiLower (body.take 3) == "an " then [body.drop 3] else []) ++ [body]
  match candidates.find? phraseOk with
  | none => none
  | some phrase =>
    let low := pyLower phrase
    if low == "a" || low == "an" || (splitWs low).any (fun w => boundaryWords.contains w || blockedWords.contains w)
    then none else some phrase

/-! Python's vocabulary policy (english.py:230–527, printer.py:183–338)

Spec 5.2's functions re-derive, for every symbol they judge, tables that depend only on the environment and the
overlay: every other predicate's declared wording (each by a lookup through the list of predicates), its template
heads, keys and content words, the sort nouns and their tokens. That made V6 cubic in the number of predicates
(1.5 s at 256, against GE2 item 9's budget of 100 ms). `PolicyCtx.of E O` computes those tables once; each function
below is spec 5.2's, reading a table where the spec recomputed it, and keeps its spec signature as a wrapper.
`PolicyReference.lean` holds spec 5.2's text verbatim, and `E2Examples.lean` checks that the two agree. -/
def sortNouns (E : Env) (O : Overlay) (s : SortDecl) : List String :=
  match E.declaredNoun O s.name with
  | some n => [n] ++ (E.pluralOf s.name).toList
  | none => []

/-- A declared predicate and what the policy reads of it, computed once: its declared wording and negative, the
keys `duplicateWording` compares, the heads `lintCodes` and `acceptsDeclared` read, its content words and the key
of its wording. -/
structure PredFacts where
  decl : PredDecl
  wording : Option String
  negative : Option String
  ownKeys : List String
  lintHead : Option String
  head : Option String
  content : List String
  key : Option String

def PredFacts.of (E : Env) (O : Overlay) (d : PredDecl) : PredFacts :=
  let w := E.declaredWording O d.name
  let n := E.declaredNegative O d.name
  { decl := d, wording := w, negative := n,
    ownKeys := ([w.getD (strictWording d.name d.arity)] ++ n.toList).map wordingKey,
    lintHead := templateHead (w.getD (strictWording d.name d.arity)) d.arity,
    head := templateHead (w.getD "") d.arity, content := contentWords (w.getD ""), key := w.map wordingKey }

/-- The tables of an environment and an overlay that the policy reads for every symbol. -/
structure PolicyCtx where
  E : Env
  O : Overlay
  preds : List PredFacts
  predNames : List String
  constNames : List String
  names : List String
  lintHeads : List (String × String)
  nounLasts : List (Option String × String)
  nounTokens : List (List String)
  negatedHeads : List String
  isHeadNegations : List String
  adjBlocked : List String
  suggestedNegHeads : List String

def PolicyCtx.of (E : Env) (O : Overlay) : PolicyCtx :=
  let preds := E.declaredPreds.map (PredFacts.of E O)
  let predNames := E.declaredPreds.map (·.name)
  let sortNames := E.declaredSorts.map (·.name)
  let constNames := E.declaredConsts.map (·.name)
  let lintHeads := preds.filterMap fun f => f.lintHead.map (·, f.decl.name)
  let isHeads := preds.filterMap fun f => match f.wording with
    | some v => if v.startsWith "{0} is " then (splitWs v)[2]? else none
    | none => none
  let sHeads := predNames ++ preds.filterMap (·.head)
  { E, O, preds, predNames, constNames, names := sortNames ++ predNames ++ constNames, lintHeads,
    nounLasts := E.declaredSorts.flatMap fun s => (sortNouns E O s).map fun n => ((tokens n).getLast?, s.name),
    nounTokens := (sortNames ++ E.declaredSorts.flatMap (sortNouns E O)).map tokens,
    negatedHeads := ["un", "non", "un-", "non-"].flatMap fun pre => (predNames ++ lintHeads.map (·.1)).map (pre ++ ·),
    isHeadNegations := (predNames ++ isHeads).flatMap fun h => ["un" ++ h, "non" ++ h],
    adjBlocked := reserved ++ auxiliaries ++ sortNames ++ E.declaredSorts.flatMap fun s =>
      (sortNouns E O s).flatMap splitWs,
    suggestedNegHeads := ["un", "non", "un-", "non-"].flatMap fun pre => sHeads.map (pre ++ asciiLower ·) }

/-- `template_checks` (printer.py:223–232): the length and sort-noun codes of a wording or a negative. -/
def templateCodesIn (c : PolicyCtx) (value : String) : List String :=
  let tw := tokens value
  (if value.length > 80 || (splitWs value).length > 8 then ["TEMPLATE_LENGTH"] else []) ++
  (if c.nounTokens.any (fun ts => !ts.isEmpty &&
      (List.range (tw.length + 1)).any fun i => (tw.drop i).take ts.length == ts) then ["SORT_NOUN"] else [])

def templateCodes (E : Env) (O : Overlay) (value : String) : List String := templateCodesIn (PolicyCtx.of E O) value

/-- The lint codes of a declared wording `value` of predicate `name` (`_NaturalVocabulary`). -/
def lintCodesIn (c : PolicyCtx) (name value : String) (k : Nat) : List String :=
  let owned (w : String) : Bool :=
    c.names.any (fun x => x == w && x != name) || c.lintHeads.any (fun (h, p) => h == w && p != name) ||
    c.nounLasts.any fun (n, s) => n == some w && s != name
  let forbidden := logicalWords ++ (if c.E.profiles.contains "closure@0" then closureWords else [])
  let phraseCodes (phrase : String) (conn : Bool) : List String :=
    let wds := tokens phrase
    let forb := if conn && phrase == "at" then forbidden.filter (· != "at") else forbidden
    (if wordsPhrase phrase then [] else ["PHRASE_SYNTAX"]) ++
    (if wds.any forb.contains then ["LOGICAL_WORD"] else []) ++
    (if wds.any variableWord then ["VARIABLE_TOKEN"] else []) ++
    (if wds.any owned then ["SYMBOL_COLLISION"] else []) ++
    (if wds.any c.negatedHeads.contains then ["NEGATED_HEAD"] else [])
  let dup := if (c.preds.filter fun f => f.wording == some value).length > 1
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
    (templateCodesIn c value ++ dup ++ shape).eraseDups

def lintCodes (E : Env) (O : Overlay) (name value : String) (k : Nat) : List String :=
  lintCodesIn (PolicyCtx.of E O) name value k

/-- Step 4 of `acceptsDeclared` (english.py:368–372): the key of `p`'s declared wording or negative is the key of
another declared predicate's wording (its strict wording when it declares none) or declared negative. -/
def duplicateWordingIn (c : PolicyCtx) (p : String) : Bool :=
  let mine := ((c.E.declaredWording c.O p).toList ++ (c.E.declaredNegative c.O p).toList).map wordingKey
  (c.preds.filter (·.decl.name != p)).any fun f => f.ownKeys.any fun x => mine.any (x == ·)

def duplicateWording (E : Env) (O : Overlay) (p : String) : Bool := duplicateWordingIn (PolicyCtx.of E O) p

/-- Whether Python accepts the declared wording of `name` (english.py:264–372). -/
def acceptsDeclaredIn (c : PolicyCtx) (name : String) : Bool :=
  let E := c.E
  match E.predicate? name, E.declaredWording c.O name with
  | some d, some t =>
    let k := d.arity
    let codes := lintCodesIn c name t k
    if k > 2 then codes.isEmpty else
    let idiom := (idioms k).contains t
    let p0 := if t.startsWith "{0} " then t.drop 4 else t
    let phrase := if k == 1 then p0 else if p0.endsWith " {1}" then p0.dropRight 4 else p0
    let shaped := t == "{0} " ++ phrase ++ (if k == 1 then "" else " {1}")
    let others := c.preds.filter (·.decl.name != name)
    let phraseRuns := runs isW phrase
    let occurs := wordOccursIn phraseRuns phrase
    let collision :=
      ((c.predNames ++ c.constNames).filter (· != name)).any occurs ||
      others.any fun f => match f.head with
        | some h => !["is", "was", "a", "an"].contains h && occurs h
        | none => false
    let negated := (splitWs phrase).any c.isHeadNegations.contains
    let ms := (if k == 1 then complementPatterns else activePatterns).filterMap (matchPattern phrase)
    let safeAdj := ms.all fun a => match a with
      | some w => !c.adjBlocked.contains w
      | none => true
    let rescue := shaped && codes.all eligibleCodes.contains && !collision && !negated && t.length ≤ 80 &&
      !ms.isEmpty && safeAdj
    let content := contentWords t
    let anchored := content.any (contentWords (name ++ " " ++ d.description)).contains
    let idiomCollision := c.constNames.any occurs ||
      others.any fun f =>
        let d2 := f.decl
        let head := f.head
        [some d2.name, head].any fun tok? => match tok? with
          | none => false
          | some tok =>
            !tok.isEmpty && !["is", "was", "a", "an", "has"].contains tok &&
            let shared := (name.splitOn "_").contains tok && (d2.name.splitOn "_").contains tok
            let headCollision := some tok == head && content.all f.content.contains
            !shared && (tok == d2.name || headCollision) && occurs tok
    let converse := phrase.endsWith " by" && !name.endsWith "_by"
    let idiomOk := codes.all (eligibleCodes ++ ["VARIABLE_TOKEN"]).contains && anchored && !idiomCollision &&
      !converse && !negated && !codes.contains "DUPLICATE_TEMPLATE"
    let accepted1 := if !codes.isEmpty || idiom then (if idiom then idiomOk else rescue) else true
    let suggestedOk := E.suggestedPred name && k == 1 && match unaryPhrase t with
      | none => false
      | some ph =>
        let phWords := (runs (fun c => isLower c || isDigit c || c == '_' || c == '-') (pyLower ph)).filterMap
          fun w => let cs := w.toList.dropWhile (fun c => !isLower c)
                   if cs.isEmpty then none else some (String.mk cs)
        !c.constNames.any (fun x => wordOccursI x ph) &&
        !c.preds.any (fun f => f.decl.name != name && f.key == some (wordingKey t)) &&
        !phWords.any c.suggestedNegHeads.contains && !codes.contains "NEGATED_HEAD"
    let accepted2 := accepted1 || suggestedOk
    let accepted3 := accepted2 && (idiom || !(runs isLower t).any extraReserved.contains)
    let accepted4 := accepted3 && !(E.profiles.contains "order@0" &&
      (runs isLower (pyLower t)).any comparisonWords.contains)
    accepted4 && !duplicateWordingIn c name
  | _, _ => false

def acceptsDeclared (E : Env) (O : Overlay) (name : String) : Bool := acceptsDeclaredIn (PolicyCtx.of E O) name

/-- Python's wording and negative for a predicate before the profile steps (english.py:264–389). -/
def mainSelectionIn (c : PolicyCtx) (d : PredDecl) : String × Option String :=
  let E := c.E
  let O := c.O
  let k := d.arity
  match E.declaredWording O d.name with
  | none =>
    if k > 2 then (strictWording d.name k, none)
    else if lowerWord d.name && !reserved.contains d.name && (k == 1 || mechanicalVerbs.contains d.name) then
      (strictWording d.name k, none)
    else ((fallbackWording d.name k).getD (strictWording d.name k), none)
  | some t =>
    if k > 2 then (if acceptsDeclaredIn c d.name then (t, none) else (strictWording d.name k, none))
    else if acceptsDeclaredIn c d.name then
      let neg := match E.declaredNegative O d.name with
        | some n => if negativeTemplate t k == some n && n.length ≤ 120 && (splitWs n).length ≤ 18 then some n else none
        | none => none
      (t, neg)
    else ((fallbackWording d.name k).getD t, none)

def mainSelection (E : Env) (O : Overlay) (d : PredDecl) : String × Option String :=
  mainSelectionIn (PolicyCtx.of E O) d

/-- Python's selected wording and negative of a predicate (english.py:390–527), over the tables `c` of `E` and
`O`. -/
def policyPredicateIn (c : PolicyCtx) (E : Env) (p : String) : Option (String × Option String) :=
  let F := E.forms
  match E.predicate? p with
  | none => none
  | some d =>
    let (w, n) := mainSelectionIn c d
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

/-- Python's selected wording and negative of a predicate (english.py:390–527). -/
def policyPredicate (E : Env) (O : Overlay) (p : String) : Option (String × Option String) :=
  policyPredicateIn (PolicyCtx.of E O) E p

theorem policyPredicate_tables (E : Env) (O : Overlay) (p : String) :
    policyPredicateIn (PolicyCtx.of E O) E p = policyPredicate E O p := rfl

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
def Lexicon.policyFailures (E : Env) (O : Overlay) (L : Lexicon) : List Failure :=
  let preds := E.predicates.map (·.name)
  let nouns := policyNouns E O
  let spellings := policySpellings E O
  let c := PolicyCtx.of E O
  (L.wordings.filterMap fun (p, w) =>
    if !preds.contains p then none else
    match policyPredicateIn c E p with
    | some (pw, _) => if w == pw || some w == fallbackWording p (E.arity p) then none else some ("V6", "predicate", p)
    | none => none) ++
  (L.negatives.filterMap fun (p, n) =>
    if !preds.contains p then none else
    match policyPredicateIn c E p with
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

def Lexicon.policyOk (E : Env) (O : Overlay) (L : Lexicon) : Bool := (L.policyFailures E O).isEmpty

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

end VE.EnglishGrammar
