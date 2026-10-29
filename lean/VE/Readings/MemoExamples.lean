import VE.Service.Protocol

/-! Build-time probes for every branch of the process-local readings admission memo. -/
open Lean VE.Readings.Run VE.Service

#guard ({} : AdmissionMemo).admissions == 0 && ({} : AdmissionMemo).hits == 0

#guard Id.run do
  let .ok c := Json.parse "{\"id\":\"readings-choice\",\"kind\":\"readings-choice\",\"environment\":{\"language\":\"ve.core@0.2\",\"profiles\":[\"norm-defaults@0\",\"norms@0\",\"readings@1\",\"relational-fol@0\"],\"spec_revision\":\"ve-v0.2-expand2-2026-09-25\",\"vocabulary\":{\"sorts\":{\"agent\":{\"description\":\"agent\"}},\"constants\":{},\"predicates\":{\"greet_required\":{\"arguments\":[\"agent\"],\"description\":\"obligation\",\"regulated\":{\"role\":\"obligation\",\"default\":\"deny\",\"act\":\"{0} greet\",\"permission\":\"greet_permitted\"}},\"greet_permitted\":{\"arguments\":[\"agent\"],\"description\":\"permission\",\"regulated\":{\"role\":\"permission\",\"default\":\"deny\",\"act\":\"{0} greet\"}}}}},\"document\":{\"units\":[{\"id\":\"u0\",\"kind\":\"norm\",\"content\":{\"norm\":{\"name\":\"must-greet\",\"predicate\":\"greet_required\",\"sign\":true,\"guard\":[\"top\"],\"unless\":[],\"over\":[]}}},{\"id\":\"u_a\"},{\"id\":\"u_b\"}],\"reading_sets\":[{\"id\":\"rs_a\",\"unit\":\"u_a\",\"version\":1,\"status\":\"open\",\"readings\":[{\"id\":\"every\",\"kind\":\"norm\",\"content\":{\"norm\":{\"name\":\"must-help\",\"predicate\":\"help_required\",\"sign\":true,\"guard\":[\"top\"],\"unless\":[],\"over\":[]}},\"meaning_id\":\"0515c095a2aec36349afd129d4a841cc4e89dc651178902e5d5c3b69aec36338\",\"admission\":{\"who\":\"w\",\"why\":\"y\",\"distinguishing_models\":{\"asks\":\"803302a4a75368f270db9cbaf56d7a7b39d4f0c5d28ec455645d8227de0df7d3\"}},\"companion\":{\"environment\":{\"language\":\"ve.core@0.2\",\"profiles\":[\"norm-defaults@0\",\"norms@0\",\"relational-fol@0\"],\"spec_revision\":\"ve-v0.2-expand2-2026-09-25\",\"vocabulary\":{\"sorts\":{\"agent\":{\"description\":\"agent\"},\"user\":{\"description\":\"user\"}},\"constants\":{},\"predicates\":{\"asks\":{\"arguments\":[\"user\",\"agent\"],\"description\":\"{0} asks {1}\"},\"help_required\":{\"arguments\":[\"agent\",\"user\"],\"description\":\"obligation\",\"regulated\":{\"role\":\"obligation\",\"default\":\"unspecified\",\"act\":\"{0} help {1}\",\"permission\":\"help_permitted\"}},\"help_permitted\":{\"arguments\":[\"agent\",\"user\"],\"description\":\"permission\",\"regulated\":{\"role\":\"permission\",\"default\":\"unspecified\",\"act\":\"{0} help {1}\"}}}}},\"open_terms\":[]}},{\"id\":\"asks\",\"kind\":\"norm\",\"content\":{\"norm\":{\"name\":\"must-help\",\"predicate\":\"help_required\",\"sign\":true,\"guard\":[\"binary\",\"asks\",[\"var\",0],[\"var\",1]],\"unless\":[],\"over\":[]}},\"meaning_id\":\"331dab9ccb61fdc514a752f0aad1b592c7f2535dc2b63fe2fec8f0c2582f9125\",\"admission\":{\"who\":\"w\",\"why\":\"y\",\"distinguishing_models\":{\"every\":\"803302a4a75368f270db9cbaf56d7a7b39d4f0c5d28ec455645d8227de0df7d3\"}},\"companion\":{\"environment\":{\"language\":\"ve.core@0.2\",\"profiles\":[\"norm-defaults@0\",\"norms@0\",\"relational-fol@0\"],\"spec_revision\":\"ve-v0.2-expand2-2026-09-25\",\"vocabulary\":{\"sorts\":{\"agent\":{\"description\":\"agent\"},\"user\":{\"description\":\"user\"}},\"constants\":{},\"predicates\":{\"asks\":{\"arguments\":[\"user\",\"agent\"],\"description\":\"{0} asks {1}\"},\"help_required\":{\"arguments\":[\"agent\",\"user\"],\"description\":\"obligation\",\"regulated\":{\"role\":\"obligation\",\"default\":\"unspecified\",\"act\":\"{0} help {1}\",\"permission\":\"help_permitted\"}},\"help_permitted\":{\"arguments\":[\"agent\",\"user\"],\"description\":\"permission\",\"regulated\":{\"role\":\"permission\",\"default\":\"unspecified\",\"act\":\"{0} help {1}\"}}}}},\"open_terms\":[]}}],\"situations\":{\"803302a4a75368f270db9cbaf56d7a7b39d4f0c5d28ec455645d8227de0df7d3\":{\"base\":{\"domains\":{\"agent\":[\"a\"],\"user\":[\"u\"]},\"constants\":{},\"relations\":{\"asks\":[],\"unsaid__help_permitted\":[[\"a\",\"u\"]],\"unsaid__help_required\":[]}},\"fixed\":[],\"witness\":\"every\",\"decisions\":[],\"probe\":{\"outcome\":{\"predicate\":\"help_required\",\"tuple\":[\"a\",\"u\"]}},\"value\":true}}},{\"id\":\"rs_b\",\"unit\":\"u_b\",\"version\":1,\"status\":\"open\",\"readings\":[{\"id\":\"every\",\"kind\":\"norm\",\"content\":{\"norm\":{\"name\":\"must-warn\",\"predicate\":\"warn_required\",\"sign\":true,\"guard\":[\"top\"],\"unless\":[],\"over\":[]}},\"meaning_id\":\"fc1fecf48adf38e856b6ecc5a9c5a305ab8d782ef1f34f9ec7b723023428e82a\",\"admission\":{\"who\":\"w\",\"why\":\"y\",\"distinguishing_models\":{\"calls\":\"742b25b4c5b77b38b5d1689cc2320363964a5d4cf27ffa011f24621e8f54b23d\"}},\"companion\":{\"environment\":{\"language\":\"ve.core@0.2\",\"profiles\":[\"norm-defaults@0\",\"norms@0\",\"relational-fol@0\"],\"spec_revision\":\"ve-v0.2-expand2-2026-09-25\",\"vocabulary\":{\"sorts\":{\"agent\":{\"description\":\"agent\"},\"user\":{\"description\":\"user\"}},\"constants\":{},\"predicates\":{\"calls\":{\"arguments\":[\"user\",\"agent\"],\"description\":\"{0} calls {1}\"},\"warn_required\":{\"arguments\":[\"agent\",\"user\"],\"description\":\"obligation\",\"regulated\":{\"role\":\"obligation\",\"default\":\"unspecified\",\"act\":\"{0} warn {1}\",\"permission\":\"warn_permitted\"}},\"warn_permitted\":{\"arguments\":[\"agent\",\"user\"],\"description\":\"permission\",\"regulated\":{\"role\":\"permission\",\"default\":\"unspecified\",\"act\":\"{0} warn {1}\"}}}}},\"open_terms\":[]}},{\"id\":\"calls\",\"kind\":\"norm\",\"content\":{\"norm\":{\"name\":\"must-warn\",\"predicate\":\"warn_required\",\"sign\":true,\"guard\":[\"binary\",\"calls\",[\"var\",0],[\"var\",1]],\"unless\":[],\"over\":[]}},\"meaning_id\":\"b436ca46aa94c6aaf3c4e8ffd05513823a0da839707edcb7b9206b26c2568575\",\"admission\":{\"who\":\"w\",\"why\":\"y\",\"distinguishing_models\":{\"every\":\"742b25b4c5b77b38b5d1689cc2320363964a5d4cf27ffa011f24621e8f54b23d\"}},\"companion\":{\"environment\":{\"language\":\"ve.core@0.2\",\"profiles\":[\"norm-defaults@0\",\"norms@0\",\"relational-fol@0\"],\"spec_revision\":\"ve-v0.2-expand2-2026-09-25\",\"vocabulary\":{\"sorts\":{\"agent\":{\"description\":\"agent\"},\"user\":{\"description\":\"user\"}},\"constants\":{},\"predicates\":{\"calls\":{\"arguments\":[\"user\",\"agent\"],\"description\":\"{0} calls {1}\"},\"warn_required\":{\"arguments\":[\"agent\",\"user\"],\"description\":\"obligation\",\"regulated\":{\"role\":\"obligation\",\"default\":\"unspecified\",\"act\":\"{0} warn {1}\",\"permission\":\"warn_permitted\"}},\"warn_permitted\":{\"arguments\":[\"agent\",\"user\"],\"description\":\"permission\",\"regulated\":{\"role\":\"permission\",\"default\":\"unspecified\",\"act\":\"{0} warn {1}\"}}}}},\"open_terms\":[]}}],\"situations\":{\"742b25b4c5b77b38b5d1689cc2320363964a5d4cf27ffa011f24621e8f54b23d\":{\"base\":{\"domains\":{\"agent\":[\"a\"],\"user\":[\"u\"]},\"constants\":{},\"relations\":{\"calls\":[],\"unsaid__warn_permitted\":[[\"a\",\"u\"]],\"unsaid__warn_required\":[]}},\"fixed\":[],\"witness\":\"every\",\"decisions\":[],\"probe\":{\"outcome\":{\"predicate\":\"warn_required\",\"tuple\":[\"a\",\"u\"]}},\"value\":true}}}]},\"choice\":[[\"rs_a\",0]],\"inner\":{\"kind\":\"norm-defaults-elaborate\"},\"component\":\"rs_a\"}" | return false
  let c2 := c.setObjVal! "choice" (Json.arr #[Json.arr #[.str "rs_a", toJson (1 : Nat)]])
  let bad1 := c.setObjVal! "component" (.str "absent")
  let bad2 := c.setObjVal! "component" (.str "also_absent")
  let (first, m1) := runCaseReportedMemo {} c
  if first != runCaseReported c || m1.admissions != 1 || m1.hits != 0 then return false
  let (second, m2) := runCaseReportedMemo m1 c2
  if second != runCaseReported c2 || m2.admissions != 1 || m2.hits != 1 then return false
  let (refused, _) := runCaseReportedMemo m2 bad1
  if refused != runCaseReported bad1 then return false
  let mainCase := (c.setObjVal! "component" (.str "main")).setObjVal! "choice" (Json.arr #[])
  let otherCase := c.setObjVal! "component" (.str "rs_b") |>.setObjVal! "choice"
    (Json.arr #[Json.arr #[.str "rs_b", toJson (0 : Nat)]])
  let validate := c.setObjVal! "kind" (.str "readings-validate")
  let elaborate := c.setObjVal! "kind" (.str "readings-elaborate")
  let verdicts := c.setObjVal! "kind" (.str "readings-verdicts")
  let unsupported := c.setObjVal! "kind" (.str "other-kind")
  let single := c.setObjVal! "document"
    ((c.getObjValD "document").setObjVal! "reading_sets" (Json.arr #[]))
  for item in [mainCase, otherCase, validate, elaborate, verdicts, unsupported, single] do
    if (runCaseReportedMemo {} item).1 != runCaseReported item then return false
  let make := fun (name : String) (bytes : Nat) =>
    ({kind := name, environment := .null, document := .null, bytes := bytes, ready := []} : AdmissionMemoEntry)
  if admissionMemoMaxEntries != 4 || admissionMemoMaxBytes != 2097152 then return false
  if !((make "a" 1).matches "a" .null .null) || (make "a" 1).matches "b" .null .null ||
      (make "a" 1).matches "a" (.str "other") .null || (make "a" 1).matches "a" .null (.str "other") then return false
  if (admissionMemoTrim [make "a" 1, make "b" 1, make "c" 1, make "d" 1, make "e" 1]).map (·.kind) !=
      ["a", "b", "c", "d"] then return false
  if (admissionMemoTrim [make "large" 2097152, make "extra" 1]).map (·.kind) != ["large"] then return false
  let synthetic : AdmissionMemo := { entries := [make "a" 1, make "b" 1, make "c" 1], admissions := 5 }
  let .ok (ready, reordered) := admitComponentsMemo synthetic "b" .null .null [] | return false
  if !ready.isEmpty || reordered.entries.map (·.kind) != ["b", "a", "c"] ||
      reordered.hits != 1 || reordered.admissions != 5 then return false
  let (rows, mr) := readingsResults #[.error "bad", .ok c, .ok c2] {}
  if rows.size != 3 || rows[1]! != first || rows[2]! != second ||
      (rows[0]!.getObjValD "status") != .str "error" || mr.admissions != 1 || mr.hits != 1 then return false
  let casesText := (Json.arr #[bad1, c, c2, bad2, mainCase]).compress
  let request := Json.mkObj [("id", .str "memo"), ("mode", .str "readings-route"),
    ("cases", Json.arr #[bad1, c, c2, bad2, mainCase])]
  let (some response, _, state) := handleLineMemo {} {} request.compress | return false
  let counts := response.getObjValD "counts"
  if response.getObjValD "id" != .str "memo" || response.getObjValD "status" != .str "ok" ||
      response.getObjValD "mode" != .str "readings-route" ||
      counts.getObjValD "cases" != toJson (5 : Nat) ||
      counts.getObjValD "bytes" != toJson casesText.utf8ByteSize ||
      counts.getObjValD "errors" != toJson (2 : Nat) ||
      state.admissions != 1 || state.hits != 2 then return false
  let .arr results := response.getObjValD "results" | return false
  if results.size != 5 || results[0]!.getObjValD "result" != runCaseReported bad1 ||
      results[1]!.getObjValD "result" != first ||
      results[2]!.getObjValD "result" != second ||
      results[3]!.getObjValD "result" != runCaseReported bad2 ||
      results[4]!.getObjValD "result" != runCaseReported mainCase then return false
  if (handleLineMemo {} {} " ").1.isSome || (handleLineMemo {} {} "x").1.isNone ||
      !memoLineTooLong (16777218 : Nat) ||
      memoLineTooLong (16777217 : Nat) then return false
  return true
