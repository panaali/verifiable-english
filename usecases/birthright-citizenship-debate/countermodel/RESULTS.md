# Countermodel test results

All runs: `UV_CACHE_DIR=/private/tmp/ve-uv-cache-uc uv run python -m ve countermodel --env ../environment.json --premises testN-premises.ve --conclusion testN-conclusion.ve --nonempty-domains --max-domain-size 3`

`status: NotFound` = no countermodel exists within the searched domain bound = the conclusion **follows** from the premises (entailment holds, modulo the search bound — v0's countermodel search is sound for "Found" but a "NotFound" result at a bounded domain size is not a completeness proof for unrestricted first-order consequence; see `docs/spec/v0-language.md`, "Finite models and evaluation").
`status: Found` = a finite countermodel was found = the conclusion does **not** follow; the returned model is a concrete witness.

## Test 1 — the shared core, fully instantiated: VALID

Premises: Citizenship Clause rule + `@child is born_in_us.` + `@child is subject_to_jurisdiction.`
Conclusion: `@child is us_citizen.`
**Result: `NotFound` (entails).** Plain modus ponens. Both sides agree on this step; it is not where the debate lives.

## Test 2 — the crux, without the jurisdiction premise: INVALID

Premises: Citizenship Clause rule + `@child is born_in_us.` (jurisdiction premise dropped)
Conclusion: `@child is us_citizen.`
**Result: `Found`** — countermodel: `{born_in_us: [child]}`, all other predicates empty, so `subject_to_jurisdiction(child) = false` and `us_citizen(child) = false`.

This is the single most important formal result in this use case: it proves,
mechanically, that "born on U.S. soil" alone never entails U.S. citizenship
in this vocabulary — `subject_to_jurisdiction` is load-bearing. The entire
Krikorian/Cooper-vs-Mayes/Newman debate is a debate about whether a specific,
real class of children (those with undocumented or temporary-visa parents)
falls inside or outside that one predicate's extension. `countermodel` did
not resolve that; it located it exactly.

## Test 3 — the Wong Kim Ark analogy, unextended: INVALID

Premises: `has_noncitizen_domiciled_parent(x) → subject_to_jurisdiction(x)` (the Wong Kim Ark rule both sides accept) + `@child is has_noncitizen_undocumented_parent.`
Conclusion: `@child is subject_to_jurisdiction.`
**Result: `Found`** — countermodel: `{has_noncitizen_undocumented_parent: [child]}`, `has_noncitizen_domiciled_parent` and `subject_to_jurisdiction` both empty.

This tests the "against ending" side's analogical move (Wong Kim Ark's
non-citizen parents ⟹ today's non-citizen parents are covered too) as a
*strict* deductive step. It is not one: the accepted Wong Kim Ark rule talks
only about **domiciled** non-citizen parents; nothing licenses transferring
its conclusion to **undocumented** parents without an extra, contested
premise. This is exactly Krikorian's rebuttal in the transcript (he
distinguishes legal, domiciled immigration from undocumented presence); the
analogy is doing real argumentative work that a citation to precedent alone
does not supply.

## Test 4 — adding the "keep it" side's bridging premise: VALID

Premises: Wong Kim Ark rule + `has_noncitizen_undocumented_parent(x) → subject_to_jurisdiction(x)` (Mayes/Newman's implicit extension) + `@child is has_noncitizen_undocumented_parent.`
Conclusion: `@child is subject_to_jurisdiction.`
**Result: `NotFound` (entails).** Once the contested premise is granted, the
conclusion follows validly — unsurprising (it's the added premise doing
direct work), but it confirms the "keep it" side's argument is internally
valid, not merely rhetorically appealing.

## Test 5 — the "end it" side's own bridging premise: also VALID (from their premise)

Premises: `has_noncitizen_undocumented_parent(x) → not subject_to_jurisdiction(x)` (Krikorian/Cooper's implicit extension — the exact negation of test 4's added premise) + `@child is has_noncitizen_undocumented_parent.`
Conclusion: `not (@child is subject_to_jurisdiction).`
**Result: `NotFound` (entails).**

Tests 4 and 5 together show that **both sides reason validly from their own,
mutually contradictory, premise about what "subject to the jurisdiction
thereof" covers.** Neither side is committing a logical error; VE's checker
cannot referee between the two premises, because doing so requires
historical, textual, and precedential judgment (what did "jurisdiction" mean
in 1868; how far does Wong Kim Ark's holding generalize) that is outside a
finite relational structure. This is the debate's actual content, and it is
squarely a **definitional** dispute (over the correct extension of one
predicate), not a factual or values dispute, and not a logical one.
