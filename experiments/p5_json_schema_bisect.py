"""Record of the 2026-09-22 flash-lite schema-acceptance bisection (v12 400).

Usage: ITEM=0 python -m experiments.p5_json_schema_bisect full,wire response_schema
"""
import json, sys
from google import genai
from google.genai import types
from experiments import p5 as p
from experiments import p5_json_authoring as j
LOG = j.BISECT_LOG
client = genai.Client(vertexai=True, project="project-5ee49d39-f814-4ff7-861", location="global",
    http_options=types.HttpOptions(timeout=60000, retry_options=types.HttpRetryOptions(attempts=1)))
item = p.materials('dev')[int(__import__('os').environ.get('ITEM','0'))]
base = j.schema(item['payload'])

def strip(s, keys):
    if isinstance(s, dict):
        return {k: strip(v, keys) for k, v in s.items() if k not in keys}
    if isinstance(s, list):
        return [strip(v, keys) for v in s]
    return s

def attempt(name, schema, field, model='gemini-2.5-flash-lite'):
    kw = {field: schema}
    cfg = types.GenerateContentConfig(temperature=0, max_output_tokens=16, response_mime_type='application/json', **kw)
    rec = {'name': name, 'field': field, 'model': model}
    try:
        r = client.models.generate_content(model=model, contents='Return JSON.', config=cfg)
        u = r.usage_metadata
        rec.update(ok=True, prompt=u.prompt_token_count, out=(u.candidates_token_count or 0) + (u.thoughts_token_count or 0))
    except Exception as e:
        rec.update(ok=False, error=str(e)[:300])
    open(LOG, 'a').write(json.dumps(rec) + '\n')
    print(rec, flush=True)

def wire(s):
    if isinstance(s, dict):
        out = {k: wire(v) for k, v in s.items() if k not in ('minItems', 'maxItems')}
        if s.get('minItems') == 1: out['minItems'] = 1
        return out
    if isinstance(s, list): return [wire(v) for v in s]
    return s
variants = {
  'wire': wire(base),
  'full': base,
  'no_additionalProperties': strip(base, {'additionalProperties'}),
  'no_minmax_int': strip(base, {'minimum', 'maximum'}),
  'no_items_bounds': strip(base, {'minItems', 'maxItems'}),
  'no_all3': strip(base, {'additionalProperties', 'minimum', 'maximum', 'minItems', 'maxItems'}),
}
for field in sys.argv[2:]:
  for name in sys.argv[1].split(','):
    attempt(name, variants[name], field)
