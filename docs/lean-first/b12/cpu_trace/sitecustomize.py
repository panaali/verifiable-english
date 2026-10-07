import json
import os
from collections import Counter
from ve.backends import lean_service as service

_original_stop = service.LeanService._stop
_original_request = service.LeanService._request

def _counted_request(self, mode, *args, **kwargs):
    counts = getattr(self, '_bench_modes', None)
    if counts is None:
        counts = self._bench_modes = Counter()
    counts[mode] += 1
    return _original_request(self, mode, *args, **kwargs)

def _recorded_stop(self, graceful):
    proc = self._proc
    if proc is not None:
        value = service._cpu_seconds(proc.pid)
        if value is not None:
            path = os.environ.get('VE_BENCH_CPU_LOG')
            if path:
                fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
                try:
                    os.write(fd, (json.dumps({'owner': os.getpid(), 'pid': proc.pid, 'cpu_s': value,
                                              'modes': dict(getattr(self, '_bench_modes', {})),
                                              'stats': self.stats}) + '\n').encode())
                finally:
                    os.close(fd)
    return _original_stop(self, graceful)

service.LeanService._request = _counted_request
service.LeanService._stop = _recorded_stop
