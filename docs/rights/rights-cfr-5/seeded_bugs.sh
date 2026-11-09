#!/bin/bash
# rights-cfr-5 seeded bugs: plant each bug in ve/surface/rights.py, run the one test that must
# catch it, then restore the file from git. Usage: bash docs/rights/rights-cfr-5/seeded_bugs.sh
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
F=ve/surface/rights.py
git diff --quiet -- "$F" || { echo "refusing: $F has uncommitted changes"; exit 2; }
trap 'git checkout -- "$F"' EXIT
run() { # name, old text, new text, pytest -k selection
  python3 - "$2" "$3" <<'PY'
import sys, pathlib
p = pathlib.Path("ve/surface/rights.py"); s = p.read_text()
assert s.count(sys.argv[1]) == 1, sys.argv[1]
p.write_text(s.replace(sys.argv[1], sys.argv[2]))
PY
  echo "== $1 ($4)"; git diff --stat -- "$F" | tail -1
  timeout 500 uv run pytest -q tests/test_rights.py -k "$4" -p no:cacheprovider 2>&1 | grep -E "passed|failed|^E  " | head -4 || true
  git checkout -- "$F"
}
run S1-switch-dropped-on-parse '    raw["name"] = name' '    raw["name"] = name; raw.pop("alterable", None)' roundtrip_with_switch
run S2-non-rendered-header-accepted '    return "Rule 1" + render_header_options((), parties) + ". " == block.string[:block.start(3)]' '    return True' never_writes
run S3-precedence-option-accepted 'render_header_options((), parties) + ". "' 'render_header_options(_refs, parties) + ". "' never_writes
run S6-unparsed-header-passed-on '        return False' '        return True' never_writes
run S4-header-dropped-on-render '    return f"{kind.title()} of right {right}" + source[len("Rule 1"):]' '    return f"{kind.title()} of right {right}. " + block[3]' roundtrip_with_switch
run S5-generated-switch-dropped '    raw["name"] = name' '    raw["name"] = name; raw.pop("alterable", None) if raw.get("mode") == "default" else None' one_by_one
git diff --quiet -- "$F" && echo RESTORED
