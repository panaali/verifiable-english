# F15's class: claims.py reads every form of a count (a number or range, up to three words, what it counts; "N
# each"; "all N"; "about N"; N lines) and finds each wrong one in F15c.md UNBOUND, each as its own sentence; the
# ap-2 of "ap-2 replays" is a name, not a count.
r=$(mktemp -d)
uv run python docs/speed/trustmut/claims.py --report docs/speed/trustmut/hunt/F15c.md > "$r/out.txt"
test $? = 1 || exit 1
grep "F15c.md" "$r/out.txt" > "$r/got.txt"
cat > "$r/want.txt" <<'WANT'
hunt/F15c.md:2 UNBOUND ["21–35 of each replay's mutants"]: 21–35 of each replay's mutants are INVALID.
hunt/F15c.md:4 UNBOUND ['211 each']: The kills are the mutants of the `#guard`, `decide` and `rfl` rows (211 each).
hunt/F15c.md:6 UNBOUND ['about 1']: The F9 line axis of the test is about 161.
hunt/F15c.md:8 UNBOUND ['all 7']: At the default it flags all 7, so steps two and three follow.
hunt/F15c.md:10 UNBOUND ['20 lines']: Removing those operators saves under 20 lines.
WANT
diff "$r/want.txt" "$r/got.txt" && echo "F15c: 5 count forms UNBOUND, the name ap-2 not a count"
