import VE.Core.Conservativity
import VE.TableauExtendedChecker
import VE.Route.Steps
import VE.Core.Wire

/-! Closure's tableau checker is Core's on the embedding (consolidation step 3a).

`VE/TableauExtended*` are textual copies of `VE/Core/TableauExtended*` over the closure
language, which lacks Core's n-ary atoms. Embedding a closure branch and trace into Core
(`embedBranch`, `embedTrace`, `embedCert`, with `VE.Core.embedClosure` on formulas) commutes
with every function replay calls, so `replay` agrees for both flags and every fuel, and so do
the step counts. The two `checkCertificate`s differ only in their version gate. The trace
decoders do not agree: Core's decodes an n-ary `atom` invariant that closure's refuses. -/
namespace VE.Closure.CoreEquiv

open VE.Core (embedClosure embedKind)

def embedToken : Tableau.Token → Core.Tableau.Token
  | .constant c => .constant c
  | .witness i => .witness i

mutual
def embedTrace : Tableau.Trace → Core.Tableau.Trace
  | .close => .close
  | .expand rule index parameter children => .expand rule index parameter (embedTraces children)
  | .induct index sort P children => .induct index sort (embedClosure P) (embedTraces children)
def embedTraces : List Tableau.Trace → List Core.Tableau.Trace
  | [] => []
  | t :: ts => embedTrace t :: embedTraces ts
end

def embedCert (c : Tableau.Certificate) : Core.Tableau.Certificate :=
  ⟨c.checker_version, c.environment_id, c.premise_meaning_ids, c.conclusion_meaning_id,
    embedTrace c.trace⟩

def embedSigned (a : Tableau.Signed) : Core.Tableau.Signed :=
  ⟨embedClosure a.formula, a.positive, a.bindings.map embedToken⟩

def embedBranch (b : Tableau.Branch) : Core.Tableau.Branch :=
  ⟨b.formulas.map embedSigned, b.witnesses, b.expanded,
    b.instantiated.map fun p => (p.1, embedToken p.2)⟩

/-! ### Formulas: Core's copies of the closure functions agree on `embedClosure`. -/

theorem embedKind_inj (k l : Kind) : embedKind k = embedKind l ↔ k = l := by
  cases k <;> cases l <;> decide

theorem embedClosure_inj (a b : Formula) : embedClosure a = embedClosure b ↔ a = b := by
  induction a generalizing b <;> cases b <;>
    simp_all [embedClosure, embedKind_inj]

theorem liftTerm_eq (t : Term) : VE.Core.liftTerm t = VE.Closure.liftTerm t := by
  cases t <;> rfl

theorem liftSub_eq (σ : Nat → Term) : VE.Core.liftSub σ = VE.Closure.liftSub σ := by
  funext i
  cases i <;> simp [VE.Core.liftSub, VE.Closure.liftSub, liftTerm_eq]

theorem substTerm_eq (σ : Nat → Term) (t : Term) :
    VE.Core.substTerm σ t = VE.Closure.substTerm σ t := by
  cases t <;> rfl

theorem subst_embed (a : Formula) (σ τ : Nat → Term) (h : ∀ i, σ i = τ i) :
    (embedClosure a).subst σ = embedClosure (a.subst τ) := by
  have hστ : σ = τ := funext h
  subst hστ
  induction a generalizing σ <;>
    simp_all [embedClosure, VE.Core.Formula.subst, Formula.subst, substTerm_eq, liftSub_eq]

def embedEdge : Edge → Core.Edge
  | .named p => .named p
  | .body s a => .body s (embedClosure a)

theorem embedEdge_inj (e f : Edge) : embedEdge e = embedEdge f ↔ e = f := by
  cases e <;> cases f <;> simp [embedEdge, embedClosure_inj]

theorem reach_embed (k : Kind) (e : Edge) (t u : Term) :
    Core.Formula.reach (embedKind k) (embedEdge e) t u = embedClosure (Formula.reach k e t u) := by
  cases e <;> rfl

theorem shift_embed (e : Edge) : (embedEdge e).shift = embedEdge e.shift := by
  cases e with
  | named p => rfl
  | body s a =>
    simp only [embedEdge, Core.Edge.shift, Edge.shift, Core.Edge.body.injEq, true_and]
    exact subst_embed a _ _ (fun i => by simp [liftSub_eq])

theorem at_embed (e : Edge) (t r : Term) : (embedEdge e).at t r = embedClosure (e.at t r) := by
  cases e with
  | named p => rfl
  | body s a =>
    exact subst_embed a _ _ (fun i => by rcases i with _ | _ | i <;> rfl)

theorem unfold_embed (k : Kind) (e : Edge) (s : String) (t r : Term) :
    Core.unfold (embedKind k) (embedEdge e) s t r = embedClosure (unfold k e s t r) := by
  cases k <;>
    simp [embedKind, Core.unfold, unfold, embedClosure, at_embed, shift_embed, liftTerm_eq,
      ← reach_embed] <;> rfl

theorem composeKind_embed (k l : Kind) :
    Core.composeKind (embedKind k) (embedKind l) = embedKind (composeKind k l) := by
  cases k <;> cases l <;> rfl

theorem endEdge_embed (last : Bool) (e : Edge) (s : String) (t r : Term) :
    Core.endEdge last (embedEdge e) s t r = embedClosure (endEdge last e s t r) := by
  cases last <;> simp [Core.endEdge, endEdge, embedClosure, at_embed, shift_embed, liftTerm_eq]

theorem invariantAt_embed (P : Formula) (t : Term) :
    Core.invariantAt (embedClosure P) t = embedClosure (invariantAt P t) :=
  subst_embed P _ _ (fun i => by rcases i with _ | i <;> rfl)

theorem inductionStep_embed (s : String) (e : Edge) (P : Formula) :
    Core.inductionStep s (embedEdge e) (embedClosure P) =
      embedClosure (inductionStep s e P) := by
  simp only [Core.inductionStep, inductionStep, embedClosure, shift_embed, at_embed,
    Core.Formula.all.injEq, Core.Formula.implies.injEq, Core.Formula.and.injEq, true_and, and_true]
  exact ⟨subst_embed P _ _ (fun i => by rcases i with _ | i <;> rfl),
    subst_embed P _ _ (fun i => by rcases i with _ | i <;> rfl)⟩

theorem unlift_eq (t : Term) : Core.unlift t = unlift t := by
  rcases t with _ | _ | i <;> rfl

theorem liftMatch_eq (cmp : Term → Term → Bool) : Core.liftMatch cmp = liftMatch cmp := by
  funext t r
  simp only [Core.liftMatch, liftMatch, unlift_eq]
  cases unlift t <;> cases unlift r <;> rfl

theorem matches_embed (cmp : Term → Term → Bool) (a b : Formula) :
    (embedClosure a).matches cmp (embedClosure b) = a.matches cmp b := by
  induction a generalizing b cmp <;> cases b <;>
    simp_all [embedClosure, Core.Formula.matches, Formula.matches, liftMatch_eq, embedKind_inj]

/-! ### Tokens, signed formulas and branches. -/

theorem embedToken_inj (t r : Tableau.Token) : embedToken t = embedToken r ↔ t = r := by
  cases t <;> cases r <;> simp [embedToken]

theorem mem_map_embedToken (t : Tableau.Token) (ts : List Tableau.Token) :
    embedToken t ∈ ts.map embedToken ↔ t ∈ ts := by
  simp [embedToken_inj]

theorem map_embedToken_inj (ts rs : List Tableau.Token) :
    ts.map embedToken = rs.map embedToken ↔ ts = rs := by
  induction ts generalizing rs with
  | nil => cases rs <;> simp
  | cons t ts ih => cases rs <;> simp [embedToken_inj, ih]

theorem mem_instantiated (i : Nat) (t : Tableau.Token) (ps : List (Nat × Tableau.Token)) :
    (i, embedToken t) ∈ ps.map (fun p => (p.1, embedToken p.2)) ↔ (i, t) ∈ ps := by
  constructor
  · intro h
    obtain ⟨⟨j, r⟩, hm, he⟩ := List.mem_map.mp h
    simp only [Prod.mk.injEq, embedToken_inj] at he
    obtain ⟨rfl, rfl⟩ := he
    exact hm
  · intro h
    exact List.mem_map.mpr ⟨(i, t), h, rfl⟩

theorem parse_embed (text : String) :
    Core.Tableau.Token.parse text = (Tableau.Token.parse text).map embedToken := by
  simp only [Core.Tableau.Token.parse, Tableau.Token.parse]
  split
  · rfl
  · split
    · cases (text.drop 2).toNat? <;> simp [bind, Option.bind] <;> split <;> rfl
    · rfl

theorem sortOf_embed (E : Environment) (b : Tableau.Branch) (t : Tableau.Token) :
    (embedToken t).sortOf E (embedBranch b) = t.sortOf E b := by
  cases t <;> rfl

theorem scoped_embed (b : Tableau.Branch) : (embedBranch b).scoped = b.scoped := by
  have ht : ∀ n (t : Tableau.Token), (embedToken t).scoped n = t.scoped n := by
    intro n t; cases t <;> rfl
  simp [Core.Tableau.Branch.scoped, Tableau.Branch.scoped, embedBranch, embedSigned, List.all_map,
    Function.comp_def, ht]

theorem known_embed (E : Environment) (b : Tableau.Branch) :
    (embedBranch b).known E = b.known E := by
  simp only [Core.Tableau.Branch.known, Tableau.Branch.known]
  conv => lhs; arg 1; simp only [embedBranch]
  simp [List.all_map, Function.comp_def, embedSigned, sortOf_embed]

theorem embedBranch_expanded (b : Tableau.Branch) : (embedBranch b).expanded = b.expanded := rfl

theorem embedBranch_instantiated (b : Tableau.Branch) :
    (embedBranch b).instantiated = b.instantiated.map fun p => (p.1, embedToken p.2) := rfl

theorem embedSigned_bindings (a : Tableau.Signed) :
    (embedSigned a).bindings = a.bindings.map embedToken := rfl

theorem add_embed (b : Tableau.Branch) (xs : List Tableau.Signed) :
    (embedBranch b).add (xs.map embedSigned) = embedBranch (b.add xs) := by
  simp [Core.Tableau.Branch.add, Tableau.Branch.add, embedBranch]

theorem getElem?_embed (b : Tableau.Branch) (i : Nat) :
    (embedBranch b).formulas[i]? = (b.formulas[i]?).map embedSigned := by
  simp [embedBranch]

def embedRule : Tableau.Rule → Core.Tableau.Rule
  | .literal => .literal
  | .closure k e t r => .closure (embedKind k) (embedEdge e) t r
  | .one xs => .one (xs.map embedSigned)
  | .two x y => .two (embedSigned x) (embedSigned y)
  | .gamma s f => .gamma s (embedClosure f)
  | .delta s f => .delta s (embedClosure f)

theorem rule_embed (a : Tableau.Signed) : (embedSigned a).rule = embedRule a.rule := by
  rcases a with ⟨f, p, bs⟩
  cases f <;> cases p <;> rfl

theorem tag_embed (a : Tableau.Signed) : (embedSigned a).tag = a.tag := by
  rcases a with ⟨f, p, bs⟩
  cases f with
  | reachNamed k r t u => cases k <;> rfl
  | reachBody k s g t u => cases k <;> rfl
  | _ => rfl

/-! ### Literals and the equality closure. -/

def embedAtom : Tableau.Atom → Core.Tableau.Atom
  | .top => .top
  | .bottom => .bottom
  | .unary p t => .unary p (embedToken t)
  | .binary p t r => .binary p (embedToken t) (embedToken r)
  | .eq t r => .eq (embedToken t) (embedToken r)

def embedLiteral (l : Tableau.Literal) : Core.Tableau.Literal :=
  ⟨embedAtom l.atom, l.positive⟩

def embedPair (e : Tableau.Token × Tableau.Token) : Core.Tableau.Token × Core.Tableau.Token :=
  (embedToken e.1, embedToken e.2)

theorem termToken_embed (bs : List Tableau.Token) (t : Term) :
    Core.Tableau.termToken (bs.map embedToken) t = (Tableau.termToken bs t).map embedToken := by
  cases t <;> simp [Core.Tableau.termToken, Tableau.termToken, embedToken]

theorem ground_embed (bs : List Tableau.Token) (f : Formula) :
    Core.Tableau.ground (bs.map embedToken) (embedClosure f) =
      (Tableau.ground bs f).map embedAtom := by
  cases f with
  | unary p t =>
    cases h : Tableau.termToken bs t <;>
      simp [embedClosure, Core.Tableau.ground, Tableau.ground, termToken_embed, h, embedAtom]
  | binary p t r =>
    cases h : Tableau.termToken bs t <;> cases h' : Tableau.termToken bs r <;>
      simp [embedClosure, Core.Tableau.ground, Tableau.ground, termToken_embed, h, h', embedAtom]
  | eq t r =>
    cases h : Tableau.termToken bs t <;> cases h' : Tableau.termToken bs r <;>
      simp [embedClosure, Core.Tableau.ground, Tableau.ground, termToken_embed, h, h', embedAtom]
  | _ => rfl

theorem literals_embed (b : Tableau.Branch) :
    Core.Tableau.literals (embedBranch b) = (Tableau.literals b).map embedLiteral := by
  simp only [Core.Tableau.literals, Tableau.literals, embedBranch, List.filterMap_map,
    List.map_filterMap]
  congr 1
  funext a
  simp [embedSigned, ground_embed, embedLiteral, Function.comp_def, Option.map_map]

theorem equalities_embed (ls : List Tableau.Literal) :
    Core.Tableau.equalities (ls.map embedLiteral) = (Tableau.equalities ls).map embedPair := by
  simp only [Core.Tableau.equalities, Tableau.equalities, List.filterMap_map, List.map_filterMap]
  congr 1
  funext l
  rcases l with ⟨a, p⟩
  cases a <;> cases p <;> rfl

theorem dedup_embed (ts : List Tableau.Token) :
    Core.Tableau.dedup (ts.map embedToken) = (Tableau.dedup ts).map embedToken := by
  induction ts with
  | nil => rfl
  | cons t ts ih =>
    simp only [List.map_cons, Core.Tableau.dedup, Tableau.dedup, ih, mem_map_embedToken]
    split <;> rfl

theorem grow_embed (es : List (Tableau.Token × Tableau.Token)) (seen : List Tableau.Token) :
    Core.Tableau.grow (es.map embedPair) (seen.map embedToken) =
      (Tableau.grow es seen).map embedToken := by
  simp only [Core.Tableau.grow, Tableau.grow, ← dedup_embed, List.map_append, List.flatMap_map,
    List.map_flatMap]
  congr 2
  refine congrArg (fun f => List.flatMap f es) (funext fun e => ?_)
  rcases e with ⟨a, c⟩
  simp only [embedPair, mem_map_embedToken]
  split <;> split <;> rfl

theorem reachable_embed (es : List (Tableau.Token × Tableau.Token)) (n : Nat)
    (seen : List Tableau.Token) :
    Core.Tableau.reachable (es.map embedPair) n (seen.map embedToken) =
      (Tableau.reachable es n seen).map embedToken := by
  induction n generalizing seen with
  | zero => rfl
  | succ n ih => simp only [Core.Tableau.reachable, Tableau.reachable, grow_embed, ih]

theorem equivalent_embed (es : List (Tableau.Token × Tableau.Token)) (t r : Tableau.Token) :
    Core.Tableau.equivalent (es.map embedPair) (embedToken t) (embedToken r) =
      Tableau.equivalent es t r := by
  have h := reachable_embed es es.length [t]
  simp only [List.map_cons, List.map_nil] at h
  simp [Core.Tableau.equivalent, Tableau.equivalent, h, mem_map_embedToken]

theorem atomMatches_embed (es : List (Tableau.Token × Tableau.Token)) (x y : Tableau.Atom) :
    Core.Tableau.atomMatches (es.map embedPair) (embedAtom x) (embedAtom y) =
      Tableau.atomMatches es x y := by
  cases x <;> cases y <;>
    simp [embedAtom, Core.Tableau.atomMatches, Tableau.atomMatches, equivalent_embed]

theorem closes_embed (E : Environment) (b : Tableau.Branch) (ls : List Tableau.Literal)
    (l : Tableau.Literal) :
    Core.Tableau.closes E (embedBranch b) (ls.map embedLiteral) (embedLiteral l) =
      Tableau.closes E b ls l := by
  rcases l with ⟨a, p⟩
  cases a <;> cases p <;>
    simp [Core.Tableau.closes, Tableau.closes, embedLiteral, embedAtom, equalities_embed,
      equivalent_embed, sortOf_embed, List.any_map, Function.comp_def]
  all_goals
    congr 1; funext x; congr 1
    first
      | exact atomMatches_embed _ x.atom .top
      | exact atomMatches_embed _ x.atom .bottom
      | exact atomMatches_embed _ x.atom (.unary _ _)
      | exact atomMatches_embed _ x.atom (.binary _ _ _)

theorem closed_embed (E : Environment) (b : Tableau.Branch) :
    Core.Tableau.closed E (embedBranch b) = Tableau.closed E b := by
  simp [Core.Tableau.closed, Tableau.closed, literals_embed, List.any_map, Function.comp_def,
    closes_embed]

theorem complementary_embed (b : Tableau.Branch) :
    Core.Tableau.complementary (embedBranch b) = Tableau.complementary b := by
  simp [Core.Tableau.complementary, Tableau.complementary, embedBranch, List.any_map,
    Function.comp_def, embedSigned, embedClosure_inj, map_embedToken_inj]

/-! ### The rules. -/

theorem edgeCheck_embed (E : Environment) (s : String) (e : Edge) :
    Core.Tableau.edgeCheck E s (embedEdge e) = Tableau.edgeCheck E s e := by
  cases e <;> rfl

theorem unfoldAt_embed (E : Environment) (b : Tableau.Branch) (bs : List Tableau.Token)
    (k : Kind) (e : Edge) (t r : Term) :
    Core.Tableau.unfoldAt E (embedBranch b) (bs.map embedToken) (embedKind k) (embedEdge e) t r =
      (Tableau.unfoldAt E b bs k e t r).map embedClosure := by
  simp only [Core.Tableau.unfoldAt, Tableau.unfoldAt, termToken_embed]
  cases Tableau.termToken bs t <;> cases Tableau.termToken bs r <;>
    simp [bind, Option.bind, sortOf_embed]
  rename_i x y
  cases x.sortOf E b <;> simp [edgeCheck_embed]
  split <;> simp [unfold_embed]

theorem groundMatch_embed (es : List (Tableau.Token × Tableau.Token)) (bs cs : List Tableau.Token) :
    Core.Tableau.groundMatch (es.map embedPair) (bs.map embedToken) (cs.map embedToken) =
      Tableau.groundMatch es bs cs := by
  funext t r
  simp only [Core.Tableau.groundMatch, Tableau.groundMatch, termToken_embed]
  cases Tableau.termToken bs t <;> cases Tableau.termToken cs r <;>
    simp [equivalent_embed]

theorem isReach_embed (f : Formula) : Core.Tableau.isReach (embedClosure f) = Tableau.isReach f := by
  cases f <;> rfl

theorem reachClosed_embed (b : Tableau.Branch) :
    Core.Tableau.reachClosed (embedBranch b) = Tableau.reachClosed b := by
  simp only [Core.Tableau.reachClosed, Tableau.reachClosed, literals_embed, equalities_embed]
  conv => lhs; simp only [embedBranch]
  simp [List.any_map, Function.comp_def, embedSigned, isReach_embed, groundMatch_embed,
    matches_embed]

theorem edgeStep_embed (E : Environment) (a : Tableau.Signed) :
    Core.Tableau.edgeStep E (embedSigned a) = (Tableau.edgeStep E a).map embedSigned := by
  rcases a with ⟨f, p, bs⟩
  cases f <;> cases p <;> try rfl
  rename_i q t r
  simp only [embedSigned, embedClosure, Core.Tableau.edgeStep, Tableau.edgeStep]
  rcases E.predicates q with _ | _ | ⟨s, _ | ⟨w, _ | _⟩⟩ <;> try rfl
  by_cases h : s = w <;> simp [h] <;> rfl

theorem composeStep_embed (a d : Tableau.Signed) :
    Core.Tableau.composeStep (embedSigned a) (embedSigned d) =
      (Tableau.composeStep a d).map embedSigned := by
  simp only [Core.Tableau.composeStep, Tableau.composeStep, rule_embed]
  cases a.rule <;> cases d.rule <;> try rfl
  rename_i k e t r l f u v
  simp only [embedRule, embedSigned, map_embedToken_inj, embedEdge_inj]
  split <;> simp_all [composeKind_embed, reach_embed, embedSigned]

theorem endStep_embed (E : Environment) (b : Tableau.Branch) (a : Tableau.Signed) (last : Bool) :
    Core.Tableau.endStep E (embedBranch b) (embedSigned a) last =
      (Tableau.endStep E b a last).map embedSigned := by
  simp only [Core.Tableau.endStep, Tableau.endStep, rule_embed]
  cases a.rule <;> try rfl
  rename_i k e t r
  cases k <;> try rfl
  simp only [embedRule, embedKind, embedSigned]
  split <;> try rfl
  simp only [termToken_embed, bind, Option.bind]
  cases Tableau.termToken a.bindings t <;> try rfl
  rename_i x
  simp only [Option.map_some, sortOf_embed]
  cases x.sortOf E b <;> try rfl
  simp only [edgeCheck_embed]
  split <;> simp [endEdge_embed, embedSigned]

theorem namedStep_embed (E : Environment) (a : Tableau.Signed) :
    Core.Tableau.namedStep E (embedSigned a) = (Tableau.namedStep E a).map embedSigned := by
  rcases a with ⟨f, p, bs⟩
  cases f <;> try rfl
  rename_i k q t r
  simp only [embedSigned, embedClosure, Core.Tableau.namedStep, Tableau.namedStep]
  rcases E.predicates q with _ | _ | ⟨s, _ | ⟨w, _ | _⟩⟩ <;> try rfl
  by_cases h : s = w <;> simp [h] <;> rfl

theorem extraRule_eq (rule : String) : Core.Tableau.extraRule rule = Tableau.extraRule rule := rfl

theorem deriveExtra_embed (E : Environment) (b : Tableau.Branch) (a : Tableau.Signed)
    (rule : String) (parameter : Option String) :
    Core.Tableau.deriveExtra E (embedBranch b) (embedSigned a) rule parameter =
      (Tableau.deriveExtra E b a rule parameter).map embedSigned := by
  simp only [Core.Tableau.deriveExtra, Tableau.deriveExtra]
  split
  · cases parameter <;> try rfl
    rename_i text
    simp only [bind, Option.bind]
    cases text.toNat? <;> try rfl
    rename_i j
    simp only [getElem?_embed]
    cases b.formulas[j]? <;> try rfl
    simp [composeStep_embed]
  · split <;> try rfl
    split
    · exact edgeStep_embed E a
    split
    · exact endStep_embed E b a false
    split
    · exact endStep_embed E b a true
    split
    · exact namedStep_embed E a
    rfl

theorem extra_embed (E : Environment) (b : Tableau.Branch) (rule : String) (index : Nat)
    (parameter : Option String) :
    Core.Tableau.extra E (embedBranch b) rule index parameter =
      (Tableau.extra E b rule index parameter).map (·.map embedBranch) := by
  simp only [Core.Tableau.extra, Tableau.extra, getElem?_embed, bind, Option.bind]
  cases b.formulas[index]? <;> try rfl
  simp only [Option.map_some, deriveExtra_embed]
  cases Tableau.deriveExtra E b _ rule parameter <;> try rfl
  simp [← add_embed]

theorem sortsOf_embed (E : Environment) (b : Tableau.Branch) (ts : List Tableau.Token) :
    (ts.map embedToken).mapM (Core.Tableau.Token.sortOf E (embedBranch b)) =
      ts.mapM (Tableau.Token.sortOf E b) := by
  induction ts with
  | nil => rfl
  | cons t ts ih => simp [List.mapM_cons, sortOf_embed, ih]

theorem induct_embed (E : Environment) (b : Tableau.Branch) (index : Nat) (s : String)
    (P : Formula) :
    Core.Tableau.induct E (embedBranch b) index s (embedClosure P) =
      (Tableau.induct E b index s P).map (·.map embedBranch) := by
  simp only [Core.Tableau.induct, Tableau.induct, getElem?_embed, bind, Option.bind]
  cases b.formulas[index]? <;> try rfl
  rename_i a
  simp only [Option.map_some, rule_embed]
  cases a.rule <;> try rfl
  rename_i k e t r
  simp only [embedRule, embedSigned, sortsOf_embed]
  cases a.bindings.mapM (Tableau.Token.sortOf E b) <;> try rfl
  simp only [edgeCheck_embed, VE.Core.embedClosure_check]
  split <;> try rfl
  simp [← add_embed, embedSigned, invariantAt_embed, inductionStep_embed]

theorem next_embed (E : Environment) (b : Tableau.Branch) (index : Nat)
    (parameter : Option String) :
    Core.Tableau.next E (embedBranch b) index parameter =
      (Tableau.next E b index parameter).map (·.map embedBranch) := by
  simp only [Core.Tableau.next, Tableau.next, getElem?_embed, bind, Option.bind]
  cases b.formulas[index]? <;> try rfl
  rename_i a
  simp only [Option.map_some, rule_embed]
  cases a.rule with
  | literal => rfl
  | closure k e t r =>
    simp only [embedRule, embedBranch_expanded, embedSigned_bindings, unfoldAt_embed]
    by_cases hc : (parameter.isSome || decide (index ∈ b.expanded)) = true
    · simp [hc]
    · simp only [hc]
      cases Tableau.unfoldAt E b a.bindings k e t r <;>
        simp [Core.Tableau.Branch.add, Tableau.Branch.add, embedBranch, embedSigned]
  | gamma s f =>
    simp only [embedRule]
    cases parameter with
    | none => rfl
    | some text =>
      simp only [parse_embed]
      cases Tableau.Token.parse text with
      | none => rfl
      | some t =>
        simp only [Option.map_some, sortOf_embed, embedBranch_instantiated, mem_instantiated]
        by_cases hc : (decide (t.sortOf E b ≠ some s) || decide ((index, t) ∈ b.instantiated)) = true
        · simp only [hc]; rfl
        · simp only [hc]
          simp [Core.Tableau.Branch.add, Tableau.Branch.add, embedBranch, embedSigned]
  | one xs =>
    simp only [embedRule, embedBranch_expanded]
    by_cases hc : (parameter.isSome || decide (index ∈ b.expanded)) = true
    · simp [hc]
    · simp only [hc]
      simp [Core.Tableau.Branch.add, Tableau.Branch.add, embedBranch]
  | two x y =>
    simp only [embedRule, embedBranch_expanded]
    by_cases hc : (parameter.isSome || decide (index ∈ b.expanded)) = true
    · simp [hc]
    · simp only [hc]
      simp [Core.Tableau.Branch.add, Tableau.Branch.add, embedBranch, embedSigned]
  | delta s f =>
    simp only [embedRule, embedBranch_expanded]
    by_cases hc : (parameter.isSome || decide (index ∈ b.expanded)) = true
    · simp [hc]
    · simp only [hc]
      simp [Core.Tableau.Branch.add, Tableau.Branch.add, embedBranch, embedSigned, embedToken]

theorem step_embed (E : Environment) (b : Tableau.Branch) (rule : String) (index : Nat)
    (parameter : Option String) :
    Core.Tableau.step E (embedBranch b) rule index parameter =
      (Tableau.step E b rule index parameter).map (·.map embedBranch) := by
  simp only [Core.Tableau.step, Tableau.step, extraRule_eq, getElem?_embed]
  split
  · exact extra_embed E b rule index parameter
  · simp only [Option.any_map, tag_embed]
    split
    · exact next_embed E b index parameter
    · rfl

theorem checkChildren_embed (f : Core.Tableau.Branch → Core.Tableau.Trace → Bool)
    (g : Tableau.Branch → Tableau.Trace → Bool) (h : ∀ b t, f (embedBranch b) (embedTrace t) = g b t)
    (bs : List Tableau.Branch) (ts : List Tableau.Trace) :
    Core.Tableau.checkChildren f (bs.map embedBranch) (embedTraces ts) =
      Tableau.checkChildren g bs ts := by
  induction bs generalizing ts with
  | nil => cases ts <;> rfl
  | cons b bs ih =>
    cases ts with
    | nil => rfl
    | cons t ts =>
      simp only [List.map_cons, embedTraces, Core.Tableau.checkChildren, Tableau.checkChildren,
        h, ih]

/-- Closure's replay is Core's replay on the embedding, for both flags and every fuel. -/
theorem replay_embed (E : Environment) (compound induction : Bool) (fuel : Nat)
    (b : Tableau.Branch) (t : Tableau.Trace) :
    Core.Tableau.replay E compound induction fuel (embedBranch b) (embedTrace t) =
      Tableau.replay E compound induction fuel b t := by
  induction fuel generalizing b t with
  | zero => rfl
  | succ fuel ih =>
    cases t with
    | close =>
      simp only [Core.Tableau.replay, Tableau.replay, embedTrace, scoped_embed, known_embed,
        closed_embed, complementary_embed, reachClosed_embed]
    | expand rule index parameter children =>
      simp only [Core.Tableau.replay, Tableau.replay, embedTrace, scoped_embed, known_embed,
        step_embed]
      cases Tableau.step E b rule index parameter with
      | none => rfl
      | some bs => simp only [Option.map_some, checkChildren_embed _ _ ih]
    | induct index s P children =>
      simp only [Core.Tableau.replay, Tableau.replay, embedTrace, scoped_embed, known_embed,
        induct_embed]
      cases Tableau.induct E b index s P with
      | none => rfl
      | some bs => simp only [Option.map_some, checkChildren_embed _ _ ih]

theorem initial_embed (premises : List Formula) (conclusion : Formula) :
    Core.Tableau.initial (premises.map embedClosure) (embedClosure conclusion) =
      embedBranch (Tableau.initial premises conclusion) := by
  simp [Core.Tableau.initial, Tableau.initial, embedBranch, embedSigned, Function.comp_def]

/-- On a certificate: closure's replay from its initial branch is Core's replay of the
embedded certificate from the embedded initial branch, for both flags and every fuel. -/
theorem replay_certificate_embed (E : Environment) (compound induction : Bool) (fuel : Nat)
    (premises : List Formula) (conclusion : Formula) (c : Tableau.Certificate) :
    Core.Tableau.replay E compound induction fuel
        (Core.Tableau.initial (premises.map embedClosure) (embedClosure conclusion))
        (embedCert c).trace =
      Tableau.replay E compound induction fuel (Tableau.initial premises conclusion) c.trace := by
  rw [← replay_embed E compound induction fuel (Tableau.initial premises conclusion) c.trace,
    initial_embed]
  rfl

mutual
/-- A closure trace and its embedding count the same replay steps. -/
theorem steps_embed (t : Tableau.Trace) :
    VE.Route.Steps.core (embedTrace t) = VE.Route.Steps.closure t :=
  match t with
  | .close => rfl
  | .expand _ _ _ cs => by
    simp only [embedTrace, VE.Route.Steps.core, VE.Route.Steps.closure,
      VE.CertificateWire.closureSteps, stepsList_embed cs]
  | .induct _ _ _ cs => by
    simp only [embedTrace, VE.Route.Steps.core, VE.Route.Steps.closure,
      VE.CertificateWire.closureSteps, stepsList_embed cs]

theorem stepsList_embed (ts : List Tableau.Trace) :
    VE.Route.Steps.coreList (embedTraces ts) = VE.CertificateWire.closureStepsList ts :=
  match ts with
  | [] => rfl
  | t :: ts => by
    simp only [embedTraces, VE.Route.Steps.coreList, VE.CertificateWire.closureStepsList,
      steps_embed t, stepsList_embed ts]
end

/-- Closure's certificate checker is its own version gate and well-formedness checks, then
Core's replay of the embedded certificate with closure's flag choice (`version == @1`). -/
theorem checkCertificate_eq_core_replay (E : Environment) (premises : List Formula)
    (conclusion : Formula) (c : Tableau.Certificate) :
    Tableau.checkCertificate E premises conclusion c =
      ((c.checker_version == "ve-tableau-closure-checker@0" ||
          c.checker_version == "ve-tableau-closure-checker@1") &&
        (premises.map embedClosure).all (fun f => f.check E []) &&
        (embedClosure conclusion).check E [] &&
        Core.Tableau.replay E true (c.checker_version == "ve-tableau-closure-checker@1") 125
          (Core.Tableau.initial (premises.map embedClosure) (embedClosure conclusion))
          (embedCert c).trace) := by
  rw [replay_certificate_embed, VE.Core.embedClosure_check]
  simp [Tableau.checkCertificate, List.all_map, Function.comp_def, VE.Core.embedClosure_check]

/-- An `@0` certificate: Core's replay with the induction flag off. -/
theorem checkCertificate_v0 (E : Environment) (premises : List Formula)
    (conclusion : Formula) (c : Tableau.Certificate)
    (hv : c.checker_version = "ve-tableau-closure-checker@0") :
    Tableau.checkCertificate E premises conclusion c =
      ((premises.map embedClosure).all (fun f => f.check E []) &&
        (embedClosure conclusion).check E [] &&
        Core.Tableau.replay E true false 125
          (Core.Tableau.initial (premises.map embedClosure) (embedClosure conclusion))
          (embedCert c).trace) := by
  rw [checkCertificate_eq_core_replay, hv]
  simp

/-- An `@1` certificate: Core's replay with both flags on, as Core's own checker runs it. -/
theorem checkCertificate_v1 (E : Environment) (premises : List Formula)
    (conclusion : Formula) (c : Tableau.Certificate)
    (hv : c.checker_version = "ve-tableau-closure-checker@1") :
    Tableau.checkCertificate E premises conclusion c =
      ((premises.map embedClosure).all (fun f => f.check E []) &&
        (embedClosure conclusion).check E [] &&
        Core.Tableau.replay E true true 125
          (Core.Tableau.initial (premises.map embedClosure) (embedClosure conclusion))
          (embedCert c).trace) := by
  rw [checkCertificate_eq_core_replay, hv]
  simp

/-- Any other version is rejected. -/
theorem checkCertificate_other_version (E : Environment) (premises : List Formula)
    (conclusion : Formula) (c : Tableau.Certificate)
    (h0 : c.checker_version ≠ "ve-tableau-closure-checker@0")
    (h1 : c.checker_version ≠ "ve-tableau-closure-checker@1") :
    Tableau.checkCertificate E premises conclusion c = false := by
  simp [Tableau.checkCertificate, h0, h1]

/-- The trace decoders are not equal on the embedding: a `closure-induct@1` node whose
invariant is a ternary `atom` decodes in Core and is refused by closure. -/
theorem decodeTrace_ne_embed :
    ∃ fuel j, Core.Wire.decodeTrace fuel j ≠
      (VE.CertificateWire.decodeClosureTrace fuel j).map embedTrace := by
  let c : Lean.Json := .arr #[.str "const", .str "a"]
  refine ⟨125, Lean.Json.mkObj [("rule", .str "closure-induct@1"), ("at", (0 : Nat)),
    ("sort", .str "s"), ("invariant", .arr #[.str "atom", .str "p", .arr #[c, c, c]]),
    ("children", .arr #[])], fun h => ?_⟩
  have h' := congrArg Except.toBool h
  revert h'
  decide

end VE.Closure.CoreEquiv
