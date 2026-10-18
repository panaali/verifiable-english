import VE.Limits
import VE.Bridge
import VE.Order.Wire
import VE.EnglishGrammar.Lexer

/-! The limits that frozen or hashed modules keep as literals are `VE.Limits`' values: at the limit
and one past it for the frozen decoders' inline literals, and by value for their named copies. The
frozen decoders are hash-frozen by architecture decision D2 (`VE/Route/frozen-sources.sha256`), the
English lexer by the grammar lock (`ve/english_grammar/LOCK.json`); neither may import `VE.Limits`. -/
namespace VE.LimitTies
open VE.Limits

private def nested (depth : Nat) : String :=
  String.mk (List.replicate depth '[') ++ String.mk (List.replicate depth ']')

private def name (bytes : Nat) : String := String.mk (List.replicate bytes 'a')

#guard (VE.JsonInput.parse (nested maxJsonDepth)).toBool
#guard !(VE.JsonInput.parse (nested (maxJsonDepth + 1))).toBool
#guard VE.Bridge.identifier (name maxIdentifierBytes)
#guard !VE.Bridge.identifier (name (maxIdentifierBytes + 1))
#guard VE.Bridge.sourceIdentifierBudget (name maxIdentifierBytes)
#guard !VE.Bridge.sourceIdentifierBudget (name (maxIdentifierBytes + 1))
#guard VE.Order.Wire.maxNumeralChars == maxNumeralChars
#guard VE.EnglishGrammar.maxSourceBytes == maxSourceBytes

end VE.LimitTies
