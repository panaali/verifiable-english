"""ap-3db seeded bugs: plant each one in a copy of lean/, show a named fixture fail, leave the worktree as it is.

    uv run python docs/act-phrases/ap-3db/seed_bugs.py [--workers N]

Each worker copies `lean/` (with its build) under a temporary directory. A row plants its edits, stubs the proofs named
beside them with `sorry` (so a `#guard` must fail, not only a proof), runs
`lake build VE.Acts.DecodeExamples VE.Service.ActsExamples`, and restores the files. A row is KILLED when a `#guard`
fails; a row marked `proof` is about a branch no input reaches, and is KILLED when its theorem fails. Writes
mutants.json beside this file; exit 1 unless every row is KILLED.
"""
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "mutants.json"
W, AW, DE = "VE/Norms/Wire.lean", "VE/Acts/Wire.lean", "VE/Acts/Decode.lean"
NW, NR, DR = "VE/NormDefaults/Wire.lean", "VE/Norms/Run.lean", "VE/NormDefaults/Run.lean"
RW = "VE/Readings/Wire.lean"
TARGETS = ["VE.Acts.DecodeExamples", "VE.Service.ActsExamples"]
SP = "VE.Acts.Lexical.checkWith (fun act _ => pure act) fx name k raw"
SRC = [(DE, "lookup_split"), (DE, "splitEnv_route"), (DE, "sourceOf_U"), (DE, "sourceOf_lexical")]

# (id, definition, claim, edits, proofs to stub, kind)
BUGS = [
    ("shape-is-lexical", "canonicalShape", "the hook admits a joined act under acts@0",
     [(W, f"then {SP}\n", "then VE.Acts.Lexical.check fx name k raw\n")], [], "guard"),
    ("shape-without-profile", "canonicalShape", "without acts@0 the hook is canonicalAct, byte for byte",
     [(W, f"if profiles.contains \"acts@0\" then {SP}", f"if true then {SP}")], [], "guard"),
    ("shape-declaration-no-acts", "decodeRegulatedShape", "a plain declaration keeps its act and form",
     [(W, "decodeRegulatedWith (profiles.contains \"acts@0\") (canonicalShape profiles fx)",
       "decodeRegulatedWith false (canonicalShape profiles fx)")], [], "guard"),
    ("helper-dropped", "canonicalActIn", "environment, typing, model gate, Background and English keep D-4 (DRI item 2)",
     [(W, "if profiles.contains \"acts@0\" then VE.Acts.Lexical.check fx name k raw else canonicalAct name k raw",
       f"if profiles.contains \"acts@0\" then {SP} else canonicalAct name k raw")], [], "guard"),
    ("trees-dropped", "actsOf", "each joined act's tree reaches elaboration",
     [(W, "pure (A.map (r.name, ·))", "pure ((A.map (r.name, ·)).filter (fun _ => false))")], [], "guard"),
    ("arity-constant", "actsOf", "each act is checked at its predicate's arity",
     [(W, "VE.Acts.Wire.checkAct fx V r.name r.sorts.length (.str a)", "VE.Acts.Wire.checkAct fx V r.name 1 (.str a)")],
     [], "guard"),
    ("joined-not-asked", "joinedActs", "a lexical decoder reads no tree",
     [(W, "if joined && ps.contains \"acts@0\" then actsOf", "if ps.contains \"acts@0\" then actsOf")], [], "guard"),
    ("joined-no-profile", "joinedActs", "without acts@0 no act is read",
     [(W, "if joined && ps.contains \"acts@0\" then actsOf", "if joined then actsOf")], [], "guard"),
    ("vocab-empty", "actsVocab", "the block's frames reach the act check",
     [(W, "| false, .ok block => VE.Acts.Wire.decodeVocab block", "| false, .ok _ => pure ⟨[], []⟩")], [], "guard"),
    ("frames-refused", "actsFixed", "the block admits frames and adverbs under acts@0 (DRI item 4)",
     [(W, "exactFields block ([\"fixed\"] ++ [\"frames\", \"adverbs\"].filter fun k => (block.getObjVal? k).isOk)",
       "exactFields block [\"fixed\"]")], [], "guard"),
    ("readings-canonical-joined", "canonicalEnvironmentJson", "the readings route's identity keeps Lexical.check",
     [(W, "if ps.contains \"readings@1\" then canonicalActIn ps fx else canonicalShape ps fx",
       "canonicalShape ps fx")], [], "guard"),
    ("source-lexical", "decodeSource", "decodeSource admits a joined act by default",
     [(W, "(displayConstants : Bool := true) (joined : Bool := true) : Except String Source",
       "(displayConstants : Bool := true) (joined : Bool := false) : Except String Source")],
     [(NW, "decode_conservative"), (NW, "decodeSourceU_plain")], "guard"),
    ("environment-joined", "decodeNormsEnvironment", "the decoder's default stays lexical (DRI item 2)",
     [(W, "(displayConstants : Bool := true) (acts : Bool := false) (joined : Bool := false) :",
       "(displayConstants : Bool := true) (acts : Bool := false) (joined : Bool := true) :")], [], "guard"),
    ("frame-fields-swapped", "decodeFrame", "markers and split are read from their keys",
     [(AW, "← strings (j.getObjValD \"markers\"), ← strings (j.getObjValD \"split\"),",
       "← strings (j.getObjValD \"split\"), ← strings (j.getObjValD \"markers\"),")], [], "guard"),
    ("frame-modifiers", "decodeFrame", "modifiers are read from their key",
     [(AW, "← strings (j.getObjValD \"modifiers\")⟩", "(← strings (j.getObjValD \"modifiers\")).take 0⟩")], [], "guard"),
    ("frame-head", "decodeFrame", "a head is its words",
     [(AW, "⟨wordsOf (← stringField j \"head\"),", "⟨[← stringField j \"head\"],")], [], "guard"),
    ("vocab-unchecked", "decodeVocab", "D-31 raised by checkVocab",
     [(AW, "  checkVocab V\n  pure V", "  pure V")], [], "guard"),
    ("adverbs-dropped", "decodeVocab", "adverbs are read",
     [(AW, "let V : Vocab := ⟨frames, adverbs⟩", "let V : Vocab := ⟨frames, adverbs.take 0⟩")], [], "guard"),
    ("frames-required", "decodeVocab", "an absent field is empty",
     [(AW, "    | .ok fs => (← fs.getArr?).toList.mapM decodeFrame\n    | .error _ => pure []",
       "    | .ok fs => (← fs.getArr?).toList.mapM decodeFrame\n    | .error _ => throw \"frames\"")], [], "guard"),
    ("fixed-empty", "fixedOf", "fixedOf reads the block's list",
     [(AW, "getObjValD \"acts\").getObjValD \"fixed\"))", "getObjValD \"acts\").getObjValD \"frames\"))")], [], "guard"),
    ("source-kept", "splitPredicates", "a split source is no longer declared",
     [(DE, "P.filter fun x => !M.preds.any (·.2.1 == x.1) && !M.preds.any (·.1 == x.1)",
       "P.filter fun x => !M.preds.any (·.1 == x.1)")], SRC, "guard"),
    ("name-kept", "splitPredicates", "a part takes over a colliding name",
     [(DE, "P.filter fun x => !M.preds.any (·.2.1 == x.1) && !M.preds.any (·.1 == x.1)",
       "P.filter fun x => !M.preds.any (·.2.1 == x.1)")], SRC, "guard"),
    ("part-sorts", "splitPredicates", "each part keeps its source's sorts",
     [(DE, "(x.1, (VE.Bridge.lookup P x.2.1).getD [])", "(x.1, [])")], SRC, "guard"),
    ("json-own-name", "splitJson", "a part's declaration is its source's",
     [(DE, "acc.setObjVal! x.1 (predicates.getObjValD x.2.1)", "acc.setObjVal! x.1 (predicates.getObjValD x.1)")],
     SRC, "guard"),
    ("regulated-source", "sourceOf", "the routes read the parts' declarations",
     [(DE, "{ src.ne with rv := rv', regulated := e.U'.D.T.regulated, json := splitJson src.ne.json e.M }",
       "{ src.ne with rv := rv', json := splitJson src.ne.json e.M }")], SRC, "guard"),
    ("json-source", "sourceOf", "a plain part reads its source's form",
     [(DE, "{ src.ne with rv := rv', regulated := e.U'.D.T.regulated, json := splitJson src.ne.json e.M }",
       "{ src.ne with rv := rv', regulated := e.U'.D.T.regulated }")], SRC, "guard"),
    ("source-vocabulary", "sourceOf", "the source vocabulary declares the parts",
     [(DE, "{ rv.sourceVocabulary with predicates := splitPredicates rv.sourceVocabulary.predicates e.M }",
       "{ rv.sourceVocabulary with predicates := rv.sourceVocabulary.predicates }")], SRC, "guard"),
    ("flags-refused", "decodeElaboratedFlagged", "the norms route keeps its data@0 flags",
     [(DE, "VE.Norms.Wire.decodeSource environment norms (flags := true) >>= (elaborateSource",
       "VE.Norms.Wire.decodeSource environment norms >>= (elaborateSource")], [], "guard"),
    ("elaborated-source", "elaboratedU", "norm-defaults reads e.U'",
     [(DE, "  decodeElaboratedU environment norms >>= sourceOf\n",
       "  VE.NormDefaults.Wire.decodeSourceU environment norms\n")], [], "guard"),
    ("flagged-source", "flaggedSource", "the norms route reads e.U'",
     [(DE, "  (decodeElaboratedFlagged environment norms >>= sourceOf).map (·.src)\n",
       "  ((decodeElaboratedFlagged environment norms).map (·.s)).map (·.src)\n")],
     [(DE, "flaggedSource_elaborated")], "guard"),
    ("trees-not-read", "elaborateSource", "elaboration reads the decoder's trees",
     [(DE, "⟨s.U, V, fx, s.src.ne.joined,", "⟨s.U, V, fx, [],")], [], "guard"),
    ("norms-entry-source", "Run.decoderOf", "the entry point put back on the source (DRI item 1's seeded bug)",
     [(NR, "if underActs environment then VE.Acts.Decode.flaggedSource else Wire.decodeFlagged",
       "if underActs environment then Wire.decodeFlagged else Wire.decodeFlagged")], [], "guard"),
    ("under-acts-false", "Run.underActs", "acts@0 is read from the case's environment",
     [(NR, "!(Wire.actsProfiles true environment).isEmpty", "(Wire.actsProfiles true environment).isEmpty")], [], "guard"),
    ("route-unrouted", "Run.runCaseRouted", "runCaseRouted reads the case's decoder",
     [(NR, "runCaseIn (decoderOf (j.getObjValD \"environment\")) j", "runCaseIn Wire.decodeFlagged j")], [], "guard"),
    ("defaults-entry-source", "NormDefaults.Run.decoderOf", "norm-defaults put back on decodeSourceU (DRI item 1)",
     [(DR, "if VE.Norms.Run.underActs environment then VE.Acts.Decode.elaboratedU else Wire.decodeSourceU",
       "if VE.Norms.Run.underActs environment then Wire.decodeSourceU else Wire.decodeSourceU")], [], "guard"),
    ("defaults-unrouted", "NormDefaults.Run.runCaseRouted", "runCaseRouted reads the case's decoder",
     [(DR, "runCaseIn (decoderOf (j.getObjValD \"environment\")) j", "runCaseIn Wire.decodeSourceU j")], [], "guard"),
    ("lexical-is-joined", "decodeSourceLexical", "the lexical decoder keeps D-4 (DRI item 2)",
     [(NW, "decodeSourceUWith false", "decodeSourceUWith true")], [], "guard"),
    ("profiled-joined", "decodeSourceUWith", "the profiled branch passes joined on",
     [(NW, "decodeSource env' norms true true joined", "decodeSource env' norms true true")], [], "guard"),
    ("plain-joined", "decodeSourceUWith", "the plain branch passes joined on",
     [(NW, "decodeSource environment norms (joined := joined)", "decodeSource environment norms")], [], "guard"),
    ("readings-frame-joined", "Readings.decodeFrame", "the readings route's frame reads Lexical.check (D-33's text)",
     [(RW, "VE.Norms.Wire.decodeNormsEnvironment frameJson (displayConstants := false) (acts := true)",
       "VE.Norms.Wire.decodeNormsEnvironment frameJson (displayConstants := false) (acts := true) (joined := true)")],
     [], "guard"),
    ("lexical-act-true", "Readings.lexicalAct", "lexicalAct tells a joined act from a single one",
     [(RW, "  | some a => (VE.Acts.Lexical.check fx r.name r.sorts.length (.str a)).toOption == some a\n",
       "  | some _ => true\n")], [(RW, "readings_lexical_only")], "guard"),
    ("lexical-act-first", "Readings.lexicalAct", "lexicalAct compares the act with its canonical form",
     [(RW, "(VE.Acts.Lexical.check fx r.name r.sorts.length (.str a)).toOption == some a",
       "(VE.Acts.Lexical.check fx r.name r.sorts.length (.str a)).toOption.isSome")], [(RW, "readings_lexical_only")],
     "guard"),
    ("readings-guard-dropped", "Readings.decodeEnvironment", "every act of the frame is lexical (D-33, by theorem)",
     [(RW, "    | true, some r =>\n      throw s!\"UnsupportedProfile: acts@0 on the readings route admits single acts "
       "only; the act of {r.name} joins acts\"\n    | _, _ => pure re", "    | _, _ => pure re")], [], "proof"),
]


def stub(text, name):
    """The proof of theorem `name`, up to the next blank line, replaced by `sorry`."""
    i = text.index(f"theorem {name} ")
    j = text.index("\n\n", i)
    m = list(re.finditer(r":=( by)?\s*\n|:= by ", text[i:j]))
    return text[:i + m[0].start()] + ":= by sorry" + text[j:]


def run(path, env):
    r = subprocess.run(["lake", "build", *TARGETS], cwd=path, env=env, capture_output=True, text=True)
    out = r.stdout + r.stderr
    return (r.returncode, sorted(set(re.findall(r"error: ((?:VE|ResponseShape)/\S+?\.lean:\d+):\d+: Expression\n", out))),
            sorted(set(re.findall(r"error: ((?:VE|ResponseShape)/\S+?\.lean:\d+):", out))))


def worker(wid, base, jobs, rows, lock):
    lean = Path(base) / f"w{wid}" / "lean"
    env = {**os.environ, "PATH": os.path.expanduser("~/.elan/bin") + os.pathsep + os.environ["PATH"],
           "LEAN_NUM_THREADS": "6"}
    shutil.copytree(ROOT / "lean", lean, symlinks=True)
    while True:
        try:
            bid, defn, claim, edits, stubs, kind = jobs.get_nowait()
        except queue.Empty:
            return
        files = {p for p, *_ in edits} | {p for p, _ in stubs}
        orig = {p: (lean / p).read_text() for p in files}
        text = dict(orig)
        for path, old, new in edits:
            assert text[path].count(old) == 1, (bid, old)
            text[path] = text[path].replace(old, new)
        for path, name in stubs:
            text[path] = stub(text[path], name)
        for p, t in text.items():
            (lean / p).write_text(t)
        code, guards, errs = run(lean, env)
        for p, t in orig.items():
            (lean / p).write_text(t)
        killed = bool(guards) or (kind == "proof" and code != 0)
        row = {"id": bid, "file": "lean/" + edits[0][0], "definition": defn, "claim": claim,
               "status": "KILLED" if killed else "SURVIVOR" if code == 0 else "INVALID",
               "test": guards[0] if guards else (errs[0] if errs else None), "guards": guards[:8], "errors": errs[:4]}
        with lock:
            rows.append(row)
            print(row["status"], bid, row["test"], len(guards), flush=True)


def main():
    n = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 5
    only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
    jobs = queue.Queue()
    for b in BUGS:
        if only is None or b[0] in only:
            jobs.put(b)
    rows, lock = [], threading.Lock()
    with tempfile.TemporaryDirectory(prefix="ap3db-seed-") as base:
        ts = [threading.Thread(target=worker, args=(i, base, jobs, rows, lock)) for i in range(n)]
        for t in ts:
            t.start()
        for t in ts:
            t.join()
    rows.sort(key=lambda r: [b[0] for b in BUGS].index(r["id"]))
    if only is not None and OUT.exists():
        # a rerun of some rows replaces those rows of the last full run
        kept = {r["id"]: r for r in json.loads(OUT.read_text())["mutants"]}
        kept.update({r["id"]: r for r in rows})
        rows = [kept[b[0]] for b in BUGS if b[0] in kept]
    OUT.write_text(json.dumps({"mutants": rows}, indent=1, ensure_ascii=False) + "\n")
    sys.exit(0 if all(r["status"] == "KILLED" for r in rows) else 1)


if __name__ == "__main__":
    main()
