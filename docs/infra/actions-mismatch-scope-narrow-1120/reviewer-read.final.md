OK: safe to install as staged, provided `mismatch-scope.sh` is installed before the four call sites (see the first point below).

**Install order (required).** The live `mismatch-scope.sh` is still the broad 06:42Z rule; nothing calls it right now, so it does no harm yet. If any call site is moved into place before the helper, the ADV-1 problem comes back. `merge-train.sh` reads the helper once when a train starts, so a train started in that gap would keep the broad rule for its whole run. Move `mismatch-scope.sh.new-amscope2` into place first (or in the same step), then the call sites.

**Claims:**
1. **Holds.** Every input below blocks (rc 0), in both `C.UTF-8` and `C` locales:
   - all 11 cloud-tm-verify fail(1) reasons under tm, testmap, select, armsh and item-named jobs;
   - cloud-late.py lines and every `select-*` line;
   - a file mixing allowed and blocking lines, in either order;
   - a CR inside a line or at its end, a NUL followed by more text, a `)` inside the path, trailing space, a tab after the timestamp, a BOM, non-ASCII digits or job characters, `tm--x`, a `:` or space in the job, an empty reason;
   - a broken symlink, a directory, a FIFO (no hang), an unreadable file, an empty file, a file holding only a newline.
   
   No cloud-pull.sh line can pass, even when `$out` runs over several lines: each mismatch() write starts with `<stamp> <job>: <first line of $out>`, and that first line is cloud-tm-verify's `cloud-tm-verify <job>: MISMATCH: …`, a Python traceback, or empty. None of these match the allowed text, and every line must match. The pattern parts are written into the code; `$job` and `$why` only appear on the left of `==`, so they are never read as patterns. `[^\)]#` correctly rejects any `)` inside the path.
2. **Holds.** After a call, the caller's `extendedglob` and `localoptions` are back to what they were (off stays off, on stays on). The caller's `why`, `job`, `l`, `n`, `rest` and `f` are untouched; this matters because `merge-train.sh` uses `$why` at :570/:577. If the caller has `shglob` or `emulate sh|ksh` set when it reads the helper, the read fails and the old rule applies (any file blocks), which is the safe direction.
3. **Holds.** All four call sites match the live files plus the `.new-amscope` change; `arm-postcheck.sh` is byte-identical to its `.new-amscope` copy, and the other three differ only in comments. All live files match their `.bak-20261120amscope` copies, and all five staged shell files pass `zsh -n`. cloud-overflow.sh, gha-select.sh and testmap-gha.sh still check only whether the file exists.
4. **Holds.** On `.new-amscope2`, all 19 tests pass. On `.new-amscope`, 7 fail: (v), (vi), (vii), (viii) and the three direct cases. On the live files, (i) ×2 and `helper_one_copy` fail as required; the three direct cases also fail there, because the live helper is still the broad rule.

**Bugs I planted in scratch copies:** these loosened rules all made the tests fail:
- "starts with verdict sample differs" (the task's wording);
- adding `select` to the allowed jobs;
- `*` in place of `[^\)]#`;
- checking only the first line;
- treating an empty file as "on";
- dropping `setopt extendedglob` (allowed lines then block, and test (i) catches it).

**Not blocking:**
- No test pins two cases: an unreadable or non-regular file, and the job character check (`[A-Za-z0-9._-]`). Planting "unreadable file leaves the legs on" or removing the character check still passed all 19 tests. The helper itself handles both correctly in my probes.
- The test file lost its `#!/usr/bin/env python3` line (harmless when run with `python3 -I`).
- The old method names `test_v_*` and `test_vi_*` are now `test_ix_absent_is_on` and `test_x_no_helper_falls_back_to_the_old_rule`. If any selection list names the old tests, it needs updating.
- A NUL inside the path of an otherwise exact verdict-sample line still passes. No writer produces this.

Nothing under `/home/seyran/code` was touched. All probes ran in `/tmp/amscope2-review/scratch-*` and test temp files went to `/tmp/amscope2-review/tmp`.
