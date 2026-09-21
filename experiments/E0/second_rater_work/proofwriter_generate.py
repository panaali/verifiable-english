"""Generate the blinded E0 ProofWriter second-rating records.

The controlled-English normalization is intentionally recorded as data below so
that every source premise can be audited against its v0 rendering.
"""
import json
import sys
from pathlib import Path
sys.path.insert(0, "/private/tmp/ve-e0-integration")
from ve import Environment
import ve
from ve.check import check

ROOT = Path(__file__).parents[1]
SRC = ROOT / "survey_samples/_drawn/proofwriter.json"
OUT = Path(__file__).with_name("proofwriter.jsonl")

# Logical forms use p(a), r(a,b), ~p(a), conjunction &, and implication ->.
# A bare lower-case x denotes the universally quantified source variable.
# Entries later named in EXCLUDED are retained only as rejected, lossy draft
# decompositions for audit history. They are never emitted as v0 witnesses.
FORMS = {
"AttNoneg-OWA-D3-1678#row58201": ["green(dave)","furry(erin)","green(erin)","kind(fiona)","rough(fiona)","round(fiona)","green(harry)","kind(harry)","rough(harry)","round(harry)","kind(x)&green(x)->furry(x)","green(dave)->kind(dave)","kind(dave)&furry(dave)->rough(dave)","rough(fiona)&round(fiona)->quiet(fiona)","kind(x)->quiet(x)","furry(x)&quiet(x)->round(x)","~rough(harry)"],
"AttNeg-OWA-D1-2570#row81100": ["young(anne)","green(erin)","young(harry)","young(x)->~green(x)","big(x)&green(x)->nice(x)","young(x)&quiet(x)->~nice(x)","quiet(harry)->~nice(harry)","big(x)&nice(x)->round(x)","green(x)&~young(x)->quiet(x)","~white(harry)"],
"AttNoneg-OWA-D2-1054#row27258": ["white(bob)","smart(dave)","blue(fiona)","young(harry)","blue(x)&smart(x)->rough(x)","smart(x)->blue(x)","~white(harry)"],
"AttNeg-OWA-D3-1247#row63340": ["blue(anne)","~white(fiona)","young(gary)","white(harry)","furry(x)->round(x)","blue(x)->furry(x)","rough(x)&young(x)->kind(x)","rough(fiona)&white(fiona)->~young(fiona)","round(x)->white(x)","rough(x)->white(x)","rough(harry)->~white(harry)","kind(harry)&~round(harry)->rough(harry)","white(anne)"],
"AttNeg-OWA-D1-780#row81032": ["blue(bob)","cold(bob)","kind(bob)","young(bob)","green(erin)","round(erin)","blue(harry)","cold(harry)","~green(harry)","kind(harry)","quiet(harry)","young(harry)","green(x)&round(x)->quiet(x)","quiet(erin)"],
"AttNoneg-OWA-D0-5556#row48937": ["white(bob)","green(charlie)","nice(erin)","round(fiona)","round(x)->blue(x)","blue(x)->cold(x)","round(x)->green(x)","cold(x)&round(x)->nice(x)","cold(x)->nice(x)","green(x)->blue(x)","~white(bob)"],
"RelNeg-OWA-D0-6084#row3763": ["cold(cow)","nice(cow)","likes(cow,tiger)","needs(cow,tiger)","cold(tiger)","~nice(tiger)","red(tiger)","rough(tiger)","~young(tiger)","likes(tiger,cow)","~needs(tiger,cow)","visits(tiger,cow)","needs(x,cow)&likes(x,tiger)->~cold(tiger)","nice(x)->needs(x,tiger)","~cold(tiger)"],
"AttNonegNatLang-OWA-60#row11574": ["young(bob)","round(bob)","cold(bob)","red(bob)","big(bob)","rough(bob)","big(fred)","young(fred)","young(gary)","round(gary)","blue(gary)","rough(gary)","cold(x)&red(x)&round(x)->nice(x)","big(x)&round(x)->blue(x)","green(x)&red(x)->nice(x)","rough(x)->cold(x)","cold(x)&rough(x)->red(x)","young(x)&big(x)->rough(x)","big(x)&round(x)&cold(x)->nice(x)","~kind(fred)"],
"AttNoneg-OWA-D1-755#row54539": ["quiet(charlie)","rough(fiona)","quiet(x)->nice(x)","nice(x)->big(x)","young(charlie)->nice(charlie)","~quiet(charlie)"],
"AttNonegNatLang-OWA-211#row10260": ["round(alan)","rough(alan)","green(alan)","blue(charlie)","green(charlie)","blue(fred)","big(fred)","rough(fred)","green(gary)","red(gary)","cold(gary)","green(x)&cold(x)->blue(x)","young(x)&rough(x)&kind(x)->nice(x)","red(x)&green(x)&cold(x)->young(x)","green(x)&young(x)->nice(x)","round(x)&blue(x)&green(x)->young(x)","nice(x)&blue(x)&red(x)->kind(x)","nice(x)&kind(x)->cold(x)","kind(gary)"],
"AttNonegNatLang-OWA-2#row12794": ["blue(alan)","green(alan)","young(bob)","round(bob)","red(bob)","nice(bob)","big(charlie)","young(charlie)","round(fred)","rough(fred)","green(fred)","young(x)&round(x)->green(x)","green(x)&blue(x)&nice(x)->cold(x)","blue(x)&kind(x)&round(x)->nice(x)","round(x)&green(x)&nice(x)->blue(x)","young(x)&big(x)&round(x)->green(x)","nice(x)&kind(x)->cold(x)","~big(fred)"],
"AttNeg-OWA-D3-1064#row63240": ["furry(anne)","kind(anne)","~nice(anne)","quiet(anne)","green(charlie)","furry(erin)","nice(erin)","round(erin)","furry(fiona)","kind(fiona)","~nice(fiona)","round(fiona)","green(x)->~round(x)","round(charlie)->kind(charlie)","green(erin)->quiet(erin)","~round(charlie)->smart(charlie)","round(x)&~quiet(x)->furry(x)","smart(x)->furry(x)","~quiet(charlie)"],
"AttNonegNatLang-OWA-92#row10996": ["round(bob)","young(bob)","red(bob)","blue(bob)","nice(dave)","kind(dave)","blue(dave)","cold(dave)","big(eric)","young(eric)","blue(x)&rough(x)&kind(x)->round(x)","kind(x)&round(x)->cold(x)","big(x)->kind(x)","blue(x)&red(x)->big(x)","big(x)&blue(x)->young(x)","young(x)&big(x)&round(x)->green(x)","blue(x)&rough(x)&big(x)->cold(x)","~nice(bob)"],
"AttNoneg-OWA-D5-271#row67881": ["rough(bob)","red(charlie)","rough(charlie)","blue(erin)","rough(erin)","smart(erin)","blue(harry)","nice(harry)","red(harry)","rough(harry)","nice(x)->smart(x)","nice(x)->red(x)","red(x)&rough(x)->smart(x)","smart(x)&rough(x)->nice(x)","rough(x)->red(x)","round(x)&rough(x)->blue(x)","red(x)&big(x)->nice(x)","nice(x)&rough(x)->round(x)","nice(bob)->rough(bob)","big(harry)"],
"AttNeg-OWA-D3-1048#row31060": ["~smart(bob)","~quiet(dave)","red(dave)","round(dave)","smart(dave)","~white(dave)","young(dave)","smart(gary)","~green(harry)","red(harry)","smart(x)->green(x)","green(gary)->round(gary)","green(gary)&~red(gary)->smart(gary)","round(x)->young(x)","white(x)&quiet(x)->~round(x)","~green(dave)->quiet(dave)","~red(bob)"],
"RelNeg-OWA-D2-1099#row37111": ["nice(mouse)","likes(mouse,squirrel)","visits(mouse,squirrel)","red(squirrel)","~young(squirrel)","likes(squirrel,mouse)","visits(squirrel,mouse)","rough(squirrel)->visits(squirrel,mouse)","visits(x,squirrel)->visits(squirrel,mouse)","likes(x,squirrel)->red(squirrel)","needs(x,mouse)&red(x)->needs(mouse,squirrel)","likes(mouse,squirrel)->~needs(mouse,squirrel)","nice(mouse)&young(mouse)->~visits(mouse,squirrel)","~red(mouse)->likes(mouse,squirrel)","likes(x,squirrel)&~needs(x,squirrel)->visits(x,mouse)","~visits(mouse,mouse)"],
"RelNoneg-OWA-D2-372#row34143": ["chases(bald_eagle,dog)","blue(bald_eagle)","green(bald_eagle)","red(bald_eagle)","round(bald_eagle)","young(bald_eagle)","likes(bald_eagle,dog)","visits(bald_eagle,dog)","chases(dog,bald_eagle)","green(dog)","red(dog)","round(dog)","young(dog)","likes(dog,bald_eagle)","visits(dog,bald_eagle)","blue(bald_eagle)->chases(bald_eagle,dog)","chases(x,dog)->visits(dog,bald_eagle)","visits(x,dog)->chases(x,dog)","round(x)->visits(x,dog)","chases(x,dog)&chases(dog,bald_eagle)->visits(dog,bald_eagle)","likes(x,dog)->chases(dog,bald_eagle)","~visits(dog,dog)"],
"AttNoneg-OWA-D2-1717#row35179": ["quiet(charlie)","rough(gary)","round(gary)","smart(gary)","cold(harry)","round(harry)","smart(harry)","cold(x)->quiet(x)","rough(gary)->cold(gary)","~quiet(charlie)"],
"AttNeg-OWA-D1-1513#row83162": ["~big(bob)","nice(bob)","smart(bob)","big(fiona)","cold(fiona)","nice(fiona)","~big(gary)","green(gary)","smart(gary)","~white(gary)","smart(x)&white(x)->blue(x)","white(x)&blue(x)->~smart(x)","big(gary)->white(gary)","big(x)->white(x)","blue(bob)&~big(bob)->~green(bob)","smart(bob)&cold(bob)->white(bob)","white(fiona)"],
"RelNoneg-OWA-D1-63#row82168": ["chases(bald_eagle,rabbit)","big(bald_eagle)","cold(bald_eagle)","nice(bald_eagle)","rough(bald_eagle)","round(bald_eagle)","likes(bald_eagle,rabbit)","needs(bald_eagle,rabbit)","chases(rabbit,bald_eagle)","big(rabbit)","nice(rabbit)","rough(rabbit)","round(rabbit)","likes(rabbit,bald_eagle)","needs(rabbit,bald_eagle)","cold(x)&round(x)->needs(x,rabbit)","likes(x,bald_eagle)->likes(x,rabbit)","cold(x)->chases(x,bald_eagle)","rough(bald_eagle)"],
"RelNoneg-OWA-D5-992#row65395": ["nice(bear)","likes(bear,cat)","sees(bear,dog)","eats(cat,bear)","cold(cat)","sees(cat,bear)","eats(dog,bear)","eats(dog,lion)","blue(dog)","sees(dog,cat)","eats(lion,cat)","cold(lion)","likes(lion,bear)","likes(lion,cat)","big(x)->eats(x,dog)","cold(x)->nice(x)","blue(x)&sees(x,bear)->sees(x,dog)","eats(x,dog)->nice(dog)","blue(x)&sees(x,dog)->big(x)","eats(x,bear)&nice(x)->blue(x)","eats(x,bear)&sees(x,dog)->big(dog)","rough(cat)"],
"RelNeg-OWA-D5-771#row71601": ["needs(cat,dog)","sees(cat,rabbit)","needs(dog,squirrel)","chases(rabbit,dog)","chases(rabbit,squirrel)","cold(rabbit)","green(rabbit)","needs(rabbit,dog)","chases(squirrel,cat)","~blue(squirrel)","needs(squirrel,rabbit)","kind(x)->sees(x,dog)","sees(x,squirrel)->sees(squirrel,dog)","chases(squirrel,cat)->kind(cat)","blue(x)&red(x)->chases(x,dog)","green(cat)&sees(cat,dog)->needs(dog,rabbit)","blue(x)->~chases(x,squirrel)","sees(x,dog)->sees(x,squirrel)","chases(x,rabbit)->sees(rabbit,cat)","~sees(cat,squirrel)"],
"AttNoneg-OWA-D2-166#row33879": ["big(anne)","blue(anne)","cold(anne)","green(anne)","quiet(anne)","blue(charlie)","furry(charlie)","quiet(charlie)","green(gary)","quiet(gary)","cold(x)->blue(x)","green(x)->cold(x)","~big(anne)"],
"RelNoneg-OWA-D5-439#row72635": ["cold(bald_eagle)","green(bald_eagle)","needs(bald_eagle,lion)","visits(bald_eagle,rabbit)","sees(dog,lion)","cold(lion)","green(lion)","needs(lion,dog)","needs(lion,rabbit)","visits(lion,bald_eagle)","visits(lion,dog)","round(rabbit)","visits(rabbit,dog)","visits(rabbit,lion)","round(x)->rough(x)","visits(x,rabbit)&needs(x,bald_eagle)->visits(rabbit,bald_eagle)","rough(x)->visits(x,lion)","needs(dog,rabbit)&sees(rabbit,bald_eagle)->sees(bald_eagle,dog)","visits(rabbit,lion)&needs(rabbit,dog)->round(dog)","visits(x,rabbit)->needs(rabbit,bald_eagle)","visits(x,lion)&needs(lion,dog)->needs(x,dog)","~needs(dog,dog)"],
"RelNeg-OWA-D2-672#row37344": ["~chases(cat,tiger)","green(cat)","round(cat)","sees(cat,tiger)","chases(dog,mouse)","chases(dog,tiger)","green(dog)","sees(dog,mouse)","sees(dog,tiger)","visits(dog,cat)","chases(mouse,cat)","~round(mouse)","sees(mouse,cat)","~visits(mouse,cat)","visits(tiger,dog)","round(x)&~sees(x,dog)->~sees(x,cat)","sees(x,cat)&visits(cat,tiger)->visits(cat,mouse)","visits(x,mouse)->~chases(x,mouse)","sees(x,mouse)->chases(x,dog)","green(x)&sees(x,tiger)->sees(tiger,mouse)","chases(x,tiger)&~sees(x,cat)->sees(tiger,mouse)","sees(x,mouse)&~chases(mouse,tiger)->~chases(mouse,dog)","chases(x,dog)&sees(x,cat)->sees(dog,mouse)","~visits(tiger,mouse)"],
"AttNoneg-OWA-D5-189#row71830": ["blue(dave)","kind(dave)","rough(dave)","blue(erin)","furry(erin)","quiet(erin)","smart(erin)","blue(gary)","quiet(gary)","big(harry)","blue(x)->rough(x)","kind(x)&furry(x)->big(x)","kind(x)&big(x)->rough(x)","quiet(x)&kind(x)->rough(x)","kind(x)->furry(x)","big(x)->quiet(x)","quiet(x)->blue(x)","rough(x)->kind(x)","furry(gary)"],
"RelNeg-OWA-D3-464#row23356": ["~chases(bald_eagle,squirrel)","~chases(cow,bald_eagle)","chases(cow,squirrel)","cold(cow)","green(cow)","~nice(cow)","needs(cow,bald_eagle)","~needs(cow,squirrel)","chases(squirrel,cow)","eats(squirrel,bald_eagle)","~cold(squirrel)","needs(squirrel,cow)","chases(x,squirrel)&needs(x,cow)->needs(squirrel,bald_eagle)","eats(x,bald_eagle)&~cold(x)->needs(x,squirrel)","green(x)->needs(x,cow)","needs(x,bald_eagle)&needs(x,cow)->~eats(x,cow)","chases(x,cow)&~nice(x)->~needs(cow,bald_eagle)","round(bald_eagle)&~needs(bald_eagle,cow)->needs(cow,bald_eagle)","needs(squirrel,squirrel)"],
"RelNoneg-OWA-D1-1859#row80494": ["nice(bear)","nice(x)->cold(x)","big(x)&cold(x)->kind(x)","nice(bear)"],
"RelNoneg-OWA-D3-1163#row31346": ["likes(bear,mouse)","chases(mouse,bear)","visits(rabbit,bear)","rough(mouse)&visits(mouse,rabbit)->nice(mouse)","visits(x,rabbit)&visits(rabbit,bear)->nice(rabbit)","big(x)->chases(x,bear)","likes(x,mouse)->visits(x,rabbit)","chases(x,mouse)&chases(x,rabbit)->chases(rabbit,bear)","nice(x)&young(x)->green(x)","likes(x,rabbit)&visits(rabbit,bear)->visits(x,mouse)","nice(x)->visits(x,mouse)","~young(rabbit)"],
"RelNoneg-OWA-D0-1850#row7599": ["chases(bald_eagle,cat)","chases(bald_eagle,tiger)","blue(bald_eagle)","cold(bald_eagle)","nice(bald_eagle)","likes(bald_eagle,cat)","likes(bald_eagle,tiger)","visits(bald_eagle,cat)","visits(bald_eagle,tiger)","chases(cat,bald_eagle)","chases(cat,tiger)","big(cat)","blue(cat)","kind(cat)","visits(cat,bald_eagle)","visits(tiger,bald_eagle)","visits(cat,bald_eagle)&likes(cat,bald_eagle)->chases(bald_eagle,cat)","visits(x,cat)&chases(x,bald_eagle)->chases(cat,tiger)","visits(x,bald_eagle)&nice(bald_eagle)->big(x)","kind(bald_eagle)"],
}

EXCLUDED = {
    "AttNonegNatLang-OWA-60#row11574": (["frequency-or-default-quantification"], "The raw theory uses 'usually' and 'often' as frequency/default qualifiers. v0 has neither generalized frequency quantifiers nor default logic, so replacing them with universal implications would strengthen and lose the stated meaning."),
    "AttNonegNatLang-OWA-211#row10260": (["frequency-or-default-quantification", "epistemic-qualification"], "The raw theory includes 'often assumed' (an epistemic/default qualification) and 'usually'. v0 cannot express those qualifications, and treating them as strict universal implications is not faithful."),
    "AttNonegNatLang-OWA-2#row12794": (["frequency-or-default-quantification", "figurative-language-disambiguation"], "The raw theory uses 'tends to', 'usually', and figurative color language. v0 cannot preserve the default/frequency force; a strict Horn normalization would erase those qualifications."),
    "AttNonegNatLang-OWA-92#row10996": (["frequency-or-default-quantification", "figurative-language-disambiguation"], "The raw theory uses 'often' and 'usually' frequency/default claims as essential premises. v0 cannot express their force, so universally quantifying them would be a non-faithful strengthening."),
}

def atoms(form):
    import re
    return re.findall(r"~?([a-z_]+)\(([^)]*)\)", form)

def render_atom(token):
    neg = token.startswith("~")
    if neg: token = token[1:]
    p, args = token[:-1].split("(", 1)
    aa = args.split(",")
    ts = [a if a == "x" else "@" + a for a in aa]
    atom = f"{ts[0]} is {p}" if len(ts) == 1 else f"{ts[0]} {p} {ts[1]}"
    return f"not ({atom})" if neg else atom

def render(form):
    if "->" in form:
        lhs, rhs = form.split("->")
        parts = lhs.split("&")
        body = render_atom(parts[0])
        for part in parts[1:]: body = f"({body}) and ({render_atom(part)})"
        s = f"if ({body}), then ({render_atom(rhs)})"
    else:
        s = render_atom(form)
    if "x" in [a for _, arg in atoms(form) for a in arg.split(",")]:
        s = f"for every entity x, ({s})"
    return s + "."

def main():
    sample = json.loads(SRC.read_text())["sample"]
    assert len(sample) == len(FORMS) == 30
    records=[]
    for item in sample:
        if item["id"] in EXCLUDED:
            constructs, rationale = EXCLUDED[item["id"]]
            records.append({"dataset":"proofwriter","id":item["id"],"label":"OPAQUE","construct_needed":constructs,"rationale":rationale+" The remaining named-individual facts and strictly worded rules provide a useful relational skeleton, but not a faithful formalization of the complete theory.","formalization":None,"environment":None,"parse_result":{"status":"not_checked","reason":"No faithful full v0 formalization exists; the earlier strict-Horn normalization was rejected as lossy."},"reification":None,"opaque_boundary":"The frequency/default quantifiers and, where named in construct_needed, epistemic force or figurative-language disambiguation cannot be implemented in v0. Ordinary unary facts and strict rules remain relationally expressible.","statement_roles":None,"argument_binding":{"premises":"the complete raw theory","question":"the raw question","v0_document":None,"note":"No partial skeleton is recorded as a full witness; the raw question remains the conclusion/query rather than a premise."},"checker_provenance":{"commit":"12538d8d418b3eeec59e58d74c3886786e5139da","module":ve.__file__}})
            continue
        fs=FORMS[item["id"]]
        preds={}; consts=set()
        for f in fs:
            for p,argstr in atoms(f):
                name=p
                arity=len(argstr.split(","))
                preds[name]=arity
                consts.update(a for a in argstr.split(",") if a!="x")
        env={"language":"ve.core@0","profile":"relational-fol@0","spec_revision":"ve-v0-draft-2026-09-20","vocabulary":{"sorts":{"entity":{"description":"A named or quantified individual in this ProofWriter theory."}},"predicates":{p:{"arguments":["entity"]*a,"description":("Explicit negative " if p.startswith("neg_") else "Positive ")+f"ProofWriter predicate {p}."} for p,a in sorted(preds.items())},"constants":{c:{"sort":"entity","description":f"The individual named {c.replace('_',' ')}."} for c in sorted(consts)}}}
        source="\n".join(render(f) for f in fs)+"\n"
        result=check(Environment(env),source)
        records.append({"dataset":"proofwriter","id":item["id"],"label":"DIRECT","construct_needed":[],"rationale":"The complete theory and question are unary/binary function-free first-order facts and universally quantified implications, including ordinary explicit negation, all directly available in v0.","formalization":source,"environment":env,"parse_result":result,"reification":None,"statement_roles":[*(["premise"]*(len(fs)-1)),"question"],"argument_binding":{"premise_statement_indices":list(range(len(fs)-1)),"question_statement_index":len(fs)-1,"note":"The last parsed statement is the conclusion/query, not an asserted premise. The v0 document is a syntax witness; its document-level conjunction is not an entailment certificate."},"checker_provenance":{"commit":"12538d8d418b3eeec59e58d74c3886786e5139da","module":ve.__file__}})
    OUT.write_text("".join(json.dumps(r,separators=(",",":"))+"\n" for r in records))

if __name__ == "__main__": main()
