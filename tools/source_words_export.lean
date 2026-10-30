import VE.EnglishGrammar.SourceWords

def main : IO Unit := do
  if !VE.EnglishGrammar.sourceWordsValid VE.EnglishGrammar.sourceWords then
    throw (IO.userError "SourceWords: invalid catalogue")
  IO.println VE.EnglishGrammar.sourceWordsJson.compress
