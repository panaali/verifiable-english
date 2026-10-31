/-! Stage markers of the readings admission (reviews/dri-decisions-20261029-scale-admission-profile.md item 2).
The production stage functions (`admitS2`, `admitS2Of`, `admitSDOf`, `admitNDFull`, and each set's distinguishing
models in `validateResultBy`) run their work through `stage`, and the component loops of `Run.lean` through `part`.
Each writes a marker line to stderr around the work (`dbgTrace`); its value is the work's own (`stage_eq`,
`part_eq`), so no answer and no theorem reads a marker. `ve_service` reads the markers (`VE.Service.StageTimes`):
timed into JSON lines under `VE_READINGS_STAGE_TIMES=1`, passed through raw under `=markers`, dropped otherwise. -/
namespace VE.Readings.Stage

/-- The prefix of every marker line. -/
def marker : String := "ve-stage "

/-- `work ()` between the markers `<opening> <name>` and `<closing> <status> <name>`, `status` the result's (`ok`,
    `error`): the closing marker reads the result, so the work runs between the two. -/
def around (opening closing name : String) (work : Unit → Except String α) : Except String α :=
  dbgTrace s!"{marker}{opening} {name}" fun _ =>
    let r := work ()
    dbgTrace s!"{marker}{closing} {if r matches .ok _ then "ok" else "error"} {name}" fun _ => r

/-- A stage's work: `begin <name>` ... `end <status> <name>`. -/
def stage (name : String) (work : Unit → Except String α) : Except String α := around "begin" "end" name work

/-- A component's work: `enter <name>` ... `leave <status> <name>`; the stages between belong to component `name`. -/
def part (name : String) (work : Unit → Except String α) : Except String α := around "enter" "leave" name work

theorem stage_eq (name : String) (work : Unit → Except String α) : stage name work = work () := rfl

theorem part_eq (name : String) (work : Unit → Except String α) : part name work = work () := rfl

end VE.Readings.Stage
