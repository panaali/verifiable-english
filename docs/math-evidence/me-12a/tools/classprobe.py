"""Hand mutants of the review's two classes (me-12a review F1, F2), beyond trust_mutants' operators: every place the
meaning threads its values or names, and every child position, scope offset, arity, kind and rank of admission and
boundedness. Each is planted alone in ROOT/lean (restored after), then VE.Arith.Examples is built; a mutant is killed
when the build fails. Usage: classprobe.py ROOT OUT.json [LABEL #N ...]"""
import json, re, subprocess, sys, os
from pathlib import Path
root = Path(sys.argv[1]); out = Path(sys.argv[2]); only = set(sys.argv[3:])  # optional class labels
env = dict(os.environ, PATH=os.path.expanduser('~/.elan/bin') + ':' + os.environ['PATH'])
H, D = 'lean/VE/Arith/Holds.lean', 'lean/VE/Arith/Defs.lean'
def each(f, before, after, label):
    """One mutant per occurrence of `before` in `f`."""
    n = (root / f).read_text().count(before)
    assert n, (f, before)
    return [(f, before, after, i, f'{label} #{i + 1}') for i in range(n)]
M = []
# F1: the meaning loses its values or names.
M += each(H, 'Term.value E ρ ', 'Term.value E [] ', 'a term child read without the values')
M += each(H, 'Term.values E ρ ', 'Term.values E [] ', 'arguments read without the values')
M += each(H, 'Holds E ρ ', 'Holds E [] ', 'a formula child read without the values')
for b, x in [('((l + (i : Int)) :: ρ)', '(l + (i : Int))'), ('((n : Int) :: ρ)', '(n : Int)'), ('(n :: ρ)', 'n'),
             ('(i :: ρ)', 'i')]:
    M += each(H, b, f'[{x}]', f'a binder drops the outer values {b}')
    M += each(H, b, f'(ρ ++ [{x}])', f'a binder puts its value last {b}')
M += each(H, 'else E.funs g', 'else none', 'a function definition drops the earlier functions')
M += each(H, 'else E.preds q', 'else none', 'a predicate definition drops the earlier predicates')
M += each(H, '{ E with funs :=', '{ preds := fun _ => none, funs :=', 'a function definition clears the predicates')
M += each(H, '{ E with preds :=', '{ funs := fun _ => none, preds :=', 'a predicate definition clears the functions')
M += each(H, 'Term.value E xs body', 'Term.value ⟨fun _ => none, fun _ => none⟩ xs body', 'a body read without the earlier names')
M += each(H, 'Holds E xs body', 'Holds ⟨fun _ => none, fun _ => none⟩ xs body', 'a body read without the earlier names')
M += each(H, 'xs body', 'xs.reverse body', 'a body reads its arguments reversed')
# F2: admission and boundedness skip a position, misplace a scope, or ignore arity, kind or rank.
M += each(D, 'Term.sites k a ++ Term.sites k b', 'Term.sites k a', 'a right operand skipped')
M += each(D, 'Term.sites k a ++ Term.sites k b', 'Term.sites k b', 'a left operand skipped')
M += each(D, 'Formula.sites k φ ++ Formula.sites k ψ', 'Formula.sites k φ', 'a right formula skipped')
M += each(D, 'Formula.sites k φ ++ Formula.sites k ψ', 'Formula.sites k ψ', 'a left formula skipped')
M += each(D, '  | .not φ => Formula.sites k φ\n', '  | .not _ => []\n', 'under not skipped')
M += each(D, 'Formula.sites (k + 1) φ', '[]', 'a binder body skipped')
M += each(D, 'Formula.sites (k + 1) φ', 'Formula.sites k φ', 'a binder body read outside its binder')
M += each(D, 'Formula.sites (k + 1) φ', 'Formula.sites (k + 2) φ', 'a binder body read two binders deep')
M += each(D, 'Term.sites k lo ++ ', '', 'a range or count lo skipped')
M += each(D, 'Term.sites k hi ++ ', '', 'a range or count hi skipped')
M += each(D, 'Term.sites k lo', 'Term.sites (k + 1) lo', 'a range or count lo read inside its binder')
M += each(D, 'Term.sites k hi', 'Term.sites (k + 1) hi', 'a range or count hi read inside its binder')
M += each(D, '.count φ :: ', '', 'a count condition not checked')
M += each(D, 'args.length :: Term.sitesList k args', 'args.length :: []', 'call arguments skipped')
M += each(D, 'args.length ::', '1 ::', 'a call counts one argument')
M += each(D, '  | t :: ts => Term.sites k t ++ Term.sitesList k ts\n', '  | t :: _ => Term.sites k t\n', 'arguments after the first skipped')
M += each(D, 'if k ≤ i then [.free (i - k)]', 'if k < i then [.free (i - k)]', 'the first outer variable taken as bound')
M += each(D, '[.free (i - k)]', '[.free i]', 'an unscoped variable counted from the statement')
M += each(D, 'if j < depth then none', 'if j ≤ depth then none', 'a variable one past the parameters admitted')
M += each(D, 'd.name == f && d.isPred == pred', 'd.name == f', 'the kind of a call ignored')
M += each(D, 'match earlier.find?', 'match D.find?', 'a later definition callable')
M += each(D, 'if d.arity = argc', 'if d.arity ≤ argc', 'extra arguments admitted')
M += each(D, 'if d.arity = argc', 'if argc ≤ d.arity', 'missing arguments admitted')
M += each(D, 'if Formula.bnd B φ then none else some .unboundedCount', 'none', 'a count condition admitted unbounded')
M += each(D, '(D.take k).any (·.name == d.name)', '(D.take k).any (fun e => e.name == d.name && e.isPred == d.isPred)', 'a name across kinds not a duplicate')
M += each(D, '(D.take k).any (·.name == d.name)', '((D.take k).drop 1).any (·.name == d.name)', 'a duplicate of the first definition missed')
M += each(D, 's.refusal D (D.take k) n', 's.refusal D (D.take k) 0', 'a body without its parameters')
M += each(D, 's.refusal D (D.take k) n', 's.refusal D (D.take k) (n + 1)', 'a body with one parameter too many')
M += each(D, 's.refusal D (D.take k) n', 's.refusal D (D.take (k + 1)) n', 'a body may call itself')
M += each(D, 'Site.refusal D D 0 (some D.boundedNames)', 'Site.refusal D D 1 (some D.boundedNames)', 'a statement with one value in scope')
M += each(D, 'Site.refusal D D 0 (some D.boundedNames)', 'Site.refusal D D 0 none', 'a statement count not checked')
for a, b in [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (0, 5)]:
    names = ['duplicateName _', 'unscopedVariable _', 'unknownDefinition _', 'recursiveDefinition _', 'arityMismatch ..', 'unboundedCount']
    M += each(D, f'  | .{names[a]} => {a}\n', f'  | .{names[a]} => {b}\n', f'rank {a} becomes {b}')
M += each(D, 'best.all (r.rank < ·.rank)', 'best.all (r.rank ≤ ·.rank)', 'the last refusal of the lowest rank')
M += each(D, 'best.all (r.rank < ·.rank)', 'best.isNone', 'the first refusal whatever its rank')
M += each(D, 'Term.bnd B a && Term.bnd B b', 'Term.bnd B a', 'boundedness skips a right term')
M += each(D, 'Term.bnd B a && Term.bnd B b', 'Term.bnd B b', 'boundedness skips a left term')
M += each(D, 'Formula.bnd B φ && Formula.bnd B ψ', 'Formula.bnd B φ', 'boundedness skips a right formula')
M += each(D, 'Formula.bnd B φ && Formula.bnd B ψ', 'Formula.bnd B ψ', 'boundedness skips a left formula')
M += each(D, '  | .not φ => Formula.bnd B φ\n', '  | .not _ => true\n', 'boundedness skips under not')
M += each(D, 'Term.bnd B lo && Term.bnd B hi && Formula.bnd B φ', 'Term.bnd B hi && Formula.bnd B φ', 'boundedness skips lo')
M += each(D, 'Term.bnd B lo && Term.bnd B hi && Formula.bnd B φ', 'Term.bnd B lo && Formula.bnd B φ', 'boundedness skips hi')
M += each(D, 'Term.bnd B lo && Term.bnd B hi && Formula.bnd B φ', 'Term.bnd B lo && Term.bnd B hi', 'boundedness skips a body')
for q in ['allNat', 'exNat', 'allInt', 'exInt']:
    M += each(D, f'  | .{q} _ => false', f'  | .{q} _ => true', f'{q} counted as bounded')
M += each(D, 'B f && Term.bndList B args', 'Term.bndList B args', 'boundedness ignores the function called')
M += each(D, 'B p && Term.bndList B args', 'Term.bndList B args', 'boundedness ignores the predicate called')
M += each(D, 'B f && Term.bndList B args', 'B f', 'boundedness skips function arguments')
M += each(D, 'B p && Term.bndList B args', 'B p', 'boundedness skips predicate arguments')
M += each(D, '  | t :: ts => Term.bnd B t && Term.bndList B ts\n', '  | t :: _ => Term.bnd B t\n', 'boundedness skips later arguments')
M += each(D, 'then Term.bnd B body else B g', 'then Term.bnd B body else false', 'a function definition forgets earlier bounds')
M += each(D, 'then Formula.bnd B body else B q', 'then Formula.bnd B body else false', 'a predicate definition forgets earlier bounds')
M += each(D, 'then Term.bnd B body else B g', 'then true else B g', 'a function counted bounded whatever its body')
M += each(D, 'then Formula.bnd B body else B q', 'then true else B q', 'a predicate counted bounded whatever its body')
# F2 (re-check): two refusals of one kind reported out of the request's order, and the meaning's and admission's
# remaining reads (arity, the last definition, a later statement, a refusal's value).
M += each(D, '| .add a b | .sub a b | .mul a b => Term.sites k a ++ Term.sites k b',
          '| .add a b | .sub a b | .mul a b => Term.sites k b ++ Term.sites k a', 'order: term operands right first')
M += each(D, '| .eq a b | .lt a b | .le a b | .dvd a b => Term.sites k a ++ Term.sites k b',
          '| .eq a b | .lt a b | .le a b | .dvd a b => Term.sites k b ++ Term.sites k a', 'order: comparison right first')
M += each(D, 'Formula.sites k φ ++ Formula.sites k ψ', 'Formula.sites k ψ ++ Formula.sites k φ', 'order: connective right first')
M += each(D, '| t :: ts => Term.sites k t ++ Term.sitesList k ts', '| t :: ts => Term.sitesList k ts ++ Term.sites k t',
          'order: arguments last first')
M += each(D, '.call false f args.length :: Term.sitesList k args', 'Term.sitesList k args ++ [.call false f args.length]',
          'order: a function call after its arguments')
M += each(D, '.call true p args.length :: Term.sitesList k args', 'Term.sitesList k args ++ [.call true p args.length]',
          'order: a predicate call after its arguments')
M += each(D, 'Term.sites k lo ++ Term.sites k hi ++ .count φ :: Formula.sites (k + 1) φ',
          'Term.sites k hi ++ Term.sites k lo ++ .count φ :: Formula.sites (k + 1) φ', 'order: a count hi before lo')
M += each(D, 'Term.sites k lo ++ Term.sites k hi ++ .count φ :: Formula.sites (k + 1) φ',
          'Formula.sites (k + 1) φ ++ Term.sites k lo ++ Term.sites k hi ++ [.count φ]', 'order: a count condition first')
M += each(D, 'Term.sites k lo ++ Term.sites k hi ++ Formula.sites (k + 1) φ',
          'Term.sites k hi ++ Term.sites k lo ++ Formula.sites (k + 1) φ', 'order: a range hi before lo')
M += each(D, 'Term.sites k lo ++ Term.sites k hi ++ Formula.sites (k + 1) φ',
          'Formula.sites (k + 1) φ ++ Term.sites k lo ++ Term.sites k hi', 'order: a range body first')
M += each(D, '(List.range D.length).flatMap', '(List.range D.length).reverse.flatMap', 'order: definitions last first')
M += each(D, 'firstRefusal (D.refusals ++ φs.flatMap', 'firstRefusal (D.refusals ++ φs.reverse.flatMap', 'order: statements last first')
M += each(D, 'firstRefusal (D.refusals ++ φs.flatMap fun φ =>\n    (Formula.sites 0 φ).filterMap (Site.refusal D D 0 (some D.boundedNames)))',
          'firstRefusal ((φs.flatMap fun φ =>\n    (Formula.sites 0 φ).filterMap (Site.refusal D D 0 (some D.boundedNames))) ++ D.refusals)',
          'order: statements before definitions')
M += each(H, 'if xs.length = n then g xs else none', 'g xs', 'reads: the meaning ignores a function arity')
M += each(H, 'xs.length = n ∧ P xs', 'P xs', 'reads: the meaning ignores a predicate arity')
M += each(D, '((List.range D.length).filterMap', '((List.range (D.length - 1)).filterMap', 'reads: the last duplicate missed')
M += each(D, '(List.range D.length).flatMap', '(List.range (D.length - 1)).flatMap', 'reads: the last body unchecked')
M += each(D, 'firstRefusal (D.refusals ++ φs.flatMap', 'firstRefusal (D.refusals ++ (φs.take 1).flatMap', 'reads: later statements unchecked')
M += each(D, 'Term.sites 0 body', 'Term.sites 1 body', 'reads: a function body under one binder')
M += each(D, 'Formula.sites 0 body', 'Formula.sites 1 body', 'reads: a predicate body under one binder')
M += each(D, 'filterMap (Site.refusal D D depth none)', 'filterMap (Site.refusal D D 0 none)', 'reads: Scoped ignores its depth')
M += each(D, '| none => some (.recursiveDefinition f)', '| none => some (.unknownDefinition f)', 'reads: recursion reported unknown')
M += each(D, 'some (.arityMismatch f d.arity)', 'some (.arityMismatch f argc)', 'reads: the arity reported is the call\'s')
M += each(D, 'some (.unscopedVariable j)', 'some (.unscopedVariable (j - depth))', 'reads: unscoped counted past the scope')
M += each(D, 'some (.duplicateName d.name)', 'some (.duplicateName "")', 'reads: a duplicate without its name')
M += each(D, 'else some (.unknownDefinition f)', 'else none', 'reads: an unknown call admitted')
# Re-check F6: of several names each defined twice, which is reported (the name defined again first), and F7: Scoped
# reads no boundedness.
M += each(D, '((List.range D.length).filterMap', '((List.range D.length).reverse.filterMap', 'order: duplicates last first')
M += each(D, '(D.take k).any (·.name == d.name)', '(D.drop (k + 1)).any (·.name == d.name)', 'order: a duplicate reported at its first definition')
M += each(D, '(D.take k).any (·.name == d.name)', '(D.eraseIdx k).any (·.name == d.name)', 'order: a duplicate reported at every definition')
M += each(D, 'filterMap (Site.refusal D D depth none)', 'filterMap (Site.refusal D D depth (some D.boundedNames))', 'reads: Scoped checks boundedness')
# Equivalent, not planted: `Defs.boundedNames (D.take k)` -> `Defs.boundedNames D` in `Defs.refusals`. A count's
# condition sees a later bound only by calling a later name (RecursiveDefinition or UnknownDefinition) or a name
# defined again (DuplicateName), each of a lower rank than UnboundedCount, so `caseRefusal` and `WellFormed` agree.
# Equivalent, not planted: the duplicate pass after the sites' pass. DuplicateName has the lowest rank, so
# `firstRefusal` reports it wherever it stands, and `WellFormed` reads only emptiness.
results = []
for f, before, after, i, label in M:
    if only and label not in only: continue
    path = root / f
    orig = path.read_text()
    at = [m.start() for m in re.finditer(re.escape(before), orig)][i]
    path.write_text(orig[:at] + after + orig[at + len(before):])
    try:
        r = subprocess.run(['timeout', '900', 'lake', 'build', 'VE.Arith.Examples'], cwd=root / 'lean', env=env,
                           capture_output=True, text=True)
    finally:
        path.write_text(orig)
    errs = sorted(set(re.findall(r'error: VE/Arith/(\w+\.lean:\d+)', r.stdout + r.stderr)))
    own = Path(f).name
    status = ('SURVIVED' if r.returncode == 0 else 'KILLED' if any(not e.startswith(own) for e in errs)
              else 'OWN-ERROR')
    results.append({'file': f, 'class': label, 'before': before, 'after': after, 'occurrence': i + 1,
                    'status': status, 'errors': errs[:8]})
    print(status, label, '|', ' '.join(errs[:4]), flush=True)
# Every mutant's source is restored; rebuild it so no mutant's .olean outlives the probe (re-check F8).
subprocess.run(['lake', 'build', 'VE.Arith.Examples'], cwd=root / 'lean', env=env, capture_output=True, check=True)
out.write_text(json.dumps({'note': __doc__.split('\n')[0], 'mutants': results,
                           'survived': sum(r['status'] == 'SURVIVED' for r in results)}, indent=1, ensure_ascii=False) + '\n')
sys.exit(1 if any(r['status'] != 'KILLED' for r in results) else 0)
