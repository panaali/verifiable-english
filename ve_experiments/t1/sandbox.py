"""Fail-closed macOS Seatbelt sandbox for untrusted Python; no host credentials."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def run_python(code, item, timeout=15):
    if not shutil.which('sandbox-exec'):
        raise RuntimeError('Trusted sandbox unavailable: sandbox-exec required; no unsafe fallback')
    with tempfile.TemporaryDirectory(prefix='ve-t1-sandbox-', dir='/private/tmp') as tmp:
        root = Path(tmp).resolve()
        for filename, body in item['raw'].items():
            (root/filename).write_text(body)
        (root/'query.json').write_text(json.dumps({k:item[k] for k in ('user','target','claim','positive')}))
        (root/'solution.py').write_text(code)
        (root/'entry.py').write_text('import resource, runpy\nresource.setrlimit(resource.RLIMIT_CPU,(10,10))\nresource.setrlimit(resource.RLIMIT_FSIZE,(262144,262144))\nresource.setrlimit(resource.RLIMIT_NOFILE,(32,32))\nrunpy.run_path("solution.py",run_name="__main__")\n')
        interpreter = Path(sys.executable).resolve()
        quote = lambda s: json.dumps(str(s))
        profile = '(version 1) (deny default) (allow process-exec (literal '+quote(interpreter)+') (literal '+quote(Path(sys.base_prefix).resolve()/'Resources/Python.app/Contents/MacOS/Python')+')) (allow sysctl-read) (allow file-read-metadata)\n'
        # System runtime reads exclude user trees, private state, mounts and other temp jobs.
        exclusions = ['/Users','/private/var','/Volumes','/private/tmp']
        profile += '(allow file-read* (require-all '+ ' '.join('(require-not (subpath '+quote(p)+'))' for p in exclusions) + '))\n'
        profile += '(allow file-read* (subpath '+quote(root)+'))\n'
        profile += '(allow file-write* (subpath '+quote(root)+') (literal "/dev/null"))\n'
        # No network, process-fork, arbitrary exec, home/repo reads, or environment credentials.
        with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
            try:
                proc = subprocess.run(['/usr/bin/sandbox-exec','-p',profile,str(interpreter),'-I','-S',str(root/'entry.py')],
                    cwd=root, env={'PATH':'/usr/bin:/bin','LANG':'C','HOME':str(root),'TMPDIR':str(root)},
                    stdout=out, stderr=err, timeout=timeout)
                out.seek(0); err.seek(0)
                stdout, stderr = out.read(262144).decode(errors='replace'), err.read(262144).decode(errors='replace')
                if 'sandbox_apply' in stderr or 'sandbox-exec:' in stderr:
                    raise RuntimeError('Trusted sandbox initialization failed: '+stderr[-500:])
                if proc.returncode != 0:
                    return {'valid':False,'returncode':proc.returncode,'error':stderr[-2000:]}
                answer = json.loads(stdout)
                if set(answer) != {'reachable'} or type(answer['reachable']) is not bool:
                    raise ValueError('expected exactly {"reachable": boolean}')
                return {'valid':True,'reachable':answer['reachable'], 'claim_supported':answer['reachable']==item['positive'],
                        'scope':'agent code executed on original source files; execution does not certify code correctness'}
            except (subprocess.TimeoutExpired, ValueError) as exc:
                return {'valid':False,'error':type(exc).__name__+': '+str(exc)}
