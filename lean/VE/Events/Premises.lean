import VE.Events.Decl
import VE.Norms.Prefix

/-! The generated premises `Ev_V` (docs/spec/events-time-causation.md 1.4, 6.1): the calendar
premises (order, consecutive named dates, adjacency) and the conventions (one day per event, one
beginning and one end per state, no end before the beginning, the two link conventions), each
labelled `events:<name>`; embeddings of a structure into the calendar (1.5); and the theorems that every
embedding satisfies the calendar premises and that named dates are ordered as W6a orders them. -/
namespace VE.Events
open VE.Norms (Sat)
open VE.Time (Civil dateMax)
universe u

def bin (p : String) (i j : Nat) : VE.Formula := .binary p (.var i) (.var j)

def irreflexiveF (V : EventsEnv) : VE.Formula := .all V.day (.not (bin V.before 0 0))
def transitiveF (V : EventsEnv) : VE.Formula :=
  .all V.day (.all V.day (.all V.day
    (.implies (.and (bin V.before 2 1) (bin V.before 1 0)) (bin V.before 2 0))))
def linearF (V : EventsEnv) : VE.Formula :=
  .all V.day (.all V.day (.or (bin V.before 1 0) (.or (.eq (.var 1) (.var 0)) (bin V.before 0 1))))
def dateFactF (V : EventsEnv) (D D' : Civil) : VE.Formula := .binary V.before (dateConst D) (dateConst D')
def adjacentF (V : EventsEnv) (D D' : Civil) : VE.Formula :=
  .all V.day (.not (.and (.binary V.before (dateConst D) (.var 0)) (.binary V.before (.var 0) (dateConst D'))))
/-- `∀x. ∀t. role(x,t) → ∀u. role(x,u) → t = u` (guarded). -/
def oneRoleF (V : EventsEnv) (sort role : String) : VE.Formula :=
  .all sort (.all V.day (.implies (bin role 1 0)
    (.all V.day (.implies (bin role 2 0) (.eq (.var 1) (.var 0))))))
/-- `∀x. ∀t. begins(x,t) → ∀u. ends(x,u) → ¬ before(u,t)` (guarded). -/
def notBeforeBeginF (V : EventsEnv) (s : StateSort) : VE.Formula :=
  .all s.sort (.all V.day (.implies (bin s.begins 1 0)
    (.all V.day (.implies (bin s.ends 2 0) (.not (bin V.before 0 1))))))
/-- `∀x y. L(x,y) → ∀t. start(x,t) → ∀u. bound(y,u) → ¬ before(u,t)` (guarded). -/
def linkForwardF (V : EventsEnv) (l : Link) : VE.Formula :=
  match startRole V l.cause, boundRole V l.effect with
  | some st, some bd =>
    .all l.cause (.all l.effect (.implies (bin l.predicate 1 0)
      (.all V.day (.implies (bin st 2 0)
        (.all V.day (.implies (bin bd 2 0) (.not (bin V.before 0 1))))))))
  | _, _ => .top
/-- `∀x y. N(x,y) → C(x,y)`. -/
def linkWeakerF (n c : Link) : VE.Formula :=
  .all n.cause (.all n.effect (.implies (bin n.predicate 1 0) (bin c.predicate 1 0)))
def weakerPairs (V : EventsEnv) : List (Link × Link) :=
  (V.links.filter (fun l => l.form == LinkForm.necessary)).flatMap fun n =>
    (V.links.filter (fun c => c.form == LinkForm.contributed && c.cause == n.cause && c.effect == n.effect)).map
      (fun c => (n, c))

def isoPair (D D' : Civil) : String := D.iso ++ ":" ++ D'.iso

def calendarLabelled (V : EventsEnv) : List (String × VE.Formula) :=
  [("events:irreflexive", irreflexiveF V), ("events:transitive", transitiveF V), ("events:linear", linearF V)] ++
  (consecutive V).map (fun p => ("events:date:" ++ isoPair p.1 p.2, dateFactF V p.1 p.2)) ++
  ((consecutive V).filter (fun p => p.2.num == p.1.num + 1)).map
    (fun p => ("events:adjacent:" ++ isoPair p.1 p.2, adjacentF V p.1 p.2))

def conventionLabelled (V : EventsEnv) : List (String × VE.Formula) :=
  V.events.map (fun e => ("events:one_day:" ++ e.sort, oneRoleF V e.sort e.on)) ++
  V.states.flatMap (fun s => [("events:one_begin:" ++ s.sort, oneRoleF V s.sort s.begins),
    ("events:one_end:" ++ s.sort, oneRoleF V s.sort s.ends),
    ("events:not_before_begin:" ++ s.sort, notBeforeBeginF V s)]) ++
  V.links.map (fun l => ("events:link_forward:" ++ l.predicate, linkForwardF V l)) ++
  (weakerPairs V).map (fun p => ("events:link_weaker:" ++ p.1.predicate ++ ":" ++ p.2.predicate, linkWeakerF p.1 p.2))

def eventsLabelled (V : EventsEnv) : List (String × VE.Formula) := calendarLabelled V ++ conventionLabelled V
def orderPremises (V : EventsEnv) : List VE.Formula := [irreflexiveF V, transitiveF V, linearF V]
def calendarPremises (V : EventsEnv) : List VE.Formula := (calendarLabelled V).map (·.2)
def conventionPremises (V : EventsEnv) : List VE.Formula := (conventionLabelled V).map (·.2)
def eventsX (V : EventsEnv) : List VE.Formula := (eventsLabelled V).map (·.2)

/-- `num` numbers the days of `S` as civil days: one-to-one, within the calendar, `before` is `<`,
    and each named date denotes a day with its date's number. -/
def Embeds (V : EventsEnv) (S : VE.Structure.{u}) (num : S.Carrier → Nat) : Prop :=
  (∀ x y, S.domain V.day x → S.domain V.day y → num x = num y → x = y) ∧
  (∀ x, S.domain V.day x → num x ≤ dateMax) ∧
  (∀ x y, S.domain V.day x → S.domain V.day y → (S.relation V.before [x, y] ↔ num x < num y)) ∧
  (∀ D ∈ V.dates, ∃ x, S.constant (dateName D) = some x ∧ S.domain V.day x ∧ num x = D.num)

/-- T2b's claim: two days neither of which is before the other are the same day. -/
def unorderedSameF (V : EventsEnv) : VE.Formula :=
  .all V.day (.all V.day (.implies (.and (.not (bin V.before 1 0)) (.not (bin V.before 0 1)))
    (.eq (.var 1) (.var 0))))

/-! ## Proofs -/

theorem mem_dates_of_consecutive {V : EventsEnv} {p : Civil × Civil} (h : p ∈ consecutive V) :
    p.1 ∈ V.dates ∧ p.2 ∈ V.dates :=
  ⟨List.of_mem_zip h |>.1, List.mem_of_mem_tail (List.of_mem_zip h).2⟩

/-- Every embedding (so every calendar reading) satisfies the calendar premises. -/
theorem calendar_sat (E : VE.Environment) (V : EventsEnv) (hT : EventsTyped E V = true) (S : VE.Structure.{u})
    (hS : S.Admissible E) (num : S.Carrier → Nat) (hc : Embeds V S num) :
    Sat S (calendarPremises V) := by
  have _ := hS
  obtain ⟨inj, -, ord, dates⟩ := hc
  have hlt : (consecutive V).all (fun p => decide (p.1.num < p.2.num)) = true := by
    simp only [EventsTyped, Bool.and_eq_true] at hT; exact hT.2
  intro a ha
  simp only [calendarPremises, calendarLabelled, List.map_append, List.map_map, List.mem_append,
    List.map_cons, List.map_nil, List.mem_cons, List.mem_map, Function.comp, List.not_mem_nil, or_false,
    List.mem_filter] at ha
  rcases ha with ((rfl | rfl | rfl) | ⟨p, hp, rfl⟩) | ⟨p, ⟨hp, hadj⟩, rfl⟩
  · intro x hx ⟨v, w, hv, hw, hr⟩
    simp [VE.Term.denote] at hv hw; subst hv hw
    exact Nat.lt_irrefl _ ((ord _ _ hx hx).1 hr)
  · intro x hx y hy z hz ⟨⟨v, w, hv, hw, hr⟩, ⟨v', w', hv', hw', hr'⟩⟩
    simp [VE.Term.denote] at hv hw hv' hw'; subst hv hw hv' hw'
    exact ⟨x, z, by simp [VE.Term.denote], by simp [VE.Term.denote],
      (ord _ _ hx hz).2 (Nat.lt_trans ((ord _ _ hx hy).1 hr) ((ord _ _ hy hz).1 hr'))⟩
  · intro x hx y hy
    rcases Nat.lt_trichotomy (num x) (num y) with h | h | h
    · exact .inl ⟨x, y, rfl, rfl, (ord _ _ hx hy).2 h⟩
    · exact .inr (.inl ⟨x, rfl, by rw [inj _ _ hx hy h]; rfl⟩)
    · exact .inr (.inr ⟨y, x, rfl, rfl, (ord _ _ hy hx).2 h⟩)
  · obtain ⟨h1, h2⟩ := mem_dates_of_consecutive hp
    obtain ⟨x, hx, dx, nx⟩ := dates _ h1
    obtain ⟨y, hy, dy, ny⟩ := dates _ h2
    have := List.all_eq_true.1 hlt p hp
    exact ⟨x, y, hx, hy, (ord _ _ dx dy).2 (by simp at this; omega)⟩
  · obtain ⟨h1, h2⟩ := mem_dates_of_consecutive hp
    obtain ⟨x, hx, dx, nx⟩ := dates _ h1
    obtain ⟨y, hy, dy, ny⟩ := dates _ h2
    intro t ht ⟨⟨v, w, hv, hw, hr⟩, ⟨v', w', hv', hw', hr'⟩⟩
    simp [dateConst, VE.Term.denote] at hv hw hv' hw'
    rw [hx] at hv; rw [hy] at hw'; cases hv; cases hw'; subst hw hv'
    have := (ord _ _ dx ht).1 hr; have := (ord _ _ ht dy).1 hr'
    simp at hadj; omega

theorem chain_head {β : Type} (R : β → β → Prop) (trans : ∀ a b c, R a b → R b c → R a c) :
    ∀ (rest : List β) (a : β), (∀ p ∈ (a :: rest).zip rest, R p.1 p.2) → ∀ b ∈ rest, R a b
  | [], _, _, b, hb => absurd hb List.not_mem_nil
  | c :: rest, a, h, b, hb => by
    have hac : R a c := h (a, c) (by simp)
    rcases List.mem_cons.1 hb with hb | hb
    · rw [hb]; exact hac
    · exact trans _ _ _ hac (chain_head R trans rest c (fun p hp => h p (List.mem_cons_of_mem _ hp)) b hb)

/-- The positions of a list whose consecutive pairs are related, for a transitive relation. -/
theorem chain_positions {β : Type} (R : β → β → Prop) (trans : ∀ a b c, R a b → R b c → R a c) :
    ∀ (l : List β), (∀ p ∈ l.zip l.tail, R p.1 p.2) → ∀ x ∈ l, ∀ y ∈ l, x = y ∨ R x y ∨ R y x
  | [], _, x, hx, _, _ => absurd hx List.not_mem_nil
  | a :: rest, h, x, hx, y, hy => by
    have head := chain_head R trans rest a h
    have tail := chain_positions R trans rest (fun p hp => h p (by
      cases rest with
      | nil => simp at hp
      | cons c rest => exact List.mem_cons_of_mem _ hp))
    rcases List.mem_cons.1 hx with hx | hx <;> rcases List.mem_cons.1 hy with hy | hy
    · exact .inl (hx.trans hy.symm)
    · rw [hx]; exact .inr (.inl (head _ hy))
    · rw [hy]; exact .inr (.inr (head _ hx))
    · exact tail x hx y hy

/-- Named dates are ordered exactly as the calendar orders them, in every structure of the calendar premises. -/
theorem datesOrder_iff (E : VE.Environment) (V : EventsEnv) (hT : EventsTyped E V = true) (S : VE.Structure.{u})
    (hS : S.Admissible E) (hp : Sat S (calendarPremises V)) (D D' : Civil) (hD : D ∈ V.dates)
    (hD' : D' ∈ V.dates) :
    (VE.Formula.binary V.before (dateConst D) (dateConst D')).denote S [] ↔ D.num < D'.num := by
  simp only [EventsTyped, Bool.and_eq_true, List.all_eq_true] at hT
  obtain ⟨⟨⟨⟨⟨⟨-, -⟩, -⟩, -⟩, -⟩, hdates⟩, hlt⟩ := hT
  have day : ∀ D ∈ V.dates, ∃ x, S.constant (dateName D) = some x ∧ S.domain V.day x := fun D hD =>
    hS.1 _ _ (by have := hdates D hD; simp at this; exact this.2)
  have mem : ∀ a ∈ calendarPremises V, a.denote S [] := hp
  simp only [calendarPremises, calendarLabelled, List.map_append, List.map_map, List.mem_append,
    List.map_cons, List.mem_cons, List.mem_map, Function.comp] at mem
  have irr := mem _ (.inl (.inl (.inl rfl)))
  have tr := mem _ (.inl (.inl (.inr (.inl rfl))))
  let B : Civil → Civil → Prop := fun a b => (VE.Formula.binary V.before (dateConst a) (dateConst b)).denote S []
  have unfoldB : ∀ a b, a ∈ V.dates → b ∈ V.dates → B a b → ∃ x y, S.constant (dateName a) = some x ∧
      S.constant (dateName b) = some y ∧ S.domain V.day x ∧ S.domain V.day y ∧ S.relation V.before [x, y] := by
    intro a b ha hb ⟨v, w, hv, hw, hr⟩
    obtain ⟨x, hx, dx⟩ := day a ha; obtain ⟨y, hy, dy⟩ := day b hb
    obtain rfl : x = v := Option.some_inj.mp (hx.symm.trans hv)
    obtain rfl : y = w := Option.some_inj.mp (hy.symm.trans hw)
    exact ⟨x, y, hx, hy, dx, dy, hr⟩
  have notSelf : ∀ a ∈ V.dates, ¬ B a a := by
    intro a ha h
    obtain ⟨x, y, hx, hy, dx, -, hr⟩ := unfoldB a a ha ha h
    obtain rfl : x = y := Option.some_inj.mp (hx.symm.trans hy)
    exact irr _ dx ⟨_, _, rfl, rfl, hr⟩
  have transB : ∀ a b c, a ∈ V.dates → b ∈ V.dates → c ∈ V.dates → B a b → B b c → B a c := by
    intro a b c ha hb hc h1 h2
    obtain ⟨x, y, hx, hy, dx, dy, r1⟩ := unfoldB a b ha hb h1
    obtain ⟨y', z, hy', hz, -, dz, r2⟩ := unfoldB b c hb hc h2
    obtain rfl : y = y' := Option.some_inj.mp (hy.symm.trans hy')
    obtain ⟨_, _, h, h', r⟩ := tr _ dx _ dy _ dz ⟨⟨_, _, rfl, rfl, r1⟩, ⟨_, _, rfl, rfl, r2⟩⟩
    simp [VE.Term.denote] at h h'; subst h h'
    exact ⟨_, _, hx, hz, r⟩
  let R : Civil → Civil → Prop := fun a b => (a ∈ V.dates ∧ b ∈ V.dates) ∧ (B a b ∧ a.num < b.num)
  have pos := chain_positions R (fun a b c h1 h2 => ⟨⟨h1.1.1, h2.1.2⟩,
      transB a b c h1.1.1 h1.1.2 h2.1.2 h1.2.1 h2.2.1, Nat.lt_trans h1.2.2 h2.2.2⟩)
    V.dates (fun p hp => by
      obtain ⟨h1, h2⟩ := mem_dates_of_consecutive hp
      refine ⟨⟨h1, h2⟩, mem _ (.inl (.inr ⟨p, hp, rfl⟩)), ?_⟩
      have := hlt p hp; simp at this; exact this) D hD D' hD'
  rcases pos with rfl | ⟨-, h, lt⟩ | ⟨-, h, lt⟩
  · exact ⟨fun h => absurd h (notSelf _ hD), fun h => absurd h (Nat.lt_irrefl _)⟩
  · exact ⟨fun _ => lt, fun _ => h⟩
  · refine ⟨fun h' => absurd (transB D D' D hD hD' hD h' h) (notSelf _ hD), fun h' => ?_⟩
    exact absurd (Nat.lt_trans h' lt) (Nat.lt_irrefl _)

/-- One owner of the calendar: the generated order is W6a's chronological order. -/
theorem datesOrder_calendar (D D' : Civil) (hD : D.Proper) (hD' : D'.Proper) :
    D.num < D'.num ↔ D.Before D' :=
  (VE.Time.before_iff hD hD').symm

/-- T2b: the claim needs `linear` (with it dropped, `T2b` in `Examples.lean` finds a countermodel). -/
theorem unorderedSame_of_order (V : EventsEnv) (S : VE.Structure.{u}) (hp : Sat S (orderPremises V)) :
    (unorderedSameF V).denote S [] := by
  have lin := hp (linearF V) (by simp [orderPremises])
  intro x hx y hy ⟨h1, h2⟩
  rcases lin x hx y hy with h | ⟨v, hv, hw⟩ | h
  · exact absurd h h1
  · exact ⟨v, hv, hw⟩
  · exact absurd h h2

end VE.Events
