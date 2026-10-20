# F14's class: claims.py finds the overclaims of the F13/F14 round's report (exit 1, among them the probe claim
# "Every hunt probe but N4 (boundary 1) exits 0 on the final tool", for which nothing was saved), and none in this one.
r=$(mktemp -d)
git show be422c2d3:docs/speed/trustmut/REPORT.md > "$r/REPORT.md" || exit 2
uv run python docs/speed/trustmut/claims.py --report "$r/REPORT.md" > "$r/old.txt"
old=$?
tail -1 "$r/old.txt"
test "$old" = 1 && grep -q "UNBOUND \['exits 0', 'on the final tool'\]: - Every hunt probe but N4" "$r/old.txt" || exit 1
uv run python docs/speed/trustmut/claims.py > "$r/new.txt"
new=$?
grep " UNBOUND " "$r/new.txt"
tail -1 "$r/new.txt"
exit $new
