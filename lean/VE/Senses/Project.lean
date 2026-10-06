import VE.Senses.Preamble
import VE.EnglishGrammar.Extends

/-! The projection of a dictionary onto S2's lexicon (docs/spec/senses.md 2.5 and 5.3; batch B3).

`usedWords D sents` are the words of `D` one of whose senses has a headword token that some word token of
`sents` folds to (D18). `project D A E L used` appends to the document's environment `E` and its own
lexicon `L` the fresh pack sorts and one predicate per sense of a used word, the default selecting its bare
wording and every other sense its glossed wording, and then runs S2's `Lexicon.failures` on the result:
the projection is refused exactly when S2 refuses it (`project_valid`). Steps 1 to 5 of 2.5 come first
and name the fault in the reader's terms; step 6 names one colliding pair from `clashes`, which repeats
V4's comparison only to name the pair. `project` appends and never chooses: `L`'s selections are kept.
-/

namespace VE.Senses
open Lean VE.Grammar VE.EnglishGrammar

/-- The number of tokens of the mark that opens a gloss at the start of the tokens: 2 for `(` and
`meaning`, 5 for a comma and `in the sense of`. -/
def glossMark : List Tok → Option Nat
  | .punct "(" _ _ :: .word m _ :: _ => if fold m == "meaning" then some 2 else none
  | .punct "," _ _ :: .word a _ :: .word b _ :: .word c _ :: .word d _ :: _ =>
    if fold a == "in" && fold b == "the" && fold c == "sense" && fold d == "of" then some 5 else none
  | _ => none

/-- Whether the tokens begin with word tokens folding to the parts, in order. -/
def startsWithParts : List Tok → List String → Bool
  | _, [] => true
  | .word x _ :: ts, p :: ps => fold x == p && startsWithParts ts ps
  | _, _ => false

/-- The tokens after a word token at the start of the tokens that are its gloss's mark and gloss (2.6, R7):
the longest matching gloss of a sense of `D` with the token as a headword token, with `)` after it for
`(`; 0 when no mark follows or no gloss of the head matches. A shorter comma gloss may prefix a longer
one, so stopping at the shorter one would expose the rest of the longer gloss as body words. -/
def glossAfter (D : Dictionary) : List Tok → Nat
  | .word h _ :: rest =>
    match glossMark rest with
    | none => 0
    | some m =>
      let lens := (D.senses.filter fun s => s.headwordTokens.contains (fold h)).filterMap fun s =>
        let ps := partsOf s.gloss
        let after := rest.drop m
        if startsWithParts after ps && (m != 2 || match after.drop ps.length with
            | .punct ")" _ _ :: _ => true
            | _ => false) then some (m + ps.length) else none
      match lens with
      | [] => 0
      | n :: ns => ns.foldl max n
  | _ => 0

/-- The tokens of a sentence from index `i`, with their indices, skipping the mark and gloss after a
glossed head. -/
def unglossedFrom (D : Dictionary) (i : Nat) : List Tok → List (Nat × Tok)
  | [] => []
  | t :: ts => (i, t) :: unglossedFrom D (i + 1 + glossAfter D (t :: ts)) (ts.drop (glossAfter D (t :: ts)))
termination_by ts => ts.length
decreasing_by simp only [List.length_drop, List.length_cons]; omega

/-- The tokens of a sentence that are read as written, with their indices: every token but the mark and
the gloss after a glossed head (2.6, R7). A word inside a gloss is not an occurrence of that word. -/
def unglossed (D : Dictionary) (w : List Tok) : List (Nat × Tok) := unglossedFrom D 0 w

/-- The words of `D`, in `D`'s order, one of whose senses has a headword token equal to the folded text
of some word token of `sents` outside a gloss. -/
def usedWords (D : Dictionary) (sents : List (List Tok)) : List String :=
  let toks := sents.flatMap fun w => (unglossed D w).filterMap fun
    | (_, .word x _) => some (fold x)
    | _ => none
  D.words.filter fun w => (D.sensesOf w).any fun s => s.headwordTokens.any toks.contains

structure Projection where
  env : Env
  lexicon : Lexicon
  envJson : Json
  /-- Predicate id, sense, is default. -/
  map : List (String × Sense × Bool)
  deriving Repr

def Projection.wordOf (P : Projection) (id : String) : Option String :=
  (P.map.find? (·.1 == id)).map (·.2.1.word)

/-- Python's cap on the sorts of an environment (`ve/limits.py`). -/
def maxSorts : Nat := 32
/-- Python's cap on the predicates of an environment (`ve/limits.py`). -/
def maxPredicates : Nat := 256

/-- The senses of the used words of `D`, in `D`'s order. -/
def projectedSenses (D : Dictionary) (used : List String) : List Sense :=
  (D.words.filter used.contains).flatMap D.sensesOf

/-- Whether `s` is its word's default under `A`. -/
def isDefaultIn (D : Dictionary) (A : Assignment) (s : Sense) : Bool := defaultOf D A s.word == some s

/-- The pack sorts the environment does not have. -/
def freshSorts (D : Dictionary) (E : Env) : List PackSort := D.sorts.filter fun t => !E.sorts.any (·.name == t.name)

/-- The pack sorts the environment has. -/
def sharedSorts (D : Dictionary) (E : Env) : List PackSort := D.sorts.filter fun t => E.sorts.any (·.name == t.name)

/-- An object field set; another value unchanged. -/
def setField (j : Json) (k : String) (v : Json) : Json :=
  match j with
  | .obj kvs => .obj (kvs.insert k v)
  | _ => j

/-- The environment JSON with entries added under `vocabulary.<kind>`. -/
def addVocabulary (j : Json) (kind : String) (entries : List (String × Json)) : Json :=
  let vocab := j.getObjValD "vocabulary"
  setField j "vocabulary" (setField vocab kind (entries.foldl (fun o (k, v) => setField o k v) (vocab.getObjValD kind)))

/-- A list sorted by its symbols, stably. -/
def bySymbol {β : Type} (l : List (String × β)) : List (String × β) := l.mergeSort fun a b => a.1 ≤ b.1

/-- The projected environment JSON (2.5): the fresh sorts and one predicate per sense. A declared negative
is not written there. -/
def projectedJson (D : Dictionary) (A : Assignment) (E : Env) (used : List String) : Json :=
  let senses := projectedSenses D used
  addVocabulary
    (addVocabulary E.source "sorts" ((freshSorts D E).map fun t => (t.name, Json.mkObj
      [("description", .str t.description),
       ("verbalisation", Json.mkObj [("singular", .str t.noun), ("plural", .str t.plural)])])))
    "predicates" (senses.map fun s => (s.symbol, Json.mkObj ([("arguments", toJson s.kinds),
      ("description", .str s.description), ("verbalisation", .str (s.selectedWording (isDefaultIn D A s)))] ++
      match s.automaticNegative (isDefaultIn D A s) with
      | some n => [("negative_verbalisation", .str n)]
      | none => [])))

/-- The aliases of the projected senses, with their symbols. -/
def projectedAliases (D : Dictionary) (A : Assignment) (used : List String) : List (String × String × Bool) :=
  (projectedSenses D used).flatMap fun s => (s.aliases (isDefaultIn D A s)).map fun (a, neg) => (s.symbol, a, neg)

/-- The predicate declaration of a projected sense. -/
def senseDecl (D : Dictionary) (A : Assignment) (s : Sense) : PredDecl :=
  { name := s.symbol, arity := s.arity, wording := some (s.selectedWording (isDefaultIn D A s)),
    negative := s.automaticNegative (isDefaultIn D A s), args := s.kinds }

/-- The projected environment (2.5). -/
def projectedEnv (D : Dictionary) (A : Assignment) (E : Env) (used : List String) : Env :=
  let senses := projectedSenses D used
  { E with
    sorts := E.sorts ++ (freshSorts D E).map (fun t => { name := t.name, noun := some t.noun }),
    predicates := E.predicates ++ senses.map (senseDecl D A),
    forms := { E.forms with
      negatives := E.forms.negatives ++ senses.filterMap (fun s => (s.fixedNegative (isDefaultIn D A s)).map (s.symbol, ·)),
      aliases := E.forms.aliases ++ projectedAliases D A used },
    source := projectedJson D A E used }

/-- The projected lexicon (2.5): `L`'s entries and the dictionary's, each list sorted by symbol. -/
def projectedLexicon (D : Dictionary) (A : Assignment) (E : Env) (L : Lexicon) (used : List String) : Lexicon :=
  let senses := projectedSenses D used
  { nouns := bySymbol (L.nouns ++ (freshSorts D E).map fun t => (t.name, t.noun)),
    letters := bySymbol (L.letters ++ (freshSorts D E).map fun t => (t.name, t.letter)),
    wordings := bySymbol (L.wordings ++ senses.map fun s => (s.symbol, s.selectedWording (isDefaultIn D A s))),
    negatives := bySymbol (L.negatives ++
      senses.filterMap fun s => (s.selectedNegative (isDefaultIn D A s)).map (s.symbol, ·)),
    aliases := bySymbol (L.aliases ++ projectedAliases D A used),
    spellings := L.spellings }

/-- The projection that step 6 checks. -/
def projectionOf (D : Dictionary) (A : Assignment) (E : Env) (L : Lexicon) (used : List String) : Projection :=
  ⟨projectedEnv D A E used, projectedLexicon D A E L used, projectedJson D A E used,
   (projectedSenses D used).map fun s => (s.symbol, s, isDefaultIn D A s)⟩

/-- Steps 1 to 5 of 2.5: the shared sorts' nouns and letters, the fresh sorts' letters, the names, the
counts. -/
def preCheck (D : Dictionary) (E : Env) (L : Lexicon) (used : List String) : Option SenseFault :=
  let shared := sharedSorts D E
  let fresh := freshSorts D E
  let senses := projectedSenses D used
  let docNames := E.sorts.map (·.name) ++ E.predicates.map (·.name) ++ E.constants.map (·.name)
  match shared.find? fun t => (L.nouns.lookup t.name).map wordingKey != some (wordingKey t.noun) with
  | some t => some (.collision "sort" t.name "")
  | none =>
  match shared.find? fun t => L.letters.lookup t.name != some t.letter with
  | some t => some (.collision "letter" t.letter t.name)
  | none =>
  match fresh.find? fun t => L.letters.any (·.2 == t.letter) with
  | some t => some (.collision "letter" t.letter t.name)
  | none =>
  match (fresh.map (·.name) ++ senses.map (·.symbol)).find? docNames.contains with
  | some n => some (.collision "name" n "")
  | none =>
  if E.sorts.length + fresh.length > maxSorts then some (.limit "sorts")
  else if E.predicates.length + senses.length > maxPredicates then some (.limit "predicates")
  else none

/-- The colliding pairs of a lexicon in S2's V4 order (2.5, step 6): for each selection (wordings,
negatives, aliases, nouns, spellings), each other symbol that declares or selects a text with its
`wordingKey`, as the selection's kind and name, the other's kind and name, and the selection's text.
S2's `owners` and `selections`, which are local to `Lexicon.failures`, with no overlay. -/
def clashes (E : Env) (L : Lexicon) : List (String × String × String × String × String) :=
  let O : Overlay := {}
  let F := E.forms
  let own (text : Option String) (kind name : String) : List (String × String × String) :=
    match text with
    | some t => if t.isEmpty then [] else [(wordingKey t, kind, name)]
    | none => []
  let owners :=
    (E.predicates.map (·.name)).flatMap (fun p => own (E.declaredWording O p) "predicate" p ++
      own (E.declaredNegative O p) "predicate" p ++ own (F.wordings.lookup p) "predicate" p ++
      ((F.aliases.filter (·.1 == p)).flatMap fun a => own (some a.2.1) "predicate" p)) ++
    (E.sorts.map (·.name)).flatMap (fun s => own (E.declaredNoun O s) "sort" s ++ own (L.nouns.lookup s) "sort" s) ++
    (E.constants.map (·.name)).flatMap (fun c => own (E.declaredSpelling O c) "constant" c ++
      own (L.spellings.lookup c) "constant" c)
  let selections : List (String × String × String) :=
    L.wordings.map (fun (p, w) => (w, "predicate", p)) ++ L.negatives.map (fun (p, w) => (w, "predicate", p)) ++
    L.aliases.map (fun (p, w, _) => (w, "predicate", p)) ++ L.nouns.map (fun (s, n) => (n, "sort", s)) ++
    L.spellings.map (fun (c, sp) => (sp, "constant", c))
  (selections.flatMap fun (text, kind, name) =>
    ((owners.filter fun (k2, kind2, name2) => k2 == wordingKey text && !(kind2 == kind && name2 == name)).map
      fun (_, kind2, name2) => (kind, name, kind2, name2, text))).eraseDups

/-- The fault of step 6 for a refused projection: the first colliding pair with one side a symbol of the
document and the other a sense symbol or a fresh sort, else the first pair; with no pair, the first failure
of S2's conditions. -/
def pairFault (D : Dictionary) (E : Env) (used : List String) (P : Projection) (fs : List Failure) : SenseFault :=
  let docNames := E.sorts.map (·.name) ++ E.predicates.map (·.name) ++ E.constants.map (·.name)
  let ours := (projectedSenses D used).map (·.symbol) ++ (freshSorts D E).map (·.name)
  let cs := clashes P.env P.lexicon
  let oriented := cs.findSome? fun (k, n, k2, n2, _) =>
    if docNames.contains n && ours.contains n2 then some (SenseFault.collision k n n2)
    else if docNames.contains n2 && ours.contains n then some (SenseFault.collision k2 n2 n)
    else none
  match oriented with
  | some f => f
  | none =>
    match cs with
    | (k, n, _, n2, _) :: _ => .collision k n n2
    | [] =>
      match fs with
      | (cond, _, name) :: _ => .collision cond name ""
      | [] => .collision "" "" ""

def project (D : Dictionary) (A : Assignment) (E : Env) (L : Lexicon) (used : List String) :
    Except SenseFault Projection :=
  match preCheck D E L used with
  | some f => .error f
  | none =>
    match (projectionOf D A E L used).lexicon.failures (projectionOf D A E L used).env {} with
    | [] => .ok (projectionOf D A E L used)
    | fs => .error (pairFault D E used (projectionOf D A E L used) fs)

/-- The `wordingKey`s of what the document declares or selects: nouns and spellings. -/
def docKeys (E : Env) (L : Lexicon) : List String :=
  ((E.sorts.filterMap (·.noun)) ++ (E.constants.filterMap (·.display)) ++ L.nouns.map (·.2) ++
    L.spellings.map (·.2)).map wordingKey

/-- The `wordingKey`s of every form of every sense and of every pack noun. -/
def dictKeys (D : Dictionary) : List String :=
  ((D.senses.flatMap fun s => s.bareForms ++ s.decoratedForms) ++ D.sorts.map (·.noun)).map wordingKey

/-! ## The statements of spec 5.3 -/

theorem project_eq {D : Dictionary} {A : Assignment} {E : Env} {L : Lexicon} {used : List String}
    {P : Projection} (h : project D A E L used = .ok P) :
    preCheck D E L used = none ∧ P = projectionOf D A E L used ∧ P.lexicon.failures P.env {} = [] := by
  unfold project at h
  split at h
  · cases h
  · rename_i hp
    split at h
    · rename_i hf
      cases h
      exact ⟨hp, rfl, hf⟩
    · cases h

theorem project_valid : ∀ (D : Dictionary) (A : Assignment) (E : Env) (L : Lexicon) (used : List String)
    (P : Projection),
  project D A E L used = .ok P → P.lexicon.valid P.env {} = true := by
  intro D A E L used P h
  exact (valid_iff_no_failure _ _ _).mpr (project_eq h).2.2

/-- The proposed statement of spec 5.3 that `project` is total on its domain (F4, Q13). It is not proved;
the per-request check of `project` is the guarantee (docs/spec/senses-lean-report.md). -/
def project_total : Prop := ∀ (D : Dictionary) (A : Assignment) (E : Env) (L : Lexicon) (used : List String),
  D.wf (E.sorts.map (·.name)) = true → A.wf D = true → L.valid E {} = true →
  E.predicates = [] → E.forms.negatives = [] → E.forms.aliases = [] →
  (∀ n ∈ E.sorts.map (·.name) ++ E.constants.map (·.name),
    n ∉ D.sorts.map (·.name) ∧ n ∉ D.senses.map (·.symbol)) →
  (∀ k ∈ docKeys E L, k ∉ dictKeys D) →
  (∀ x ∈ L.letters, ∀ t ∈ D.sorts, x.2 ≠ t.letter) →
  E.sorts.length + D.sorts.length ≤ maxSorts →
  (D.senses.filter (·.word ∈ used)).length ≤ maxPredicates →
  ∃ P, project D A E L used = .ok P

theorem mem_projectedSenses {D : Dictionary} {used used2 : List String} (hu : ∀ w ∈ used, w ∈ used2)
    {s : Sense} (h : s ∈ projectedSenses D used) : s ∈ projectedSenses D used2 := by
  unfold projectedSenses at *
  simp only [List.mem_flatMap, List.mem_filter, List.contains_iff_mem] at *
  obtain ⟨w, ⟨hw, hc⟩, hs⟩ := h
  exact ⟨w, ⟨hw, by simpa using hu w (by simpa using hc)⟩, hs⟩

theorem mem_projectedAliases {D : Dictionary} {A : Assignment} {used used2 : List String}
    (hu : ∀ w ∈ used, w ∈ used2) {x : String × String × Bool} (h : x ∈ projectedAliases D A used) :
    x ∈ projectedAliases D A used2 := by
  unfold projectedAliases at *
  simp only [List.mem_flatMap] at *
  obtain ⟨s, hs, hx⟩ := h
  exact ⟨s, mem_projectedSenses hu hs, hx⟩

theorem project_extends : ∀ (D : Dictionary) (A : Assignment) (E : Env) (L : Lexicon)
    (used used2 : List String) (P P2 : Projection),
  E.profiles = ["relational-fol@0"] → (∀ w ∈ used, w ∈ used2) →
  project D A E L used = .ok P → project D A E L used2 = .ok P2 →
  P.lexicon.valid P.env {} = true → P2.lexicon.valid P2.env {} = true →
  Extends P.env {} P.lexicon P2.env {} P2.lexicon := by
  intro D A E L used used2 P P2 _ hu h h2 hv hv2
  obtain ⟨_, rfl, _⟩ := project_eq h
  obtain ⟨_, rfl, _⟩ := project_eq h2
  refine ⟨⟨rfl, rfl, ?_, ?_, ?_⟩, ⟨?_, ?_, ?_, ?_, ?_, ?_⟩, hv, hv2⟩
  · intro s hs
    exact ⟨s, hs, rfl⟩
  · intro p hp
    simp only [projectionOf, projectedEnv, List.mem_append, List.mem_map] at hp ⊢
    rcases hp with hp | ⟨s, hs, rfl⟩
    · exact ⟨p, Or.inl hp, rfl, rfl, rfl, rfl, rfl⟩
    · exact ⟨senseDecl D A s, Or.inr ⟨s, mem_projectedSenses hu hs, rfl⟩, rfl, rfl, rfl, rfl, rfl⟩
  · intro c hc
    exact ⟨c, hc, rfl, rfl⟩
  · intro x hx
    exact hx
  · intro x hx
    exact hx
  · intro x hx
    simp only [projectionOf, projectedLexicon, bySymbol, List.mem_mergeSort, List.mem_append, List.mem_map] at hx ⊢
    rcases hx with hx | ⟨s, hs, rfl⟩
    · exact Or.inl hx
    · exact Or.inr ⟨s, mem_projectedSenses hu hs, rfl⟩
  · intro x hx
    simp only [projectionOf, projectedLexicon, bySymbol, List.mem_mergeSort, List.mem_append,
      List.mem_filterMap] at hx ⊢
    rcases hx with hx | ⟨s, hs, e⟩
    · exact Or.inl hx
    · exact Or.inr ⟨s, mem_projectedSenses hu hs, e⟩
  · intro x hx
    simp only [projectionOf, projectedLexicon, bySymbol, List.mem_mergeSort, List.mem_append] at hx ⊢
    rcases hx with hx | hx
    · exact Or.inl hx
    · exact Or.inr (mem_projectedAliases hu hx)
  · intro x hx
    exact hx

end VE.Senses
