import ResponseShape

/-! The three formula-level English service rows. The outer envelope is fixed here;
the result is governed by the reader's status and code tables. -/
namespace ResponseShape.Schemas.EnglishLean
open Lean ResponseShape

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    n [obj, .required ["id", "status", "error"],
      closed [("id", .bool true), ("status", constS "error"), ("error", str)]],
    n [obj, .required ["id", "status", "result"],
      closed [("id", .bool true), ("status", constS "ok"), ("result", .bool true)]]]

def readFile : File where
  name := "english.read.json"
  comment := some "Lean English reading response."
  top := [("row", «row»)]
  defs := []

def grammarFile : File where
  name := "english.grammar.json"
  comment := some "Lean English grammar response."
  top := [("row", «row»)]
  defs := []

def checkFile : File where
  name := "english.check.json"
  comment := some "Lean English candidate check response."
  top := [("row", «row»)]
  defs := []

end ResponseShape.Schemas.EnglishLean
