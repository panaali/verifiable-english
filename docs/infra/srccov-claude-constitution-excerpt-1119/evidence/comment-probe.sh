#!/bin/sh
# Probe: can usecases/claude-constitution-excerpt/claims.ve hold a comment line (METHOD section 0: the
# document's only allowed record file is "comments in claims.ve")? Each candidate comment form is put on
# line 1 of a copy of claims.ve under $1 (a scratch directory) and rendered with the command rendered.md
# records; the unchanged copy is the control. Run from the repository root.
set -u
D=${1:?scratch dir}
mkdir -p "$D"
C=usecases/claude-constitution-excerpt/claims.ve
for form in '# S0001 left out' '-- S0001 left out' '// S0001 left out' '; S0001 left out' '% S0001 left out' \
            '/- S0001 left out -/' '(* S0001 left out *)' '## S0001 | left out'; do
  { printf '%s\n' "$form"; cat "$C"; } > "$D/probe.ve"
  out=$(uv run python -m ve render --env usecases/claude-constitution-excerpt/environment.json --view ve_fluent "$D/probe.ve" 2>&1)
  echo "form [$form] rc=$? => $(printf '%s\n' "$out" | grep -m1 -E '"message"|"line"' | sed 's/^ *//') $(printf '%s\n' "$out" | grep -m1 -E '"line"|"column"' | sed 's/^ *//')"
done
cp "$C" "$D/probe.ve"
out=$(uv run python -m ve render --env usecases/claude-constitution-excerpt/environment.json --view ve_fluent "$D/probe.ve" 2>&1)
echo "control (claims.ve unchanged) rc=$? => $(printf '%s\n' "$out" | head -1)"
