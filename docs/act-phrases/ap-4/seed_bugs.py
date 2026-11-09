#!/usr/bin/env python3
"""ap-4's seeded bugs: plant each bug, run the check that should catch it, record the failing `#guard`, theorem or
test (KILLED), restore the file, and write mutants.json beside this script. Lean plants build their targets
(`lake build`); Python plants run their pytest ids. At least one plant per new trusted definition of
`lean/VE/Acts/Run.lean` (`tools/trust_map.py`'s [V] declarations: `actJson`, `readingJson`, `listReadings`, `listed`,
`runActReadings`, `rowsOf`), one per claimed behaviour, the encoder theorem, and the plan's two (Lean: the pre-modifier's `all`
reading dropped, so rs_u055 (S4) is refused; Python: the token-index range check dropped, so AR2 is accepted).
Run from the repository root: `python3 docs/act-phrases/ap-4/seed_bugs.py [ids...]`."""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LEAN = ROOT / "lean"
RUN, G, REG = "lean/VE/Acts/Run.lean", "lean/VE/Acts/Grammar.lean", "lean/VE/Service/Registry.lean"
PY = "ve/acts.py"
EX = ["VE.Acts.RunExamples"]
UPSTREAM = ["lean/VE/Acts/RuleExamples.lean", "lean/VE/Acts/MeaningExamples.lean"]
FUZZ = "tests/test_acts_readings_answer.py"
LEANT = "tests/test_acts_readings_lean.py"
# (file, id, definition, behaviour, before, after, check: lake targets or pytest ids, isolate upstream guards)
BUGS = [
    (G, "e1x-all-dropped", "VE.Acts.globalRules", "the plan's Lean bug: the pre-modifier's `all` reading is dropped, "
     "so rs_u055 (S4) must be refused", "[⟨.E1X, [adv], .edge .first⟩, ⟨.E1X, [adv], .edge .all⟩]",
     "[⟨.E1X, [adv], .edge .first⟩]", ["VE.Acts.ReadingsExamples"], True),
    (RUN, "actJson-no-from", "VE.Acts.Run.actJson", "an act names no tokens",
     "(\"from\", toJson (fromOf ps fn base (Simple.toks (some plain) x')))", '("from", toJson ([] : List Nat))', EX, False),
    (RUN, "actJson-text-is-act", "VE.Acts.Run.actJson", "an act's text is not worded under the modal",
     '("text", .str (sentence fx op f x))', '("text", .str (Simple.text fx (some plain) x))', EX, False),
    (RUN, "actJson-act-not-plain", "VE.Acts.Run.actJson", "a plain act is rendered without its *to*",
     'Json.mkObj [("act", .str (Simple.text fx (some plain) x))', 'Json.mkObj [("act", .str (Simple.text fx (some false) x))',
     EX, False),
    (RUN, "readingJson-first-act", "VE.Acts.Run.readingJson", "a reading lists its first act only",
     "Json.arr (R.zipIdx.map fun", "Json.arr ((R.take 1).zipIdx.map fun", EX, False),
    (RUN, "readingJson-untagged", "VE.Acts.Run.readingJson", "review F4: an act's `from` is read off the untagged "
     "meaning, so its content tokens have no place", "actJson fx op f plain ps fn base x (R'.getD i x)",
     "actJson fx op f plain ps fn base x x", EX, False),
    (RUN, "listReadings-no-byte-limit", "VE.Acts.Run.listReadings", "a phrase over 400 bytes is read",
     "if Lexical.maxActBytes < phrase.utf8ByteSize then", "if Lexical.maxActBytes + 1 < phrase.utf8ByteSize then",
     EX, False),
    (RUN, "listReadings-no-tokens", "VE.Acts.Run.listReadings", "a listing has no token spans",
     '("tokens", Json.arr (sp.map fun (a, b) => Json.arr #[toJson a, toJson b]).toArray)', '("tokens", Json.arr #[])',
     EX, False),
    (RUN, "listReadings-none-listed", "VE.Acts.Run.listReadings", "a phrase with no reading is listed with none",
     '  | some (_, []) => throw "InvalidInput: this act phrase has no reading under the declared frames and its modal words"\n',
     "", EX, False),
    (RUN, "rowsOf-paraphrase-what", "VE.Acts.Run.rowsOf", "D-32 names another phrase",
     'paraphrases fx op f "this act phrase" (Ws.map Prod.fst)', 'paraphrases fx op f "the source phrase" (Ws.map Prod.fst)',
     EX, False),
    (RUN, "rowsOf-one-tag", "VE.Acts.Run.rowsOf", "review F4: every reading is read against the first meaning's "
     "derivation", "let tags := ms.map fun (_, t) => tagged V (tagBase ps) t",
     "let tags := (ms.take 1).map fun (_, t) => tagged V (tagBase ps) t", EX, False),
    (RUN, "witnessed-no-limit", "VE.Acts.Run.witnessed", "review F2: `witnessed` lists more than 64 readings, so it "
     "is not `phraseReadings` (`witnessed_readings` must break)",
     "    if maxReadings < Rs.length then none else some (ms, Rs)", "    some (ms, Rs)", EX, False),
    (RUN, "firstsBy-keeps-equal", "VE.Acts.Run.firstsBy", "review F2: first occurrences keep a later equal key "
     "(`firstsBy_map` must break)", "x :: (firstsBy f xs).filter (fun y => f y ≠ f x)", "x :: firstsBy f xs", EX, False),
    (RUN, "tagTree-tags-function-words", "VE.Acts.Run.tagTree", "review F4: the leaves of *to*, *be*, join words and "
     "markers are tagged too, so no written token of an act finds its place",
     "    let keep' := keep || (match rs[i]? with", "    let keep' := false && (match rs[i]? with", EX, False),
    (RUN, "placeOf-no-word", "VE.Acts.Run.placeOf", "review F4: a tagged word has no place",
     '| .word w => if w.startsWith "#" then (w.drop 1).toNat? else none', "| .word _ => none", EX, False),
    (RUN, "tagged-content-as-function", "VE.Acts.Run.tagged", "review F4: the phrase's content tokens are taken as "
     "function tokens, so a written *to* or *and* may read a content word", "(placeOf base x).isNone).map (·.2))",
     "true).map (·.2))", EX, False),
    (RUN, "toks-or-for-and", "VE.Acts.Run.Act.toks", "review F4: a whole *and* join's tokens write *or*, unlike its "
     "text", '| .all _ _ ps => .slot 0 :: joinToks (.word "and")', '| .all _ _ ps => .slot 0 :: joinToks (.word "or")',
     EX, False),
    (RUN, "toks-no-to", "VE.Acts.Run.Simple.toks", "review F4: an atom's tokens drop its *to*",
     "  | .atom a => (a.withTo inf).normal\n  | .whole A => Act.toks inf A",
     "  | .atom a => (a.withTo (some false)).normal\n  | .whole A => Act.toks inf A", EX, False),
    (RUN, "listReadings-bogus-verdict", "VE.Acts.Run.listReadings", "the listing's verdict is outside the shape "
     "(`runActReadings_fits` must break)", 'pure (VE.Route.Wire.ok id [("verdict", .str "LISTED"),',
     'pure (VE.Route.Wire.ok id [("verdict", .str "BOGUS"),', ["ResponseShape.Encoders.ActReadings"], False),
    (RUN, "listed-sign-ignored", "VE.Acts.Run.listed", "the rule's sign is not read: *must not* is read as *may*",
     "let some op := opOf ⟨\"\", [], false, role, none, none⟩ sign", "let some op := opOf ⟨\"\", [], false, role, none, none⟩ true",
     EX, False),
    (RUN, "listed-no-frames", "VE.Acts.Run.listed", "the request's adverbs are not read",
     '("adverbs", j.getObjValD "adverbs")', '("adverbs", Json.arr #[])', EX, False),
    (RUN, "runActReadings-refusal-listed", "VE.Acts.Run.runActReadings", "a refusal is answered as an empty listing",
     "    | .error d => refusedRow id d)", "    | .error _ => VE.Route.Wire.ok id [(\"verdict\", .str \"REFUSED\"), "
     "(\"tokens\", Json.arr #[]), (\"readings\", Json.arr #[]), (\"diagnostic\", .str \"\")])", EX, False),
    (RUN, "verdictOf-no-limit", "VE.Acts.Run.verdictOf", "a limit is answered REFUSED",
     'if d.startsWith "ResourceLimit:" then "LIMIT" else "REFUSED"', '"REFUSED"', EX, False),
    (RUN, "spans-no-fold", "VE.Acts.Run.spans", "U+2019 is not read as an apostrophe",
     "else if (if c.toNat == 0x2019 then '\\'' else c) == x then", "else if c == x then", EX, False),
    (RUN, "spans-one-space", "VE.Acts.Run.spans", "a run of whitespace is read as one character",
     "if ws c then let (r, q) := skip cs (p + c.utf8Size); read t r q else none",
     "if ws c then read t cs (p + c.utf8Size) else none", EX, False),
    (RUN, "fromOf-any-anchor", "VE.Acts.Run.fromOf", "review F4: a written token is placed before the next content "
     "token even when the act read it already, so P11's whole join loses its *or*",
     "    | some (p, false) => ((x, some p, acc.2) :: acc.1, acc.2)", "    | some (p, false) => ((x, some p, p) :: acc.1, p)",
     EX, False),
    (RUN, "fromOf-reuse", "VE.Acts.Run.fromOf", "an act lists a token it reads twice",
     "    | some i => if acc.contains i then acc else acc ++ [i]", "    | some i => acc ++ [i]", EX, False),
    (RUN, "fromOf-any-token", "VE.Acts.Run.fromOf", "review F4: a written token may read any equal token, a content "
     "word of another item included", "(fn.filter fun i => i < next", "((List.range ps.length).filter fun i => i < next",
     EX, False),
    (RUN, "sameTok-case", "VE.Acts.Run.sameTok", "words are compared case-sensitively",
     "| .word v, .word w => v.toLower == w.toLower", "| .word v, .word w => v == w", EX, False),
    (REG, "registry-name", "VE.Service.Mode.name", "the mode is registered under another name",
     '| .actReadings => "act-readings"', '| .actReadings => "act-reading"', ["VE.Service.RegistryExamples"], False),
    (PY, "py-range-check-dropped", "ve.acts.answer_problem", "the plan's Python bug: the token-index range check is "
     "dropped, so AR2's index past the last token is accepted",
     '            if any(not 0 <= i < len(tokens) for i in act["from"]):\n                return "a token index is out of range"\n',
     "", [f"{FUZZ}::test_ar2_a_token_index_past_the_last_token_is_no_answer",
          f"{FUZZ}::test_every_mutant_is_no_answer_or_lean_content_binding_cannot_see"], False),
    (PY, "py-span-bound-dropped", "ve.acts.answer_problem", "a span past the phrase is accepted",
     ' <= len(case["phrase"].encode("utf-8"))', "", [f"{FUZZ}::test_ar3_a_span_past_the_phrase_is_no_answer"], False),
    (PY, "py-equal-readings", "ve.acts.answer_problem", "two equal readings are accepted",
     'if len({_value(r["acts"]) for r in readings}) != len(readings):', "if False:",
     [f"{FUZZ}::test_ar4_two_equal_readings_are_no_answer"], False),
    (PY, "py-index-twice", "ve.acts.answer_problem", "an index twice in one act is accepted",
     'if len(set(act["from"])) != len(act["from"]):', "if False:",
     [f"{FUZZ}::test_an_index_twice_in_one_act_and_spans_out_of_order_are_no_answer"], False),
    (PY, "py-act-twice-refused", "ve.acts.answer_problem", "review F1: an act listed twice in a reading is refused, "
     "so E16's genuine answer is CheckerUnavailable",
     '        for act in reading["acts"]:\n            if not act["act"]',
     '        if len({_value(act) for act in reading["acts"]}) != len(reading["acts"]):\n'
     '            return "an act occurs twice in one reading"\n'
     '        for act in reading["acts"]:\n            if not act["act"]',
     [f"{FUZZ}::test_e16_one_act_written_twice_is_bound"], False),
    (PY, "py-coerced", "ve.acts._as_sent", "review F3: a string member is split into its letters",
     "return list(value) if type(value) is tuple else value",
     "return list(value) if type(value) in (tuple, str) else value",
     [f"{LEANT}::test_the_request_coerces_no_member",
      f"{LEANT}::test_a_malformed_acts_file_is_invalid_input_never_coerced"], False),
    (PY, "py-block-any-json", "ve.acts.read_block", "review F3: a file that is not a JSON object is sent on",
     "    if type(block) is not dict:\n", "    if False:\n",
     [f"{LEANT}::test_a_malformed_acts_file_is_invalid_input_never_coerced"], False),
    (PY, "py-cli-oserror", "ve.acts.main", "review F3: a missing --acts file is a traceback",
     "    except (OSError, UnicodeError) as exc:", "    except UnicodeError as exc:",
     [f"{LEANT}::test_an_unreadable_invalid_or_oversized_acts_file_is_invalid_input_or_a_limit"], False),
    (PY, "py-no-schema", "ve.acts.read_answer", "the row's schema is not checked",
     "        check_row(MODE, row, case, 0)\n", "        pass\n",
     [f"{FUZZ}::test_every_mutant_is_no_answer_or_lean_content_binding_cannot_see"], False),
    (PY, "py-verdict-binding", "ve.acts.answer_problem", "a refusal with readings is accepted",
     'if (verdict == "LISTED") != bool(readings) or (verdict != "LISTED") and tokens:', "if False:",
     [f"{FUZZ}::test_a_listing_needs_readings_and_a_refusal_has_no_tokens"], False),
]


def lake(targets: list[str]) -> tuple[int, list[str]]:
    p = subprocess.run(["lake", "build", *targets], cwd=LEAN, capture_output=True, text=True)
    lines = re.findall(r"^error: ((?:VE|ResponseShape)/[^:]+\.lean:\d+):", p.stdout + p.stderr, re.M)
    return p.returncode, sorted(set("lean/" + x for x in lines), key=lambda s: (s.split(":")[0], int(s.split(":")[1])))


def pytest(ids: list[str]) -> tuple[int, list[str]]:
    import os
    sys.path.insert(0, str(ROOT / "tools"))
    import nested_pytest
    p = subprocess.run(nested_pytest.command(["-q", "-p", "no:cacheprovider", *ids],
                                             python=("uv", "run", "python")),
                       cwd=ROOT, env=nested_pytest.environment(os.environ), capture_output=True, text=True)
    return p.returncode, sorted(set(re.findall(r"^FAILED (\S+)", p.stdout, re.M)))


def main() -> None:
    only = set(sys.argv[1:])
    out = ROOT / "docs/act-phrases/ap-4/mutants.json"
    rows = json.loads(out.read_text())["mutants"] if out.exists() and only else []
    rows = [r for r in rows if r["id"] not in only]
    for f, mid, defn, beh, before, after, check, isolate in BUGS:
        if only and mid not in only:
            continue
        path = ROOT / f
        text = path.read_text()
        assert text.count(before) == 1, (mid, text.count(before))
        saved = {u: (ROOT / u).read_text() for u in UPSTREAM} if isolate else {}
        try:
            path.write_text(text.replace(before, after))
            for u, t in saved.items():
                (ROOT / u).write_text(t.replace("#guard", "#eval"))
            rc, failing = pytest(check) if f.endswith(".py") else lake(check)
        finally:
            path.write_text(text)
            for u, t in saved.items():
                (ROOT / u).write_text(t)
        rows.append({"id": mid, "language": "Python" if f.endswith(".py") else "Lean", "file": f, "definition": defn,
                     "behaviour": beh, "status": "KILLED" if rc != 0 and failing else "SURVIVED",
                     "test": ", ".join(failing)})
        print(mid, rows[-1]["status"], rows[-1]["test"], flush=True)
    order = [b[1] for b in BUGS]
    rows.sort(key=lambda r: order.index(r["id"]) if r["id"] in order else len(order))
    rc, _ = lake(EX + ["ResponseShape.Encoders.ActReadings", "VE.Service.RegistryExamples", "VE.Acts.ReadingsExamples"])
    out.write_text(json.dumps({"item": "ap-4", "command": "python3 docs/act-phrases/ap-4/seed_bugs.py",
                               "restored_build_returncode": rc, "mutants": rows}, indent=1, ensure_ascii=False) + "\n")
    sys.exit(0 if rc == 0 and all(r["status"] == "KILLED" for r in rows) else 1)


if __name__ == "__main__":
    main()
