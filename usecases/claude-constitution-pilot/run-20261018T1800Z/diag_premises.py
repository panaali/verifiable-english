import sys, time, json
sys.path.insert(0,'.')
import ve.search as S
import ve.readings_verdicts as RV
orig = S.find_countermodel
def wrapped(env, premises, conclusion, **kw):
    t=time.monotonic()
    try:
        r = orig(env, premises, conclusion, **kw)
        print("find_countermodel", {k:v for k,v in kw.items() if k!='sort_bounds'}, "sort_bounds", kw.get('sort_bounds'), "->", r.status, getattr(r,'detail',None), round(time.monotonic()-t,1), "s", flush=True)
        return r
    except Exception as e:
        print("find_countermodel EXC", type(e).__name__, str(e)[:200], round(time.monotonic()-t,1), flush=True); raise
S.find_countermodel = wrapped
import ve.document as D
doc = D.load_document(sys.argv[1])
ctx = RV.context(doc)
print(type(ctx).__name__)
t=time.monotonic()
print(json.dumps(ctx.premises())[:400], round(time.monotonic()-t,1))
