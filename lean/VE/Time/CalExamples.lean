import VE.Time.Document

/-! Checks of the ground date expressions (date-arith: `Calendar`'s month offsets, weekdays and
`parseIsoFrom`, `Wire`'s `elabCal`, `cal`, `cal_cmp` and the input dates bound into a statement's
identity). Each `#guard` fails the build when a computed date, a refusal or an identity changes,
including at the boundaries a planted off-by-one error would move: a day, a month end, a leap day and a
birthday. -/
namespace VE.Time.CalExamples
open Lean VE.Time VE.Time.Wire

def p (s : String) : Json := (Json.parse s).toOption.getD .null

def cal (s : String) : Option Civil := (elabCal VE.Limits.maxDepth (p s)).toOption

def calError (s : String) : String :=
  match elabCal VE.Limits.maxDepth (p s) with
  | .error e => e
  | .ok _ => "accepted"

/-! ## Calendar -/

-- `parseIsoFrom`: the lower year bound; `parseIso` is from 1970.
#guard (parseIsoFrom minGroundYear "1900-01-01").toOption == some ⟨1900, 1, 1⟩
#guard (parseIsoFrom minGroundYear "1899-12-31").toOption == none
#guard (match parseIsoFrom minGroundYear "1899-12-31" with | .error e => e == "DateRange(1899-12-31)" | _ => false)
#guard (match parseIsoFrom minGroundYear "1900-02-29" with | .error e => e == "InvalidDate(1900-02-29)" | _ => false)
#guard (parseIsoFrom minGroundYear "1960-02-29").toOption == some ⟨1960, 2, 29⟩
#guard (parseIsoFrom 1970 "1969-12-31").toOption == none
#guard (parseIso "1969-12-31").toOption == none
#guard (parseIso "1970-01-01").toOption == some ⟨1970, 1, 1⟩
#guard (parseIso "9999-12-31").toOption == some ⟨9999, 12, 31⟩
#guard minGroundYear == 1900

-- `Civil.Ground`: 1900..9999 with a valid month and day; 1900 is not a leap year, 2000 is.
#guard decide (Civil.Ground ⟨1900, 1, 1⟩)
#guard decide (Civil.Ground ⟨9999, 12, 31⟩)
#guard decide (Civil.Ground ⟨2000, 2, 29⟩)
#guard !decide (Civil.Ground ⟨1900, 2, 29⟩)
#guard !decide (Civil.Ground ⟨1899, 12, 31⟩)
#guard !decide (Civil.Ground ⟨10000, 1, 1⟩)
#guard !decide (Civil.Ground ⟨2000, 0, 1⟩)
#guard !decide (Civil.Ground ⟨2000, 13, 1⟩)
#guard !decide (Civil.Ground ⟨2000, 1, 0⟩)
#guard !decide (Civil.Ground ⟨2001, 4, 31⟩)

-- The decidable order, for dates of any year.
#guard decide (Civil.Before ⟨1960, 6, 26⟩ ⟨1960, 6, 27⟩)
#guard !decide (Civil.Before ⟨1960, 6, 27⟩ ⟨1960, 6, 27⟩)
#guard decide (Civil.Before ⟨1960, 5, 31⟩ ⟨1960, 6, 1⟩)
#guard decide (Civil.Before ⟨1959, 12, 31⟩ ⟨1960, 1, 1⟩)
#guard !decide (Civil.Before ⟨1960, 1, 1⟩ ⟨1959, 12, 31⟩)

-- `addMonths`: the kept day; a missing day by reading; signed offsets; the year boundary.
#guard Civil.addMonths ⟨2025, 1, 31⟩ 2 none == some ⟨2025, 3, 31⟩
#guard Civil.addMonths ⟨2025, 1, 31⟩ 1 none == none
#guard Civil.addMonths ⟨2025, 1, 31⟩ 1 (some .last) == some ⟨2025, 2, 28⟩
#guard Civil.addMonths ⟨2025, 1, 31⟩ 1 (some .next) == some ⟨2025, 3, 1⟩
#guard Civil.addMonths ⟨2025, 1, 30⟩ 1 (some .next) == some ⟨2025, 3, 1⟩
#guard Civil.addMonths ⟨2025, 1, 28⟩ 1 none == some ⟨2025, 2, 28⟩
#guard Civil.addMonths ⟨2025, 3, 31⟩ 1 (some .last) == some ⟨2025, 4, 30⟩
#guard Civil.addMonths ⟨2025, 3, 31⟩ 1 (some .next) == some ⟨2025, 5, 1⟩
#guard Civil.addMonths ⟨2025, 12, 15⟩ 1 none == some ⟨2026, 1, 15⟩
#guard Civil.addMonths ⟨2025, 11, 15⟩ 1 none == some ⟨2025, 12, 15⟩
#guard Civil.addMonths ⟨2026, 1, 15⟩ (-1) none == some ⟨2025, 12, 15⟩
#guard Civil.addMonths ⟨2026, 1, 15⟩ (-13) none == some ⟨2024, 12, 15⟩
#guard Civil.addMonths ⟨2026, 3, 31⟩ (-1) (some .last) == some ⟨2026, 2, 28⟩
#guard Civil.addMonths ⟨0, 1, 1⟩ (-1) none == none
#guard Civil.addMonths ⟨0, 1, 1⟩ 0 none == some ⟨0, 1, 1⟩
-- leap days: 29 February plus whole years.
#guard Civil.addMonths ⟨1960, 2, 29⟩ 768 none == some ⟨2024, 2, 29⟩
#guard Civil.addMonths ⟨1960, 2, 29⟩ 792 none == none
#guard Civil.addMonths ⟨1960, 2, 29⟩ 792 (some .last) == some ⟨2026, 2, 28⟩
#guard Civil.addMonths ⟨1960, 2, 29⟩ 792 (some .next) == some ⟨2026, 3, 1⟩
#guard Civil.addMonths ⟨1896, 2, 29⟩ 48 none == none
#guard Civil.addMonths ⟨1996, 2, 29⟩ 48 none == some ⟨2000, 2, 29⟩
-- birthdays: the 66th birthday of a person born 27 June 1960.
#guard Civil.addMonths ⟨1960, 6, 27⟩ 792 none == some ⟨2026, 6, 27⟩

-- `weekday` (0 = Monday): 1970-01-01 was a Thursday; 23 November 2026 is a Monday.
#guard Civil.weekday ⟨1970, 1, 1⟩ == 3
#guard Civil.weekday ⟨1970, 1, 5⟩ == 0
#guard Civil.weekday ⟨2026, 11, 23⟩ == 0
#guard Civil.weekday ⟨2026, 3, 1⟩ == 6

-- `nthWeekday`: the qualifying week's third Monday in September; boundaries of the month and arguments.
#guard nthWeekday 3 0 9 2026 == some ⟨2026, 9, 21⟩
#guard nthWeekday 1 0 9 2026 == some ⟨2026, 9, 7⟩
#guard nthWeekday 1 1 9 2026 == some ⟨2026, 9, 1⟩
#guard nthWeekday 4 0 2 2026 == some ⟨2026, 2, 23⟩
#guard nthWeekday 5 0 2 2026 == none
#guard nthWeekday 5 6 3 2026 == some ⟨2026, 3, 29⟩
#guard nthWeekday 1 6 3 2026 == some ⟨2026, 3, 1⟩
#guard nthWeekday 5 1 3 2026 == some ⟨2026, 3, 31⟩
#guard nthWeekday 0 0 9 2026 == none
#guard nthWeekday 1 7 9 2026 == none
#guard nthWeekday 1 0 0 2026 == none
#guard nthWeekday 1 0 13 2026 == none
#guard nthWeekday 1 0 9 1969 == none
#guard nthWeekday 1 3 1 1970 == some ⟨1970, 1, 1⟩
#guard nthWeekday 1 0 12 9999 == some ⟨9999, 12, 6⟩
#guard nthWeekday 1 0 1 10000 == none

/-! ## Ground date expressions -/

#guard (match monthEndOf "last" with | some (some .last) => true | _ => false)
#guard (match monthEndOf "next" with | some (some .next) => true | _ => false)
#guard (match monthEndOf "none" with | some none => true | _ => false)
#guard (match monthEndOf "first" with | none => true | _ => false)

#guard cal r#"["date", "1960-06-27"]"# == some ⟨1960, 6, 27⟩
#guard calError r#"["date", "1899-12-31"]"# == "DateRange(1899-12-31)"
#guard calError r#"["date", "1960-02-30"]"# == "InvalidDate(1960-02-30)"
#guard cal r#"["plus_months", ["date", "1960-06-27"], "792", "none"]"# == some ⟨2026, 6, 27⟩
#guard cal r#"["plus_months", ["date", "1960-02-29"], "792", "last"]"# == some ⟨2026, 2, 28⟩
#guard cal r#"["plus_months", ["date", "1960-02-29"], "792", "next"]"# == some ⟨2026, 3, 1⟩
#guard calError r#"["plus_months", ["date", "1960-02-29"], "792", "none"]"# == "MissingDay(plus 792 months)"
#guard calError r#"["plus_months", ["date", "1960-02-29"], "792", "first"]"# == "Invalid month-end reading"
#guard cal r#"["plus_months", ["date", "1960-06-27"], "-12", "none"]"# == some ⟨1959, 6, 27⟩
#guard calError r#"["plus_months", ["date", "1900-01-31"], "-1", "none"]"# == "DateRange(month offset)"
#guard calError r#"["plus_months", ["date", "9999-12-31"], "1", "none"]"# == "DateRange(month offset)"
#guard cal r#"["plus_months", ["date", "9999-11-30"], "1", "none"]"# == some ⟨9999, 12, 30⟩
#guard calError r#"["plus_months", ["date", "1960-06-27"], "x", "none"]"# != "accepted"
-- a day: the last day of the week beginning the third Monday in September 2026 is 27 September.
#guard cal r#"["plus_days", ["nth_weekday", 3, 0, 9, 2026], "6"]"# == some ⟨2026, 9, 27⟩
#guard cal r#"["plus_days", ["date", "2026-02-28"], "1"]"# == some ⟨2026, 3, 1⟩
#guard cal r#"["plus_days", ["date", "2024-02-28"], "1"]"# == some ⟨2024, 2, 29⟩
#guard cal r#"["plus_days", ["date", "2026-12-31"], "0"]"# == some ⟨2026, 12, 31⟩
#guard cal r#"["plus_days", ["date", "1970-01-01"], "2932896"]"# == some ⟨9999, 12, 31⟩
#guard calError r#"["plus_days", ["date", "1970-01-01"], "2932897"]"# == "DateRange(day offset)"
#guard calError r#"["plus_days", ["date", "9999-12-31"], "1"]"# == "DateRange(day offset)"
#guard calError r#"["plus_days", ["date", "2026-01-01"], "-1"]"# == "DateRange(day offset)"
#guard calError r#"["plus_days", ["date", "1969-12-31"], "1"]"# == "DateRange(day offset)"
-- a month end: the last day of the 18th month after the month of 31 January 2025.
#guard cal r#"["month_last", ["plus_months", ["month_first", ["date", "2025-01-31"]], "18", "none"]]"# ==
  some ⟨2026, 7, 31⟩
#guard cal r#"["month_last", ["date", "2024-02-10"]]"# == some ⟨2024, 2, 29⟩
#guard cal r#"["month_last", ["date", "1900-02-10"]]"# == some ⟨1900, 2, 28⟩
#guard cal r#"["month_first", ["date", "2024-02-10"]]"# == some ⟨2024, 2, 1⟩
#guard cal r#"["nth_weekday", 3, 0, 9, 2026]"# == some ⟨2026, 9, 21⟩
#guard calError r#"["nth_weekday", 5, 0, 2, 2026]"# == "Invalid nth weekday"
#guard calError r#"["nth_weekday", "3", 0, 9, 2026]"# != "accepted"
#guard calError r#"["nth_weekday", -1, 0, 9, 2026]"# != "accepted"
#guard calError r#"["cal", ["date", "2026-01-01"]]"# == "Invalid date expression"
#guard calError r#"["date", "2026-01-01", "x"]"# == "Invalid date expression"
#guard calError r#""2026-01-01""# == "Invalid date expression"
#guard (match elabCal 0 (p r#"["date", "2026-01-01"]"#) with | .error e => e == depthLimit | _ => false)
#guard (elabCal 1 (p r#"["date", "2026-01-01"]"#)).toOption == some ⟨2026, 1, 1⟩
#guard (match elabCal 1 (p r#"["month_first", ["date", "2026-01-01"]]"#) with | .error e => e == depthLimit | _ => false)

-- `calDay`: a day term's date is from 1970.
#guard (calDay (p r#"["date", "1970-01-01"]"#)).toOption == some ⟨1970, 1, 1⟩
#guard (calDay (p r#"["plus_months", ["date", "1960-06-27"], "792", "none"]"#)).toOption == some ⟨2026, 6, 27⟩
#guard (match calDay (p r#"["date", "1969-12-31"]"#) with
  | .error e => e == "DateRange(date expression before 1970)" | _ => false)

-- `CalOrder`, decided.
#guard decide (CalOrder "before" ⟨1960, 6, 26⟩ ⟨1960, 6, 27⟩)
#guard !decide (CalOrder "before" ⟨1960, 6, 27⟩ ⟨1960, 6, 27⟩)
#guard decide (CalOrder "after" ⟨1960, 6, 28⟩ ⟨1960, 6, 27⟩)
#guard !decide (CalOrder "after" ⟨1960, 6, 27⟩ ⟨1960, 6, 27⟩)
#guard decide (CalOrder "on" ⟨1960, 6, 27⟩ ⟨1960, 6, 27⟩)
#guard !decide (CalOrder "on" ⟨1960, 6, 27⟩ ⟨1960, 6, 28⟩)
#guard decide (CalOrder "on_or_before" ⟨1960, 6, 27⟩ ⟨1960, 6, 27⟩)
#guard !decide (CalOrder "on_or_before" ⟨1960, 6, 28⟩ ⟨1960, 6, 27⟩)
#guard decide (CalOrder "on_or_after" ⟨1960, 6, 27⟩ ⟨1960, 6, 27⟩)
#guard !decide (CalOrder "on_or_after" ⟨1960, 6, 26⟩ ⟨1960, 6, 27⟩)
#guard !decide (CalOrder "later" ⟨1960, 6, 27⟩ ⟨1960, 6, 27⟩)

def cmp (op a b : String) : Option Json := (elabCalCmp op (p a) (p b)).toOption.map encQ

def cmpError (op a b : String) : String :=
  match elabCalCmp op (p a) (p b) with
  | .error e => e
  | .ok _ => "accepted"

-- valid dates: today's date node over both day numbers (shown); a date before 1970: decided.
#guard cmp "before" r#"["date", "2026-06-26"]"# r#"["date", "2026-06-27"]"# ==
  some (p r#"["date_before", ["num", "day", "20630"], ["num", "day", "20631"]]"#)
#guard cmp "after" r#"["date", "2026-06-26"]"# r#"["date", "2026-06-27"]"# ==
  some (p r#"["date_after", ["num", "day", "20630"], ["num", "day", "20631"]]"#)
#guard cmp "on" r#"["date", "2026-06-26"]"# r#"["date", "2026-06-27"]"# ==
  some (p r#"["date_on", ["num", "day", "20630"], ["num", "day", "20631"]]"#)
#guard cmp "on_or_before" r#"["date", "2026-06-26"]"# r#"["date", "2026-06-27"]"# ==
  some (p r#"["date_no_later", ["num", "day", "20630"], ["num", "day", "20631"]]"#)
#guard cmp "on_or_after" r#"["date", "2026-06-26"]"# r#"["date", "2026-06-27"]"# ==
  some (p r#"["date_no_later", ["num", "day", "20631"], ["num", "day", "20630"]]"#)
#guard cmp "before" r#"["date", "1960-06-26"]"# r#"["date", "1960-06-27"]"# == some (p r#"["top"]"#)
#guard cmp "before" r#"["date", "1960-06-27"]"# r#"["date", "1960-06-27"]"# == some (p r#"["bottom"]"#)
#guard cmp "on_or_before" r#"["date", "1960-06-27"]"# r#"["date", "1960-06-27"]"# == some (p r#"["top"]"#)
#guard cmp "on_or_after" r#"["date", "1960-06-26"]"# r#"["date", "2026-06-27"]"# == some (p r#"["bottom"]"#)
#guard cmp "on" r#"["date", "1969-12-31"]"# r#"["date", "1969-12-31"]"# == some (p r#"["top"]"#)
#guard cmp "after" r#"["date", "1970-01-01"]"# r#"["date", "1969-12-31"]"# == some (p r#"["top"]"#)
#guard cmpError "later" r#"["date", "2026-06-26"]"# r#"["date", "2026-06-27"]"# == "Invalid date comparison later"
#guard cmpError "before" r#"["date", "1899-06-26"]"# r#"["date", "2026-06-27"]"# == "DateRange(1899-06-26)"
-- a birthday: a person born 27 June 1960 has attained 66 on 27 June 2026, not on 26 June.
#guard cmp "on_or_before" r#"["plus_months", ["date", "1960-06-27"], "792", "none"]"# r#"["date", "2026-06-27"]"# ==
  some (p r#"["date_no_later", ["num", "day", "20631"], ["num", "day", "20631"]]"#)
#guard decide (CalOrder "on_or_before" ⟨2026, 6, 27⟩ ⟨2026, 6, 27⟩) &&
  !decide (CalOrder "on_or_before" ⟨2026, 6, 27⟩ ⟨2026, 6, 26⟩)

/-! ## Statements: the `cal` term, the `cal_cmp` formula and the bound input dates -/

def env : Json := p r#"{"language": "ve.core@0.2", "profiles": ["order@0", "relational-fol@0", "time@0"],
  "spec_revision": "ve-v0.2-expand2-2026-09-25",
  "vocabulary": {"sorts": {}, "predicates": {},
    "constants": {"pa": {"sort": "$int", "unit": "day", "description": "pensionable-age date"}}},
  "unit_schema": "ve-units@1", "units": {"day": {"scale": "1", "display": {"kind": "iso_date"}}}}"#

def noDay : Json := p r#"{"language": "ve.core@0.2", "profiles": ["order@0", "relational-fol@0", "time@0"],
  "spec_revision": "ve-v0.2-expand2-2026-09-25",
  "vocabulary": {"sorts": {}, "predicates": {}, "constants": {}},
  "unit_schema": "ve-units@1", "units": {"bp": {"scale": "100", "display": {"kind": "percent"}}}}"#

/-- A statement decoded in `e`: its `Q`, meaning id, inputs and report claim, or the refusal. -/
def stmt (formula : String) (e : Json := env) : Except String (Json × String × List String × Json) := do
  let w ← decodeEnvironment e
  let a ← decodeQuantity w (Json.mkObj [("format", .str "ve-quantity@1"), ("formula", p formula)])
  pure (a.Q, a.meaningId, a.inputs, Document.claimJson "n" a "asserted")

def q (formula : String) : Option Json := (stmt formula).toOption.map (·.1)
def mid (formula : String) : Option String := (stmt formula).toOption.map (·.2.1)
def inputs (formula : String) : Option (List String) := (stmt formula).toOption.map (·.2.2.1)
def claim (formula : String) : Option Json := (stmt formula).toOption.map (·.2.2.2)
def refusal (formula : String) (e : Json := env) : String :=
  match stmt formula e with
  | .error m => m
  | .ok _ => "accepted"

#guard q r#"["date_on", ["const", "day", "pa"], ["cal", ["plus_months", ["date", "1960-06-27"], "792", "none"]]]"# ==
  some (p r#"["date_on", ["const", "day", "pa"], ["num", "day", "20631"]]"#)
#guard refusal r#"["date_on", ["const", "day", "pa"], ["cal", ["date", "1969-12-31"]]]"# ==
  "DateRange(date expression before 1970)"
#guard refusal r#"["date_on", ["const", "day", "pa"], ["cal", ["date", "2026-01-01"], "x"]]"# == "Invalid quantity term"
#guard q r#"["cal_cmp", "before", ["date", "1960-06-26"], ["date", "1960-06-27"]]"# == some (p r#"["top"]"#)
#guard refusal r#"["cal_cmp", "before", ["date", "1960-06-26"]]"# == "Invalid cal_cmp node"
#guard refusal r#"["cal_cmp", "before", ["date", "1960-06-26"], ["date", "1960-06-27"]]"# noDay ==
  "UnknownUnit(day)"
#guard refusal r#"["eq", ["cal", ["date", "2026-01-01"]], ["cal", ["date", "2026-01-01"]]]"# noDay == "UnknownUnit(day)"
-- the input dates: only the `date` leaves under `cal` and `cal_cmp`, in order; none for today's statements.
#guard inputs r#"["date_on", ["const", "day", "pa"], ["date", "2026-06-27"]]"# == some []
#guard inputs r#"["and", ["date_on", ["const", "day", "pa"], ["date", "2026-06-27"]],
  ["cal_cmp", "before", ["date", "1960-06-26"], ["plus_days", ["date", "1970-01-01"], "1"]]]"# ==
  some ["1960-06-26", "1970-01-01"]
#guard inputs r#"["date_on", ["const", "day", "pa"], ["cal", ["month_last", ["date", "2024-02-10"]]]]"# ==
  some ["2024-02-10"]
#guard calInputs 257 false (p r#"["x", ["date", "2026-01-01"]]"#) == []
#guard calInputs 257 true (p r#"["date", "2026-01-01"]"#) == ["2026-01-01"]
#guard calInputs 0 true (p r#"["date", "2026-01-01"]"#) == []
#guard calInputs 257 false (p r#"["cal", ["nth_weekday", 3, 0, 9, 2026]]"#) == []
-- the same `Q` from other case dates has another meaning id; a statement without them keeps today's object.
#guard q r#"["cal_cmp", "before", ["date", "1960-01-01"], ["date", "1960-06-27"]]"# ==
  q r#"["cal_cmp", "before", ["date", "1959-01-01"], ["date", "1960-06-27"]]"#
#guard mid r#"["cal_cmp", "before", ["date", "1960-01-01"], ["date", "1960-06-27"]]"# !=
  mid r#"["cal_cmp", "before", ["date", "1959-01-01"], ["date", "1960-06-27"]]"#
#guard mid r#"["top"]"# != mid r#"["cal_cmp", "before", ["date", "1960-01-01"], ["date", "1960-06-27"]]"#
#guard (do
    let w ← decodeEnvironment env
    let (m, _) ← statementIds w .top
    let (m', _) ← statementIds w .top ["1960-01-01"]
    pure (some m == mid r#"["top"]"# && m != m')).toOption == some true
#guard inputsField [] == []
#guard inputsField ["1960-01-01"] == [("inputs", toJson ["1960-01-01"])]
-- the report claim shows them (and only when there are some).
#guard (claim r#"["cal_cmp", "before", ["date", "1960-01-01"], ["date", "1960-06-27"]]"#).map
  (·.getObjValD "inputs") == some (p r#"["1960-01-01", "1960-06-27"]"#)
#guard (claim r#"["top"]"#).map (·.getObjVal? "inputs" |>.toOption) == some none

end VE.Time.CalExamples
