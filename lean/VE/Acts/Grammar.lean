import VE.Acts.Read
import VE.Acts.LexicalProofs

/-! The act grammar's rule table (docs/spec/act-phrases.md 5.2) and its well-formedness `grammar_wf` (5.6).

`schema V` writes the rules of 5.2 over named nonterminals, and `build` numbers them and closes each nonterminal that
has no rule with `X → never`. The nonterminals are structured (`NT`, with frame `h`'s in `FNT`), and each constructor
has a rank (`NT.rank`), so condition W3 holds by construction: a rule's first nonterminal has a lower rank than its
left side. Each rule has a kind: the two rules of each edge (5.2's "two derivations") are alike but for theirs, the
near end's then `all` (2.4), and `modifier_edges` says where they stand; every other rule is `shape`.
-/

namespace VE.Acts
open Lexical (Tok)

/-- The cores of 5.2: `CB` bare (the head only), `CO` with its own material, `CL` the last item of a full list, `CR`
the last item of a shared-object list. A coordination's tail is named by its last item's pattern: `TM:B` by `bare`,
`TM:F` by `own`, `TM:R` by `rnr`. -/
inductive Core | bare | own | last | rnr
  deriving DecidableEq, Repr

/-- The nonterminals of frame `h` (5.2, "Per frame h"); those of an argument marker `m` carry it, and `LST m split` is
5.2's list `FSh:m*` (`split`) or `FNh:m°`. -/
inductive FNT
  | HD | WR | FL | PL | PT | O | OS | EE | ER | NM | ERN | OWNM | TE | TR | LFM | RE | REt | REP | RX | RR | RM
  | SPL | PX | PO | SM | MEL | MGT | MG
  | AR (m : String) | RL (m : String) | RT (m : String) | OL (m : String) | LST (m : String) (split : Bool)
  deriving DecidableEq, Repr

/-- The nonterminals of 5.2: `MK m` a marker's words; `C c` the cores; `F1 own c`, `L own c` and `T own c` a
coordination's first items, later items and tails (`own`: every item has its own function word, 5.2's `F1O`, `LO`,
`TO`; otherwise `F1S`, `LS`, `TS`); `F h x` frame `h`'s nonterminal `x`. -/
inductive NT
  | S | J | FW | TOK | ADVO | ADVSO | E1X | E1S | SINGLE | SC | COORD
  | MK (m : String) | C (c : Core) | F1 (own : Bool) (c : Core) | L (own : Bool) (c : Core) | T (own : Bool) (c : Core)
  | F (h : Nat) (x : FNT)
  deriving DecidableEq, Repr

/-- A rank per nonterminal: higher than the rank of every nonterminal that starts one of its rules (W3). -/
def NT.rank : NT → Nat
  | .ADVSO | .E1S | .SC | .C _ | .T _ _ | .F _ .FL | .F _ .PT | .F _ .TE | .F _ .RE | .F _ .REt | .F _ .MEL
  | .F _ .MGT | .F _ (.AR _) | .F _ (.RT _) | .F _ (.OL _) => 1
  | .SINGLE | .F1 _ _ | .L _ _ | .F _ .PL | .F _ .TR | .F _ .REP | .F _ .MG | .F _ (.RL _) => 2
  | .COORD | .F _ .O | .F _ .OS | .F _ (.LST _ _) => 3
  | .F _ .EE | .F _ .NM | .F _ .RX | .F _ .SPL | .F _ .PX => 4
  | .F _ .ER | .F _ .ERN | .F _ .RR | .F _ .PO => 5
  | .F _ .OWNM | .F _ .LFM | .F _ .RM => 6
  | .F _ .SM => 7
  | _ => 0

/-- A symbol of a right side: a terminal or a named nonterminal. -/
inductive RSym | t (a : Term) | n (x : NT)
  deriving DecidableEq, Repr

/-- Where an edge rule reads its modifier (2.4): over the first item, the last item (or part), or all of them; there
is no middle. -/
inductive Attach | first | last | all
  deriving DecidableEq, Repr
/-- A rule's kind as the table writes it: an edge's attachment (5.2's two derivations), or `shape`, whose action the
meaning reads from the rule's sides (5.3). -/
inductive Kind | shape | edge (a : Attach)
  deriving DecidableEq, Repr

/-- A rule over named nonterminals, with its kind. -/
structure RuleS where
  lhs : NT
  rhs : List RSym
  kind : Kind
  deriving DecidableEq, Repr

/-- The words `ws`, each as a `kw` terminal. -/
def kwSyms (ws : List String) : List RSym := ws.map (fun w => .t (.kw w))
/-- `X → x | x X`: one or more `x`. -/
def many1 (X : NT) (x : RSym) : List RuleS := [⟨X, [x], .shape⟩, ⟨X, [x, .n X], .shape⟩]
/-- A list's tail (`TM:B`, `PTh`, `RTh:m`, `MGTh`): a join word and a last member, with a comma before the join word
or not, or a comma, a middle member and the rest. -/
def tail (X : NT) (lasts : List RSym) (mid : RSym) : List RuleS :=
  lasts.map (fun x => ⟨X, [.n .J, x], .shape⟩) ++ lasts.map (fun x => ⟨X, [.t .comma, .n .J, x], .shape⟩) ++
    [⟨X, [.t .comma, mid, .n X], .shape⟩]
/-- Function words and adverbs before a core `c` (5.2's `SINGLE`, `F1S:c`, `F1O:c`, `LO:c`): adverbs `a` may stand
before the first function word, and after it `a` when the function words are shared, `ADVSO` when they are `own`. -/
def items (X a c : NT) (own : Bool) : List RuleS :=
  ((if own then [[.FW, c], [a, .FW, c], [.FW, .ADVSO, c], [a, .FW, .ADVSO, c]]
    else [[c], [a, c], [.FW, c], [a, .FW, c], [.FW, a, c], [a, .FW, a, c]]).map (·.map .n)).map (⟨X, ·, .shape⟩)

/-- Start, items and coordinations (5.2), with one `MK m` per marker of any frame. -/
def globalRules (V : Vocab) : List RuleS :=
  let adv : RSym := .t (.adv V.adverbs)
  [⟨.S, [.t .subj, .n .SINGLE], .shape⟩, ⟨.S, [.t .subj, .n .COORD], .shape⟩, ⟨.J, kwSyms ["and"], .shape⟩,
    ⟨.J, kwSyms ["or"], .shape⟩, ⟨.J, kwSyms ["nor"], .shape⟩, ⟨.FW, kwSyms ["to"], .shape⟩,
    ⟨.FW, kwSyms ["be"], .shape⟩, ⟨.FW, kwSyms ["to", "be"], .shape⟩, ⟨.TOK, [.t .slot], .shape⟩,
    ⟨.TOK, [.t .fixed], .shape⟩, ⟨.ADVO, [adv], .shape⟩] ++
  -- the first item's prefix edge: over the first item, or over all
  [⟨.E1X, [adv], .edge .first⟩, ⟨.E1X, [adv], .edge .all⟩] ++
  many1 .ADVSO (.n .ADVO) ++ many1 .E1S (.n .E1X) ++ items .SINGLE .ADVSO .SC false ++
  [true, false].flatMap (fun own =>
    [Core.bare, .own].flatMap (fun c => items (.F1 own c) .E1S (.C c) own) ++
    [Core.bare, .own, .last, .rnr].flatMap (fun c =>
      if own then items (.L true c) .ADVSO (.C c) true
      else [⟨.L false c, [.n (.C c)], .shape⟩, ⟨.L false c, [.n .ADVSO, .n (.C c)], .shape⟩]) ++
    [⟨.COORD, [.n (.F1 own .bare), .n (.T own .bare)], .shape⟩, ⟨.COORD, [.n (.F1 own .bare), .n (.T own .rnr)], .shape⟩,
      ⟨.COORD, [.n (.F1 own .own), .n (.T own .own)], .shape⟩] ++
    tail (.T own .bare) [.n (.L own .bare)] (.n (.L own .bare)) ++
    tail (.T own .rnr) [.n (.L own .rnr)] (.n (.L own .bare)) ++
    tail (.T own .own) [.n (.L own .last), .n (.L own .bare)] (.n (.L own .own))) ++
  (firsts ((V.frames.flatMap (fun f => f.markers ++ f.mods)).filter (· ≠ ""))).map
    (fun m => ⟨.MK m, kwSyms (wordsOf m), .shape⟩)

/-- The filler words' exclusions for frame `f` (1.4): the join and function words, the adverbs, the first words of
`f`'s markers and modifier markers, and the first words of all heads. -/
def fillExcl (V : Vocab) (f : Frame) : List String :=
  ["and", "or", "nor", "to", "be"] ++ V.adverbs ++ (f.markers ++ f.mods).filterMap (fun m => (wordsOf m).head?) ++
    V.frames.filterMap (·.head.head?)

/-- The rules of frame `f`, numbered `h` (5.2, "Per frame h"). -/
def frameRules (V : Vocab) (h : Nat) (f : Frame) : List RuleS :=
  let x (y : FNT) : RSym := .n (.F h y)
  let r (y : FNT) (rhs : List RSym) : RuleS := ⟨.F h y, rhs, .shape⟩
  let adv : RSym := .t (.adv V.adverbs)
  let obj := f.markers.contains ""
  let objSplit := obj && f.split.contains ""
  let ms := f.markers.filter (· ≠ "")
  let plain := ms.filter (!f.split.contains ·)
  -- the arguments and not-split lists of `y`; a trailing edge of `y` (an adverb or a modifier, each over the last
  -- item or part, or over all)
  let args (y : FNT) : List RuleS := ms.map (fun m => r y [x (.AR m)]) ++ plain.map (fun m => r y [x (.LST m false)])
  let two (y : FNT) (rhs : List RSym) : List RuleS := [⟨.F h y, rhs, .edge .last⟩, ⟨.F h y, rhs, .edge .all⟩]
  let edge (y : FNT) (fl : RSym) : List RuleS := two y [adv] ++ f.mods.flatMap (fun m => two y [.n (.MK m), fl])
  [r .HD (kwSyms f.head), ⟨.C .bare, [x .HD], .shape⟩, ⟨.C .own, [x .HD, x .OWNM], .shape⟩,
    ⟨.C .last, [x .HD, x .LFM], .shape⟩, ⟨.C .rnr, [x .HD, x .RM], .shape⟩, ⟨.SC, [x .HD], .shape⟩,
    ⟨.SC, [x .HD, x .SM], .shape⟩] ++
  many1 (.F h .WR) (.t (.fill (fillExcl V f))) ++ [r .FL [x .WR], r .FL [.n .TOK], r .PL [x .FL, x .PT]] ++
  tail (.F h .PT) [x .FL] (x .FL) ++
  ms.flatMap (fun m => [r (.AR m) [.n (.MK m), x .FL], r (.RL m) [x (.AR m), x (.RT m)]] ++
    tail (.F h (.RT m)) [x (.AR m)] (x (.AR m)) ++ [r (.OL m) [.n (.MK m), x .PL],
    r (.LST m (f.split.contains m)) [x (.RL m)], r (.LST m (f.split.contains m)) [x (.OL m)]]) ++
  (if obj then [r .O [x .FL], if objSplit then r .OS [x .PL] else r .O [x .PL]] else []) ++
  -- own material: arguments, lists, adverbs and modifiers of the item's own
  args .EE ++ [r .EE [adv]] ++ f.mods.map (fun m => r .EE [.n (.MK m), x .FL]) ++ many1 (.F h .ER) (x .EE) ++
  args .NM ++ [r .ERN [x .NM], r .ERN [x .EE, x .ERN]] ++
  (if obj then [r .OWNM [x .O], r .OWNM [x .O, x .ER]] else [r .OWNM [x .ER]]) ++
  -- the last item of a full list: trailing edges
  edge .TE (x .FL) ++ many1 (.F h .TR) (x .TE) ++
  (if obj then [r .LFM [x .O], r .LFM [x .O, x .ERN], r .LFM [x .O, x .TR], r .LFM [x .O, x .ERN, x .TR]]
   else [r .LFM [x .ERN], r .LFM [x .TR], r .LFM [x .ERN, x .TR]]) ++
  -- the last item of a shared-object list: edges, the object after modifiers ending with a token
  edge .RE (x .FL) ++ edge .REt (.n .TOK) ++ [r .REP [x .REt], r .REP [x .RE, x .REP]] ++
  args .RX ++ [r .RX [x .RE]] ++ many1 (.F h .RR) (x .RX) ++
  (if obj then [r .RM [x .O], r .RM [x .O, x .RR], r .RM [x .REP, x .O], r .RM [x .REP, x .O, x .RR]]
   else [r .RM [x .RR]]) ++
  -- a single item: one split construct, then shared arguments and edges
  (ms.filter f.split.contains).map (fun m => r .SPL [x (.LST m true)]) ++ [r .SPL [x .MG]] ++
  args .PX ++ edge .PX (x .FL) ++ many1 (.F h .PO) (x .PX) ++
  (if obj then [r .SM [x .OWNM], r .SM [x .OWNM, x .SPL], r .SM [x .OWNM, x .SPL, x .PO]] ++
     (if objSplit then [r .SM [x .OS], r .SM [x .OS, x .PO]] else [])
   else [r .SM [x .ER], r .SM [x .ER, x .SPL], r .SM [x .ER, x .SPL, x .PO], r .SM [x .SPL], r .SM [x .SPL, x .PO]]) ++
  -- joined modifiers
  [r .MEL [adv]] ++ f.mods.map (fun m => r .MEL [.n (.MK m), x .FL]) ++ tail (.F h .MGT) [x .MEL] (x .MEL) ++
  [r .MG [x .MEL, x .MGT]]

/-- The rule table of 5.2. -/
def schema (V : Vocab) : List RuleS :=
  globalRules V ++ V.frames.zipIdx.flatMap (fun (f, h) => frameRules V h f)

/-- The nonterminal a symbol names. -/
def RSym.nt? : RSym → Option NT
  | .n x => some x
  | .t _ => none

/-- `rs` with `X → never` for each nonterminal of a right side that has no rule (5.2, last paragraph). -/
def closed (rs : List RuleS) : List RuleS :=
  rs ++ ((firsts (rs.flatMap (·.rhs.filterMap RSym.nt?))).filter (fun x => !rs.any (·.lhs == x))).map
    (⟨·, [.t .never], .shape⟩)

/-- Numbers the nonterminals of `rs` in order of first occurrence as a left side; each has its constructor's rank. -/
def build (rs : List RuleS) : VE.Grammar.Grammar Term :=
  let names := firsts (rs.map (·.lhs))
  let sym : RSym → VE.Grammar.Sym Term
    | .n x => .n (names.idxOf x)
    | .t a => .t a
  { rules := (rs.map (fun r => ({ lhs := names.idxOf r.lhs, rhs := r.rhs.map sym, act := 0, tag := "" } :
      VE.Grammar.Rule Term))).toArray, start := names.idxOf .S, rank := (names.map NT.rank).toArray }

/-- The act grammar of a vocabulary (5.2). -/
def grammar (V : Vocab) : VE.Grammar.Grammar Term := build (closed (schema V))

/-! ### `grammar_wf` (5.6) -/

/-- What `framesOk` gives the rule table: every head has a word, and so does every marker other than `""`. -/
theorem framesOk_words {V : Vocab} (h : framesOk V = true) : ∀ f ∈ V.frames,
    f.head ≠ [] ∧ ∀ m ∈ f.markers ++ f.mods, m ≠ "" → wordsOf m ≠ [] := by
  have h' : checkVocab V = .ok () := by
    unfold framesOk at h; cases hc : checkVocab V <;> simp_all [Except.isOk, Except.toBool]
  unfold checkVocab at h'
  simp only [bind, Except.bind, pure, Except.pure] at h'
  split at h'; · cases h'
  split at h'; · cases h'
  next hany =>
  iterate 9 (split at h'; · cases h')
  split at h'; · cases h'
  next hl =>
  intro f hf
  refine ⟨?_, ?_⟩
  · intro he; simp only [List.any_eq_true] at hany; exact hany ⟨f, hf, by simp [he]⟩
  · intro m hm hne
    have := Lexical.forIn_ok hl (by intro x; split <;> simp) f hf
    split at this
    · cases this
    next hn =>
    cases hx : List.find? (fun m => m != " ".intercalate (wordsOf m) || wordsOf m == [])
        ((f.markers ++ f.mods).filter (· ≠ "")) with
    | some w => exact (hn w hx).elim
    | none =>
      intro hw
      have := List.find?_eq_none.mp hx m (List.mem_filter.mpr ⟨hm, by simpa using hne⟩)
      simp [hw] at this

/-- A rule's right side is non-empty, and its first nonterminal, if any, ranks below its left side (W2, W3). -/
def RuleS.ok (r : RuleS) : Bool :=
  match r.rhs with
  | [] => false
  | .n B :: _ => decide (B.rank < r.lhs.rank)
  | .t _ :: _ => true

theorem kwSyms_ok {X : NT} {ws : List String} {k : Kind} (h : ws ≠ []) : RuleS.ok ⟨X, kwSyms ws, k⟩ = true := by
  cases ws with
  | nil => exact absurd rfl h
  | cons w ws => rfl

theorem frameRules_ok (V : Vocab) (h : Nat) {f : Frame} (hh : f.head ≠ []) : (frameRules V h f).all RuleS.ok = true := by
  obtain ⟨w, ws, hw⟩ : ∃ w ws, f.head = w :: ws := by cases hx : f.head <;> simp_all
  by_cases ho : "" ∈ f.markers <;> by_cases hs : "" ∈ f.split <;>
    simp [frameRules, many1, tail, kwSyms, hw, ho, hs, RuleS.ok, NT.rank]

theorem globalRules_ok {V : Vocab} (hm : ∀ f ∈ V.frames, ∀ m ∈ f.markers ++ f.mods, m ≠ "" → wordsOf m ≠ []) :
    (globalRules V).all RuleS.ok = true := by
  simp only [globalRules, items, many1, tail, List.all_append, List.all_cons, List.all_nil, List.all_map,
    List.all_flatMap, Bool.and_eq_true, List.all_eq_true, mem_firsts, List.mem_filter, List.mem_flatMap]
  refine ⟨by simp [RuleS.ok, NT.rank, kwSyms], ?_⟩
  intro m ⟨⟨f, hf, hm'⟩, hne⟩
  exact kwSyms_ok (hm f hf m hm' (by simpa using hne))

theorem schema_ok {V : Vocab} (h : framesOk V = true) : (schema V).all RuleS.ok = true := by
  have hw := framesOk_words h
  simp only [schema, List.all_append, List.all_flatMap, Bool.and_eq_true, List.all_eq_true]
  refine ⟨List.all_eq_true.mp (globalRules_ok (fun f hf => (hw f hf).2)), ?_⟩
  intro ⟨f, i⟩ hf
  exact List.all_eq_true.mp (frameRules_ok V i (hw f (List.fst_mem_of_mem_zipIdx hf)).1)

theorem getElem?_map_idxOf {β : Type} (f : NT → β) {x : NT} : ∀ {l : List NT}, x ∈ l →
    (l.map f)[l.idxOf x]? = some (f x)
  | [], h => by cases h
  | y :: ys, h => by
    rw [List.idxOf_cons]
    by_cases hy : y = x
    · subst hy; simp
    · have hx : x ∈ ys := by rcases List.mem_cons.mp h with h | h; exact absurd h.symm hy; exact h
      have hb : (y == x) = false := by simpa using hy
      simp [hb, getElem?_map_idxOf f hx]

/-- `build` numbers any rule list into a well-formed grammar when each rule is `ok`, every nonterminal of a right
side has a rule, and so does the start symbol. -/
theorem build_wf {rs : List RuleS} (hok : ∀ r ∈ rs, r.ok = true)
    (hcl : ∀ r ∈ rs, ∀ x, .n x ∈ r.rhs → x ∈ rs.map (·.lhs)) (hS : NT.S ∈ rs.map (·.lhs)) :
    (build rs).wf = true := by
  have lt {x : NT} (hx : x ∈ rs.map (·.lhs)) : (firsts (rs.map (·.lhs))).idxOf x < (firsts (rs.map (·.lhs))).length :=
    List.idxOf_lt_length_of_mem (mem_firsts.mpr hx)
  have rk {x : NT} (hx : x ∈ rs.map (·.lhs)) :
      ((firsts (rs.map (·.lhs))).map NT.rank).toArray.getD ((firsts (rs.map (·.lhs))).idxOf x) 0 = x.rank := by
    have := getElem?_map_idxOf NT.rank (mem_firsts.mpr hx)
    rw [Array.getD_eq_getD_getElem?, List.getElem?_toArray, this]; rfl
  simp only [build, VE.Grammar.Grammar.wf, List.all_toArray]
  simp only [Bool.and_eq_true, decide_eq_true_eq, List.size_toArray, List.length_map, List.all_map, List.all_eq_true,
    Function.comp]
  refine ⟨lt hS, fun r hr => ?_⟩
  have hl : r.lhs ∈ rs.map (·.lhs) := List.mem_map_of_mem hr
  have ho := hok r hr
  simp only [VE.Grammar.Rule.wf, Bool.and_eq_true, decide_eq_true_eq, List.size_toArray, List.length_map]
  refine ⟨⟨⟨lt hl, ?_⟩, ?_⟩, ?_⟩
  · cases h : r.rhs <;> simp_all [RuleS.ok]
  · simp only [List.all_map, List.all_eq_true, Function.comp]
    intro s hs
    cases s with
    | n x => simpa using lt (hcl r hr x hs)
    | t a => rfl
  · unfold RuleS.ok at ho
    cases h : r.rhs with
    | nil => rfl
    | cons s tl =>
      cases s with
      | t a => rfl
      | n x =>
        rw [h] at ho
        have hx := hcl r hr x (by simp [h])
        simp only [List.map_cons, decide_eq_true_eq] at ho ⊢
        rw [rk hx, rk hl]; exact ho

/-- `closed` adds only `ok` rules, and leaves no nonterminal of a right side without a rule. -/
theorem closed_ok {rs : List RuleS} (hok : (rs).all RuleS.ok = true) : ∀ r ∈ closed rs, r.ok = true := by
  intro r hr
  simp only [closed, List.mem_append, List.mem_map] at hr
  rcases hr with hr | ⟨x, _, rfl⟩
  · exact List.all_eq_true.mp hok r hr
  · rfl

theorem closed_cl (rs : List RuleS) : ∀ r ∈ closed rs, ∀ x, .n x ∈ r.rhs → x ∈ (closed rs).map (·.lhs) := by
  intro r hr x hx
  simp only [closed, List.mem_append, List.mem_map] at hr
  rcases hr with hr | ⟨y, _, rfl⟩
  · by_cases hd : rs.any (·.lhs == x) = true
    · obtain ⟨r', hr', he⟩ := List.any_eq_true.mp hd
      exact List.mem_map.mpr ⟨r', by simp [closed, hr'], by simpa using he⟩
    · refine List.mem_map.mpr ⟨⟨x, [.t .never], .shape⟩, ?_, rfl⟩
      simp only [closed, List.mem_append, List.mem_map, List.mem_filter, mem_firsts, List.mem_flatMap,
        List.mem_filterMap]
      exact .inr ⟨x, ⟨⟨r, hr, .n x, hx, rfl⟩, by simpa using hd⟩, rfl⟩
  · simp at hx

/-- W2 and W3 over the rule table: every right side is non-empty, and a first nonterminal ranks below the left side. -/
theorem schema_ranked (V : Vocab) (h : framesOk V = true) :
    ∀ r ∈ schema V, r.rhs ≠ [] ∧ ∀ B rest, r.rhs = .n B :: rest → B.rank < r.lhs.rank := by
  intro r hr
  have ho := List.all_eq_true.mp (schema_ok h) r hr
  unfold RuleS.ok at ho
  refine ⟨fun he => by simp [he] at ho, fun B rest he => by simpa [he] using ho⟩

theorem grammar_wf (V : Vocab) (h : framesOk V = true) : (grammar V).wf = true :=
  build_wf (closed_ok (schema_ok h)) (closed_cl _) (by simp [closed, schema, globalRules])

/-! ### The edge rule (plan 2.4, spec 7) -/

/-- 2.4: a rule that attaches a modifier beyond its own item does so at an edge: `first` only in the first item's
prefix (`E1X`), `last` only in trailing positions (`TE`, `RE`, `REt`, `PX`), `all` in either (5.2's `E1X` reads over
the first item or all). -/
def attachOf : Kind → Option Attach
  | .shape => none
  | .edge a => some a
/-- The left sides where an attachment may stand; no middle item's nonterminal is one. -/
def edgeLhs (x : NT) : Attach → Bool
  | .first => (x matches .E1X)
  | .last => (x matches .F _ .TE | .F _ .RE | .F _ .REt | .F _ .PX)
  | .all => x matches .E1X | .F _ .TE | .F _ .RE | .F _ .REt | .F _ .PX

theorem modifier_edges (V : Vocab) : ∀ r ∈ schema V, ∀ a, attachOf r.kind = some a → edgeLhs r.lhs a = true := by
  let ok (r : RuleS) : Bool := match attachOf r.kind with | some a => edgeLhs r.lhs a | none => true
  have hf (h : Nat) (f : Frame) : (frameRules V h f).all ok = true := by
    by_cases ho : "" ∈ f.markers <;> by_cases hs : "" ∈ f.split <;>
      simp [ok, frameRules, many1, tail, kwSyms, ho, hs, attachOf, edgeLhs]
  have hg : (globalRules V).all ok = true := by
    simp [ok, globalRules, items, many1, tail, kwSyms, attachOf, edgeLhs]
  intro r hr a ha
  have hs : (schema V).all ok = true := by
    simp only [schema, List.all_append, List.all_flatMap, hg, Bool.true_and, List.all_eq_true]
    exact fun ⟨f, h⟩ _ => List.all_eq_true.mp (hf h f)
  simpa [ok, ha] using List.all_eq_true.mp hs r hr

end VE.Acts
