# per-answer ownership trace of every RSP key item on the kb-10b-switch branch, one fresh process per item
O=/tmp/kb10bs/own; W=/home/seyran/code/ve-kb-10b-switch; PY=$W/.venv/bin/python
export VE_LEAN_SERVICE=$W/lean/.lake/build/bin/ve_service
mkdir -p $O/items; cd $W
$PY -c "import json;print('\n'.join(k['id'] for k in json.load(open('usecases/anthropic-rsp/answer-key.json'))['items']))" > $O/ids.txt
export O PY
xargs -P 6 -I{} sh -c 'f=$(echo "{}" | tr "/" "_"); timeout 1800 $PY $O/trace_item_callers.py usecases/anthropic-rsp "{}" $O/items/$f.json > $O/items/$f.log 2>&1; echo "{} rc=$?"' < $O/ids.txt
echo ALLDONE
