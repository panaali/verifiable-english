/-! The command reader's codes and texts (docs/spec/commands-imperatives.md section 4), byte-identical to Python's
`parse_speech` where Python has the case. The relayed message is `<code>: <text>`. -/

namespace VE.Commands.Texts

def nonAscii : String × String := ("InvalidInput", "non-ASCII speech wording")
def empty : String × String := ("InvalidInput", "speech wording")
def permission : String × String := ("PermissionNotCommand", "use an equality-guarded W1 rule")
def please : String × String := ("InvalidInput", "please needs author approval")
def unbound : String × String := ("UnboundSlot", "you")
def addressee : String × String := ("TypeMismatch", "addressee")
def actsMatch : String × String := ("AmbiguousDerivation", "multiple declared acts match")
def coordinated : String × String := ("CoordinatedActs", "split into two commands")
def noReading : String × String := ("InvalidInput", "no single speech-act reading")
def missingObligation : String := "MissingObligationRole"
def missingPermission : String := "MissingPermissionRole"
/-- The proof task's act (SA 2.1), the text of its `MissingObligationRole`. -/
def proofAct : String := "{0} submit a proof of {1}"
/-- No record, or two, has the sentence's target; the wire encoder writes the request's unit as the text (O1). -/
def queryMismatch : String × String := ("QueryMismatch", "")

/-- Every code the reader writes, with its class: `VEError`, the class Python raises for each today. -/
def codeClasses : List (String × String) :=
  [("InvalidInput", "VEError"), ("PermissionNotCommand", "VEError"), ("UnboundSlot", "VEError"),
   ("TypeMismatch", "VEError"), ("MissingObligationRole", "VEError"), ("MissingPermissionRole", "VEError"),
   ("AmbiguousDerivation", "VEError"), ("CoordinatedActs", "VEError"), ("QueryMismatch", "VEError")]

def limitText : String := "VE stopped reading this command at its work limit."

end VE.Commands.Texts
