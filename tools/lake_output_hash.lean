/-
Print, one line per file argument, the file and the hash Lake records for it as
a build output (`Lake.computeBinFileHash`: `hash` of the file's bytes). Run with
`lean --run tools/lake_output_hash.lean FILE...` by `tools/lake_outputs.py`,
which compares it with the `outputs` of the file's `.trace`: the pinned
toolchain itself is the oracle, never a reimplementation of its hash.
-/
def main (files : List String) : IO Unit := do
  for file in files do
    IO.println s!"{hash (← IO.FS.readBinFile file)} {file}"
