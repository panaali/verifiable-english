import VE.Calc.Data

/-! ME-4's fixtures (spec 13.2 to 13.4, plan ME-4), each check on both sides of its boundary. -/

namespace VE.Calc.TableExamples
open VE.Calc VE.Numbers

def t1Bytes : ByteArray := "judge,approved,score\n32B,true,3\n32B,false,5\n14B,true,\n14B,,4\n14B,yes,6\n".toUTF8
def t1Cols : List (String × ColType) := [("judge", .text), ("approved", .bool), ("score", .number)]
def t1 : DataDecl := ⟨"08dae9651d6c3931185d6b15dcaec6ba0de6bea682de1a5db567fd54d3d6a6ef", .csv, t1Cols⟩
def T1 : Table := (decodeCsv t1Cols t1Bytes).toOption.getD ⟨[], []⟩
def run (f : Filter) (a : Agg) (limit := 1000000) (hs := [(t1.handle, t1Bytes)]) (dd := t1) : Option Counted :=
  (runCounted limit hs dd f a).toOption
def refusal (r : Except String Counted) : String := match r with | .error e => (e.splitOn ":").head! | .ok _ => "ok"
def aggs : List Agg := [.count, .sum "score", .mean "score", .min "score", .max "score"]
def all5 (f : Filter) : List (Option Counted) := aggs.map (run f)
def ok (xs : List (Option Rat)) : List (Option Counted) := xs.map fun x => some (.ok x)

/-! T-1 (13.3): the digest pinned, and every filter's five aggregates; an absent or text `approved` cell is selected by
neither `approved` nor `not approved`, and an absent score leaves sum, mean, minimum and maximum undefined. -/
#guard VE.CertificateWire.sha256 t1Bytes = t1.handle
#guard all5 (.isText "judge" "7B") = ok [some 0, some 0, none, none, none]
#guard all5 (.isText "judge" "32B") = ok [some 2, some 8, some 4, some 3, some 5]
#guard all5 (.isTrue "approved") = ok [some 2, none, none, none, none]
#guard all5 (.isFalse "approved") = ok [some 1, some 5, some 5, some 5, some 5]
#guard all5 (.isNotText "judge" "32B") = ok [some 3, none, none, none, none]
#guard all5 (.notEquals "score" 3) = ok [some 3, some 15, some 5, some 4, some 6]
#guard all5 (.equals "score" 3) = ok [some 1, some 3, some 3, some 3, some 3]
#guard all5 .all = ok [some 5, none, none, none, none]
#guard all5 (.or (.isTrue "approved") (.isFalse "approved")) = ok [some 3, none, none, none, none]
#guard T1.select (.or (.isTrue "approved") (.isFalse "approved")) = T1.rows.take 3
#guard (T1.rows.drop 3).map (T1.cell · "approved") = [.absent, .text "yes"] ∧ T1.cell T1.rows[0]! "nope" = .absent

/-! Refusals: a wrong digest, an unregistered handle, an unknown column, bytes that do not decode. -/
#guard refusal (runCounted 9 [(t1.handle, "judge,approved,score\n32B,true,4\n".toUTF8)] t1 .all .count) = "DigestMismatch"
#guard refusal (runCounted 9 [] t1 .all .count) = "UnknownHandle"
#guard refusal (runCounted 9 [(t1.handle, t1Bytes)] t1 (.isText "jduge" "32B") .count) = "UnknownColumn"
#guard refusal (runCounted 9 [(t1.handle, t1Bytes)] t1 .all (.mean "scores")) = "UnknownColumn"
#guard refusal (runCounted 9 [(t1.handle, t1Bytes)] { t1 with format := .jsonl } .all .count) = "TableFormat"

/-! T-3 (13.3): `approved_32b` needs 12 visits and `mean_7b` 5; each budget boundary on both sides; budget 0 allows
nothing, even over no rows. -/
def approved32 : Filter := .and (.isText "judge" "32B") (.isTrue "approved")
#guard run approved32 .count 12 = some (.ok (some 1)) ∧ run approved32 .count 11 = some .exhausted
#guard run (.isText "judge" "7B") (.mean "score") 5 = some (.ok none)
#guard run (.isText "judge" "7B") (.mean "score") 4 = some .exhausted
#guard Agg.runB 0 ⟨[], []⟩ .all .count = none ∧ Agg.runB 1 ⟨[], []⟩ .all .count = some (some 0)

def counted (limit : Nat) (name : String) (f : Filter) (a : Agg) : Decl :=
  ⟨name, .counted (Thunk.mk fun _ => Agg.run T1 f a) ((run f a limit).getD .exhausted)⟩
def t3 (limit : Nat) : List Decl :=
  [counted limit "approved_32b" approved32 .count, ⟨"share", .defined (.div (.val "approved_32b") (.lit 2))⟩,
   counted limit "mean_7b" (.isText "judge" "7B") (.mean "score")]
def t3Claims : List Claim :=
  [.compare ⟨.eq, false⟩ (.val "approved_32b") (.lit 1), .compare ⟨.lt, false⟩ (.val "share") (.lit 1),
   .compare ⟨.lt, false⟩ (.val "mean_7b") (.lit 1),
   .compare ⟨.lt, false⟩ (.add (.val "mean_7b") (.val "share")) (.lit 1),
   .compare ⟨.lt, false⟩ (.add (.val "share") (.val "mean_7b")) (.lit 1)]
#guard t3Claims.map (Claim.run (t3 6)) = [.unknown (.limit .evaluations), .unknown (.limit .evaluations),
  .decided .undefined, .decided .undefined, .unknown (.limit .evaluations)]
#guard t3Claims.map (Claim.run (t3 1000000)) = [.decided .holds, .decided .holds, .decided .undefined,
  .decided .undefined, .decided .undefined]

/-! CSV (4.1): CRLF and a missing last line end read as LF; quoting; each malformed shape refused beside its nearest
accepted one; number and `bool` cells read exactly, any other text kept. -/
def csv (s : String) (cols := t1Cols) : Option Table := (decodeCsv cols s.toUTF8).toOption
def rows? (t : Option Table) : Option (List (List Cell)) := t.map (·.rows)
#guard rows? (csv "judge,approved,score\r\n32B,true,3\r\n32B,false,5\r\n14B,true,\r\n14B,,4\r\n14B,yes,6") = some T1.rows
#guard rows? (csv "score,judge,approved\n\"3\",\"a,\"\"b\"\"\",\"\"") = some [[.num 3, .text "a,\"b\"", .absent]]
#guard ["j,a,x\n", "j,a\n", "a,s\n", "j,s\n", "j,a,s,s\n", "j,a,s\n1,2", "j,a,s\n\"x,y,z", "j,a,s\n\"x\"y,,",
  "j,a,s\nx\"y,,", "j,a,s\nx\ry,,"].all (csv · [("j", .text), ("a", .bool), ("s", .number)] |>.isNone)
#guard rows? (csv "j,a,s\n\"x\",,\n" [("j", .text), ("a", .bool), ("s", .number)]) = some [[.text "x", .absent, .absent]]
#guard ["j,a,s\nx,,", "j,a,s\nx,,\n"].map (rows? <| csv · [("j", .text), ("a", .bool), ("s", .number)]) =
  List.replicate 2 (some [[.text "x", .absent, .absent]])
#guard ["j\nx", "j\n\"\"", "j\n"].map (rows? <| csv · [("j", .text)]) = [some [[.text "x"]], some [[.absent]], some []]
#guard ["!", "\t"].map (fun s => rows? (csv ("j\n" ++ s) [("j", .text)])) =
  [some [[.text "!"]], some [[.text "\t"]]]
#guard rows? (csv "s,j,a\n1,x,true" [("j", .text), ("a", .bool), ("s", .number)]) = some [[.num 1, .text "x", .bool true]]
#guard (decodeCsv t1Cols (ByteArray.mk #[0xff])).toOption.isNone
#guard ["0.30", "-1.5", "0", "007", "1e3", ".5", " 1"].map (readCell .number) =
  [.num (3/10), .num (-3/2), .num 0, .text "007", .text "1e3", .text ".5", .text " 1"]
#guard ["true", "false", "True", "1"].map (readCell .bool) = [.bool true, .bool false, .text "True", .text "1"]

/-! JSON lines (4.1): T-1 as JSON lines reads as the CSV does; a repeated or undeclared key and a nested value are
refused beside the accepted line. -/
def jsonl (s : String) : Option Table := (decodeJsonl t1Cols s.toUTF8).toOption
#guard rows? (jsonl ("{\"judge\":\"32B\",\"approved\":true,\"score\":3}\n{\"judge\":\"32B\",\"approved\":false,\"score\":5}\n" ++
  "{\"judge\":\"14B\",\"approved\":true}\r\n{\"judge\":\"14B\",\"approved\":null,\"score\":4}\n" ++
  "{\"score\":6,\"judge\":\"14B\",\"approved\":\"yes\"}\n")) = some T1.rows
#guard rows? (jsonl "{\"judge\":3,\"approved\":1,\"score\":0.30}") = some [[.text "3", .text "1", .num (3/10)]]
#guard rows? (jsonl "{\"judge\":true,\"approved\":\"x\",\"score\":false}") = some [[.text "true", .text "x", .text "false"]]
#guard ["{\"judge\":\"a\",\"judge\":\"b\"}", "{\"judges\":\"a\"}", "{\"x\":1,\"judge\":\"a\"}", "{\"judge\":\"a\",\"x\":1}",
  "{\"judge\":\"a\",\"x\":1,\"score\":2}", "{\"judge\":[\"a\"]}", "{\"judge\":\"a\"}x", "\n"].all
  (jsonl · |>.isNone)
#guard rows? (jsonl "{}") = some [[.absent, .absent, .absent]] ∧ rows? (jsonl "") = some []
#guard (jsonl "{}\n{}").map (·.rows.length) = some 2 ∧ (jsonl "{}").map (·.columns) = some ["judge", "approved", "score"]

/-! Table dimensions (14): one shared bound for both decoders; each boundary is accepting beside a refusal. -/
#guard [64, 65].map (fun n =>
  let cols : List (String × ColType) := (List.range n).map fun i => (s!"c{i}", .text)
  (decodeCsv cols ((",".intercalate (cols.map Prod.fst) ++ "\n").toUTF8)).toOption.isSome) = [true, false]
#guard [64, 65].map (fun n =>
  let cols : List (String × ColType) := (List.range n).map fun i => (s!"c{i}", .text)
  (decodeJsonl cols "{}".toUTF8).toOption.isSome) = [true, false]
#guard (tableDimensions 64 1000000).toOption.isSome ∧
  (tableDimensions 65 0).toOption.isNone ∧ (tableDimensions 0 1000001).toOption.isNone
#guard match decodeCsv [("j", .text)] ("j\n" ++ String.join (List.replicate 1000001 "x\n")).toUTF8 with
  | .error e => e == "TableFormat: too many rows"
  | .ok _ => false
#guard match decodeJsonl [("j", .text)] (String.join (List.replicate 1000001 "{}\n")).toUTF8 with
  | .error e => e == "TableFormat: too many rows"
  | .ok _ => false

/-! A synthetic 30-row trial: row i is in arm "drug" when i is even, at site A, B or C by i mod 3, responded unless
4 divides i, aged 40 + i. -/
def trialCols : List (String × ColType) := [("arm", .text), ("site", .text), ("responded", .bool), ("age", .number)]
def trial : Table := (csv ("arm,site,responded,age\n" ++ String.join ((List.range 30).map fun i =>
  s!"{if i % 2 = 0 then "drug" else "placebo"},{["A", "B", "C"][i % 3]!},{decide (i % 4 ≠ 0)},{40 + i}\n"))
  trialCols).getD ⟨[], []⟩
#guard [.all, .isText "arm" "drug", .isTrue "responded", .isFalse "responded", .and (.isText "arm" "drug")
  (.isTrue "responded"), .isNotText "site" "A", .or (.isText "site" "A") (.isText "site" "B"), .equals "age" 45,
  .notEquals "age" 45].map (Agg.run trial · .count) = [30, 15, 22, 8, 7, 20, 20, 1, 29].map some
#guard [.sum "age", .mean "age", .min "age", .max "age"].map (Agg.run trial (.isText "arm" "drug")) =
  [some 810, some 54, some 40, some 68]

/-! V-5 (13.2): each row's approved count, read through its own filter, over 243 rounds (ties up, three places) to
its printed pooled FA; the printed column is text, so its written places stay. A changed printed value fails. -/
def v5Csv : String := "judge,view,explanation,approved,pooled\n" ++ String.join (List.map (· ++ "\n")
  ["14B,S,none,151,0.621", "14B,K,none,155,0.638", "14B,V,none,136,0.560", "14B,N,none,144,0.593",
   "14B,F,none,127,0.523", "14B,S,attacker,127,0.523", "14B,K,attacker,121,0.498", "14B,V,attacker,124,0.510",
   "14B,N,attacker,127,0.523", "14B,F,attacker,90,0.370", "32B,S,none,62,0.255", "32B,K,none,62,0.255",
   "32B,V,none,71,0.292", "32B,N,none,63,0.259", "32B,F,none,60,0.247", "32B,S,attacker,31,0.128",
   "32B,K,attacker,43,0.177", "32B,V,attacker,52,0.214", "32B,N,attacker,41,0.169", "32B,F,attacker,37,0.152"])
def v5 (text : String) : List Outcome :=
  let cols := [("judge", .text), ("view", .text), ("explanation", .text), ("approved", .number), ("pooled", .text)]
  let dd : DataDecl := ⟨VE.CertificateWire.sha256 text.toUTF8, .csv, cols⟩
  let T := (decodeCsv cols text.toUTF8).toOption.getD ⟨[], []⟩
  T.rows.map fun r =>
    let f := ["judge", "view", "explanation"].foldr (fun c g => match T.cell r c with
      | .text v => .and (.isText c v) g
      | _ => g) .all
    let n := (runCounted 1000000 [(dd.handle, text.toUTF8)] dd f (.sum "approved")).toOption.getD .exhausted
    match T.cell r "pooled" with
    | .text p => match VE.Time.parseDecimal p with
      | .ok d => Claim.run [⟨"a", .counted (Thunk.mk fun _ => Agg.run T f (.sum "approved")) n⟩]
          (.rounds .tiesUp (.div (.val "a") (.lit 243)) (Printed.ofDec d))
      | .error _ => .decided .undefined
    | _ => .decided .undefined
#guard v5 v5Csv = List.replicate 20 (.decided .holds)
#guard (v5 (v5Csv.replace "0.621" "0.622")).take 2 = [.decided .fails, .decided .holds]

end VE.Calc.TableExamples
