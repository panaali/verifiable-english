import VE.Acts.Read
import VE.Acts.LexicalProofs

/-! The act grammar's rule table (docs/spec/act-phrases.md 5.2) and its well-formedness `grammar_wf` (5.6).

`schema V` writes the rules of 5.2 over named nonterminals, and `build` numbers them and closes each nonterminal that
has no rule with `X → never`. The nonterminals are structured (`NT`, with frame `h`'s in `FNT`), and each constructor
has a rank (`NT.rank`), so condition W3 holds by construction: a rule's first nonterminal has a lower rank than its
left side. A rule's kind, the meaning's action (5.3), comes with the meaning (ap-2c); until then the two rules of each
edge (5.2's "two derivations") are written twice, alike, and the meaning tells them apart by their order.
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
def FNT.rank : FNT → Nat
  | .HD | .WR => 0
  | .FL | .PT | .TE | .RE | .REt | .MEL | .MGT | .AR _ | .RT _ | .OL _ => 1
  | .PL | .TR | .REP | .MG | .RL _ => 2
  | .O | .OS | .LST _ _ => 3
  | .EE | .NM | .RX | .SPL | .PX => 4
  | .ER | .ERN | .RR | .PO => 5
  | .OWNM | .LFM | .RM => 6
  | .SM => 7
def NT.rank : NT → Nat
  | .ADVSO | .E1S | .SC | .C _ | .T _ _ => 1
  | .SINGLE | .F1 _ _ | .L _ _ => 2
  | .COORD => 3
  | .F _ x => x.rank
  | _ => 0

/-- A symbol of a right side: a terminal or a named nonterminal. -/
inductive RSym | t (a : Term) | n (x : NT)
  deriving DecidableEq, Repr

/-- A rule over named nonterminals. -/
structure RuleS where
  lhs : NT
  rhs : List RSym
  deriving DecidableEq, Repr

/-- The words `ws`, each as a `kw` terminal. -/
def kwSyms (ws : List String) : List RSym := ws.map (fun w => .t (.kw w))
/-- `X → x | x X`: one or more `x`. -/
def many1 (X : NT) (x : RSym) : List RuleS := [⟨X, [x]⟩, ⟨X, [x, .n X]⟩]
/-- A list's tail (`TM:B`, `PTh`, `RTh:m`, `MGTh`): a join word and a last member, with a comma before the join word
or not, or a comma, a middle member and the rest. -/
def tail (X : NT) (lasts : List RSym) (mid : RSym) : List RuleS :=
  lasts.map (fun x => ⟨X, [.n .J, x]⟩) ++ lasts.map (fun x => ⟨X, [.t .comma, .n .J, x]⟩) ++ [⟨X, [.t .comma, mid, .n X]⟩]
/-- Function words and adverbs before a core `c` (5.2's `SINGLE`, `F1S:c`, `F1O:c`, `LO:c`): adverbs `a` may stand
before the first function word, and after it `a` when the function words are shared, `ADVSO` when they are `own`. -/
def items (X a c : NT) (own : Bool) : List RuleS :=
  ((if own then [[.FW, c], [a, .FW, c], [.FW, .ADVSO, c], [a, .FW, .ADVSO, c]]
    else [[c], [a, c], [.FW, c], [a, .FW, c], [.FW, a, c], [a, .FW, a, c]]).map (·.map .n)).map (⟨X, ·⟩)

/-- Start, items and coordinations (5.2), with one `MK m` per marker of any frame. -/
def globalRules (V : Vocab) : List RuleS :=
  let adv : RSym := .t (.adv V.adverbs)
  [⟨.S, [.t .subj, .n .SINGLE]⟩, ⟨.S, [.t .subj, .n .COORD]⟩, ⟨.J, kwSyms ["and"]⟩, ⟨.J, kwSyms ["or"]⟩,
    ⟨.J, kwSyms ["nor"]⟩, ⟨.FW, kwSyms ["to"]⟩, ⟨.FW, kwSyms ["be"]⟩, ⟨.FW, kwSyms ["to", "be"]⟩,
    ⟨.TOK, [.t .slot]⟩, ⟨.TOK, [.t .fixed]⟩, ⟨.ADVO, [adv]⟩, ⟨.E1X, [adv]⟩, ⟨.E1X, [adv]⟩] ++
  many1 .ADVSO (.n .ADVO) ++ many1 .E1S (.n .E1X) ++ items .SINGLE .ADVSO .SC false ++
  [true, false].flatMap (fun own =>
    [Core.bare, .own].flatMap (fun c => items (.F1 own c) .E1S (.C c) own) ++
    [Core.bare, .own, .last, .rnr].flatMap (fun c =>
      if own then items (.L true c) .ADVSO (.C c) true else [⟨.L false c, [.n (.C c)]⟩, ⟨.L false c, [.n .ADVSO, .n (.C c)]⟩]) ++
    [⟨.COORD, [.n (.F1 own .bare), .n (.T own .bare)]⟩, ⟨.COORD, [.n (.F1 own .bare), .n (.T own .rnr)]⟩,
      ⟨.COORD, [.n (.F1 own .own), .n (.T own .own)]⟩] ++
    tail (.T own .bare) [.n (.L own .bare)] (.n (.L own .bare)) ++
    tail (.T own .rnr) [.n (.L own .rnr)] (.n (.L own .bare)) ++
    tail (.T own .own) [.n (.L own .last), .n (.L own .bare)] (.n (.L own .own))) ++
  (firsts ((V.frames.flatMap (fun f => f.markers ++ f.mods)).filter (· ≠ ""))).map (fun m => ⟨.MK m, kwSyms (wordsOf m)⟩)

/-- The filler words' exclusions for frame `f` (1.4): the join and function words, the adverbs, the first words of
`f`'s markers and modifier markers, and the first words of all heads. -/
def fillExcl (V : Vocab) (f : Frame) : List String :=
  ["and", "or", "nor", "to", "be"] ++ V.adverbs ++ (f.markers ++ f.mods).filterMap (fun m => (wordsOf m).head?) ++
    V.frames.filterMap (·.head.head?)

/-- The rules of frame `f`, numbered `h` (5.2, "Per frame h"). -/
def frameRules (V : Vocab) (h : Nat) (f : Frame) : List RuleS :=
  let x (y : FNT) : RSym := .n (.F h y)
  let r (y : FNT) (rhs : List RSym) : RuleS := ⟨.F h y, rhs⟩
  let adv : RSym := .t (.adv V.adverbs)
  let obj := f.markers.contains ""
  let objSplit := obj && f.split.contains ""
  let ms := f.markers.filter (· ≠ "")
  let plain := ms.filter (!f.split.contains ·)
  -- the arguments and not-split lists of `y`; an edge of `y` (an adverb or a modifier, each read two ways)
  let args (y : FNT) : List RuleS := ms.map (fun m => r y [x (.AR m)]) ++ plain.map (fun m => r y [x (.LST m false)])
  let edge (y : FNT) (fl : RSym) : List RuleS :=
    [r y [adv], r y [adv]] ++ f.mods.flatMap (fun m => [r y [.n (.MK m), fl], r y [.n (.MK m), fl]])
  [r .HD (kwSyms f.head), ⟨.C .bare, [x .HD]⟩, ⟨.C .own, [x .HD, x .OWNM]⟩, ⟨.C .last, [x .HD, x .LFM]⟩,
    ⟨.C .rnr, [x .HD, x .RM]⟩, ⟨.SC, [x .HD]⟩, ⟨.SC, [x .HD, x .SM]⟩] ++
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
  rs ++ ((firsts (rs.flatMap (·.rhs.filterMap RSym.nt?))).filter (fun x => !rs.any (·.lhs == x))).map (⟨·, [.t .never]⟩)

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

theorem kwSyms_ok {X : NT} {ws : List String} (h : ws ≠ []) : RuleS.ok ⟨X, kwSyms ws⟩ = true := by
  cases ws with
  | nil => exact absurd rfl h
  | cons w ws => rfl

theorem frameRules_ok (V : Vocab) (h : Nat) {f : Frame} (hh : f.head ≠ []) : (frameRules V h f).all RuleS.ok = true := by
  obtain ⟨w, ws, hw⟩ : ∃ w ws, f.head = w :: ws := by cases hx : f.head <;> simp_all
  by_cases ho : "" ∈ f.markers <;> by_cases hs : "" ∈ f.split <;>
    simp [frameRules, many1, tail, kwSyms, hw, ho, hs, RuleS.ok, NT.rank, FNT.rank]

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
    · refine List.mem_map.mpr ⟨⟨x, [.t .never]⟩, ?_, rfl⟩
      simp only [closed, List.mem_append, List.mem_map, List.mem_filter, mem_firsts, List.mem_flatMap,
        List.mem_filterMap]
      exact .inr ⟨x, ⟨⟨r, hr, .n x, hx, rfl⟩, by simpa using hd⟩, rfl⟩
  · simp at hx

theorem grammar_wf (V : Vocab) (h : framesOk V = true) : (grammar V).wf = true :=
  build_wf (closed_ok (schema_ok h)) (closed_cl _) (by simp [closed, schema, globalRules])

end VE.Acts
