"""Wall time of the document mode against the retained loader on this chain, least of 7 (the numbers in REPORT.md)."""
import time,statistics,json
from pathlib import Path
from tests.document_chain_corpus import *
from ve.document import load
from ve.backends.relay import answer
import os,resource
retained=load._load_document
def cpu_children():
    r=resource.getrusage(resource.RUSAGE_CHILDREN); return r.ru_utime+r.ru_stime
for name,raw in (('u0073.s05',chain_document('u0073.s05')),('rd9#lower',corpus()[0]['tests/data/rd9-docroute.ve.md#lower'])):
    ts=[]
    for _ in range(7):
        t=time.perf_counter(); r,e=answer('document',{'id':'document','document':raw.decode(),'admit':True}); ts.append(time.perf_counter()-t)
    print(name,'lean document mode wall s (least of 7):',round(min(ts),4),'err',e)
    ts=[]
    for _ in range(7):
        t=time.perf_counter(); retained(raw,Path('d.ve.md'),{}); ts.append(time.perf_counter()-t)
    print(name,'retained loader wall s (least of 7):',round(min(ts),4))
