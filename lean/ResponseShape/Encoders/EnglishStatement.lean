import ResponseShape.Encoders.Common
import VE.EnglishGrammar.Norm.Run

/-! The `english.statement` mode (`VE.EnglishGrammar.Norm.Run.statementCaseReported`) against
`english.statement.json#/row` (docs/spec/en-e3-norm.md 2.3, recipe step 3): every row the mode writes fits the
shape, each status's members typed, the rule rows' spans included. -/
namespace ResponseShape.Encoders.EnglishStatement
open Lean ResponseShape ResponseShape.Skeletons VE.EnglishGrammar VE.EnglishGrammar.Norm

variable {req : Json}

abbrev treeRowSkel : Skel := skel% "english.statement.json#/$defs/tree_row"
abbrev identitiesSkel : Skel := skel% "english.statement.json#/$defs/identities"
abbrev answerSkel : Skel := skel% "english.statement.json#/$defs/answer"

mutual
theorem treeRows_fits (tags : Array String) : (start : Nat) → (t : VE.Grammar.Tree Tok) →
    ∀ x ∈ (VE.EnglishGrammar.Run.treeRows tags start t).1, Fits req treeRowSkel x
  | _, .leaf _ => by simp [VE.EnglishGrammar.Run.treeRows]
  | start, .node r kids => by
    intro x hx
    simp only [VE.EnglishGrammar.Run.treeRows, List.mem_cons] at hx
    rcases hx with rfl | h
    · fits
    · exact kidsRows_fits tags start kids x h
theorem kidsRows_fits (tags : Array String) : (start : Nat) → (ts : List (VE.Grammar.Tree Tok)) →
    ∀ x ∈ (VE.EnglishGrammar.Run.kidsRows tags start ts).1, Fits req treeRowSkel x
  | _, [] => by simp [VE.EnglishGrammar.Run.kidsRows]
  | start, t :: ts => by
    intro x hx
    simp only [VE.EnglishGrammar.Run.kidsRows, List.mem_append] at hx
    rcases hx with h | h
    · exact treeRows_fits tags start t x h
    · exact kidsRows_fits tags _ ts x h
end

theorem treeJson_fits (tags : Array String) (t : VE.Grammar.Tree Tok) :
    Fits req (.arr [] treeRowSkel) (VE.EnglishGrammar.Run.treeJson tags t) := by
  unfold VE.EnglishGrammar.Run.treeJson
  exact Fits.arrList (treeRows_fits tags 0 t)

theorem spanRow_fits (u : UnformalisedSpan) :
    Fits req (skel% "english.statement.json#/$defs/span_row") (Run.spanRow u) := by
  unfold Run.spanRow Run.placeText
  cases u.place <;> fits

/-- A decoded case's identities, with any source's SHA-256 before them, fit the identities' shape. -/
theorem case_identities (j : Json) :
    OkP (fun c : VE.EnglishGrammar.Run.Case => ∀ s : String,
      Fits req identitiesSkel (Json.mkObj ([("source_sha256", Json.str s)] ++ c.identities)))
      (VE.EnglishGrammar.Run.decodeCase j) := by
  unfold VE.EnglishGrammar.Run.decodeCase
  okfits
  all_goals (intro s; fits)

abbrev rowSkel : Skel :=
  .alt [skel% "english.statement.json#/$defs/rule_row", skel% "english.statement.json#/$defs/precedence_row"]

/-- A `one` answer's rows hold no translation-mode statement (`oneSpansOf` refuses one). -/
theorem noSource_of_oneSpansOf {lexed : Except Reject (Array (Array Spanned))} {rs : List NormStatement}
    {sps : List (Nat × Nat)} (h : Run.oneSpansOf lexed rs = some sps) : ∀ r ∈ rs, ∀ cs, r ≠ .source cs := by
  intro r hr cs0 heq
  subst heq
  unfold Run.oneSpansOf at h
  simp only [] at h
  split at h
  · cases h
  · rename_i hc
    simp only [Bool.or_eq_true, not_or, List.any_eq_true, not_exists, not_and] at hc
    exact absurd rfl (hc.1 _ hr)

/-- A `one` answer's rows hold no translation-mode statement (`oneSpans` refuses one). -/
theorem noSource_of_oneSpans {source : String} {rs : List NormStatement} {sps : List (Nat × Nat)}
    (h : Run.oneSpans source rs = some sps) : ∀ r ∈ rs, ∀ cs, r ≠ .source cs :=
  noSource_of_oneSpansOf h

theorem rows_fits (rs : List NormStatement) (sps : List (Nat × Nat)) (h : ∀ r ∈ rs, ∀ cs, r ≠ .source cs) :
    Fits req (.arr [] rowSkel) (Json.arr ((rs.zip sps).map fun (r, sp) => Run.statementRow rs sp r).toArray) := by
  apply Fits.arrList
  intro x hx
  obtain ⟨⟨r, sp⟩, hp, rfl⟩ := List.mem_map.mp hx
  have hr := (List.of_mem_zip hp).1
  cases r with
  | rule hd cl => simp only [Run.statementRow, Clause.wire]; fits
  | precedence a b => simp only [Run.statementRow]; fits
  | source cs0 => exact absurd rfl (h _ hr cs0)

section outcome
variable (cs : VE.EnglishGrammar.Run.Case) (tags : Thunk (Array String)) (source : String)
  (lexed : Except Reject (Array (Array Spanned))) (ids : Json)
  (hids : Fits req identitiesSkel ids)
include hids

/-- The class lookup of a literal code, computed. -/
macro "coded_simp" : tactic =>
  `(tactic|simp only [VE.EnglishGrammar.Run.status, VE.EnglishGrammar.Run.coded, VE.EnglishGrammar.Run.codeClasses,
    VE.EnglishGrammar.Run.statementCodeRows, List.cons_append, List.nil_append, List.lookup, String.reduceBEq,
    Option.toList, List.map_cons, List.map_nil])

theorem misplaced_fits (f : BlockFault) :
    Fits req answerSkel (Json.mkObj (Run.outcomeFields cs tags source lexed (.misplaced f) ++ [("identities", ids)])) := by
  cases f <;> simp only [Run.outcomeFields, BlockFault.code, BlockFault.text, BlockFault.sentence?] <;>
    coded_simp <;> fits using hids

theorem lexical_fits (r : Reject) :
    Fits req answerSkel (Json.mkObj (Run.outcomeFields cs tags source lexed (.lexical r) ++ [("identities", ids)])) := by
  cases r <;> simp only [Run.outcomeFields, VE.EnglishGrammar.Run.lexicalSpan, Reject.code] <;> coded_simp <;> fits using hids

theorem invalid_fits (g : GrammarFault) :
    Fits req answerSkel (Json.mkObj (Run.outcomeFields cs tags source lexed (.invalidGrammar g) ++ [("identities", ids)])) := by
  cases g <;> simp only [Run.outcomeFields, VE.EnglishGrammar.Run.invalidFields, VE.EnglishGrammar.Run.faultName,
    VE.EnglishGrammar.Run.failureJson] <;> coded_simp <;> (repeat' split) <;> fits using hids

theorem stopped_fits (i : Nat) (o : VE.Grammar.Outcome Tok Reject Piece) :
    Fits req answerSkel (Json.mkObj (Run.outcomeFields cs tags source lexed (.stopped i o) ++ [("identities", ids)])) := by
  cases o with
  | rejected r =>
    cases r <;> simp only [Run.outcomeFields, Run.stoppedFields, Reject.code] <;> coded_simp <;>
      (repeat' split) <;> fits using hids
  | _ =>
    simp only [Run.outcomeFields, Run.stoppedFields, VE.EnglishGrammar.Run.budgetFields] <;> coded_simp <;>
      fits using hids, treeJson_fits

theorem ok_fits (rs : List NormStatement) :
    Fits req answerSkel (Json.mkObj (Run.outcomeFields cs tags source lexed (.ok rs) ++ [("identities", ids)])) := by
  simp only [Run.outcomeFields]
  split
  · split
    · rename_i sps h
      have hs := noSource_of_oneSpansOf h
      simp only [VE.EnglishGrammar.Run.status, List.cons_append, List.nil_append]
      fits using hids, rows_fits
    · coded_simp
      fits using hids
  · split
    · unfold Run.decoderCode
      split <;> coded_simp <;> fits using hids
    · coded_simp
      fits using hids, spanRow_fits

theorem outcome_fits (o : NormOutcome) :
    Fits req answerSkel (Json.mkObj (Run.outcomeFields cs tags source lexed o ++ [("identities", ids)])) := by
  cases o
  · exact ok_fits cs tags source lexed ids hids _
  · exact invalid_fits cs tags source lexed ids hids _
  · exact lexical_fits cs tags source lexed ids hids _
  · exact stopped_fits cs tags source lexed ids hids _ _
  · exact misplaced_fits cs tags source lexed ids hids _

end outcome

theorem answer_fits (id : String) (cs : VE.EnglishGrammar.Run.Case) (source : String)
    (hc : ∀ s : String, Fits req identitiesSkel (Json.mkObj ([("source_sha256", Json.str s)] ++ cs.identities))) :
    Fits req Skeletons.englishStatement (Run.answer id cs source) := by
  have hids := hc (VE.CertificateWire.sha256 source.toUTF8)
  unfold Run.answer Run.answerWith VE.Route.Wire.ok
  split
  · simp only [VE.EnglishGrammar.Run.invalidOverlayFields]
    coded_simp
    fits
    all_goals exact hids
  · fits
    all_goals exact outcome_fits cs _ source _ _ hids _

/-- The request decoder keeps `decodeCase`'s case, so its identities fit. -/
theorem request_identities (j : Json) :
    OkP (fun r : String × VE.EnglishGrammar.Run.Case × String => ∀ s : String,
      Fits req identitiesSkel (Json.mkObj ([("source_sha256", Json.str s)] ++ r.2.1.identities)))
      (Run.statementRequest j) := by
  unfold Run.statementRequest
  okfits
  all_goals exact case_identities j _ (by assumption)

/-- Every row the mode writes fits `english.statement.json#/row` (docs/spec/en-e3-norm.md section 4). -/
theorem statementCaseReported_fits : ∀ j : Json,
  ResponseShape.Fits j ResponseShape.Skeletons.englishStatement (Run.statementCaseReported j) := by
  intro j
  unfold Run.statementCaseReported
  split
  · rename_i row h
    unfold Run.statementCase at h
    cases hr : Run.statementRequest j with
    | error e => rw [hr] at h; cases h
    | ok r =>
      rw [hr] at h
      obtain ⟨id, cs, source⟩ := r
      cases h
      exact answer_fits id cs source (request_identities j _ hr)
  · fits

end ResponseShape.Encoders.EnglishStatement
