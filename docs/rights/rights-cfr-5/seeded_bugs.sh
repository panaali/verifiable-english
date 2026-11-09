#!/bin/bash
# usage: seeds.sh ; runs each seeded bug against its one test, restores the file
cd /home/seyran/code/ve-rights-cfr-5
F=ve/surface/rights.py
cp $F /tmp/rcfr5/rights.orig.py
run() { # name, python-replace old, new, test
  python3 - "$2" "$3" <<'PY'
import sys, pathlib
p = pathlib.Path("ve/surface/rights.py"); s = p.read_text()
assert s.count(sys.argv[1]) == 1, sys.argv[1]
p.write_text(s.replace(sys.argv[1], sys.argv[2]))
PY
  echo "== $1 ($4)"; git diff --stat $F | tail -1
  timeout 500 uv run pytest -q tests/test_rights.py -k "$4" -p no:cacheprovider 2>&1 | grep -E "passed|failed|^E  " | head -4
  cp /tmp/rcfr5/rights.orig.py $F
}
run S1-switch-dropped-on-parse '    raw["name"] = name' '    raw["name"] = name; raw.pop("alterable", None)' roundtrip_with_switch
run S2-non-rendered-header-accepted '    return "Rule 1" + render_header_options((), parties) + ". " == block.string[:block.start(3)]' '    return True' never_writes
run S3-precedence-option-accepted 'render_header_options((), parties) + ". "' 'render_header_options(_refs, parties) + ". "' never_writes
run S6-unparsed-header-passed-on '        return False' '        return True' never_writes
run S4-header-dropped-on-render '    return f"{kind.title()} of right {right}" + source[len("Rule 1"):]' '    return f"{kind.title()} of right {right}. " + block[3]' roundtrip_with_switch
run S5-generated-switch-dropped '    raw["name"] = name' '    raw["name"] = name; raw.pop("alterable", None) if raw.get("mode") == "default" else None' one_by_one
cmp $F /tmp/rcfr5/rights.orig.py && echo RESTORED
