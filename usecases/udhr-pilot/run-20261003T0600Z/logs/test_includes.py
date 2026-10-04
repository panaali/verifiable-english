import sys, json
from copy import deepcopy
from pathlib import Path
HERE=Path('.').resolve()
sys.path.insert(0,str(HERE))
import s1doc as S
from ve.readings import s1_content_meaning_id
P=S.P
meta, src = S.read(HERE.parent/'prev-run-20261002T1800Z'/'translation.ve.md')
meta, env = S.to_s1(meta)
# a right_lines set for u067 naming right 18 (declared by every candidate of rs_u066)
node={"name":"test-change-religion","predicate":"avoid_thought_conscience_religion_required","sign":True,"guard":["top"],"unless":[],"over":[]}
line={"kind":"claim","holder_slot":None,"cites":{},"norm":node}
readings=[]
for cid in ("a","b"):
    n=dict(node,name=f"test-change-religion-{cid}")
    r={"id":cid,"kind":"right_lines","content":{"right_lines":{"right":"freedom-of-thought-conscience-and-religion","lines":[dict(line,norm=n)]}}}
    r["meaning_id"]=s1_content_meaning_id(env,"rs_u067",r)
    r["admission"]={"who":"translator","why":"test","distinguishing_models":{}}
    readings.append(r)
for r in readings: r["admission"]["distinguishing_models"]={o["id"]:"pending" for o in readings if o["id"]!=r["id"]}
unit=[u for u in meta['units'] if u['id']=='u067'][0]
unit['kind']='right_lines'
meta['reading_sets'].append({"id":"rs_u067","unit":"u067","version":1,"status":"open","readings":readings})
try:
    P.find_situations(meta)
    print("no error")
except Exception as e:
    print(type(e).__name__, getattr(e,'message',str(e)))
