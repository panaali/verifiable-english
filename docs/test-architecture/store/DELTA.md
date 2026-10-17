# tarch-store: user-visible delta

None. The answer store is test infrastructure for R1 runs (`tests/answer_store.py`). It is off unless a pytest run
asks for it, and `tools/gate.py` refuses it. With no store installed, every run but such an R1 run, and every product
use of `ve`, the client builds the same request line as before (`LeanService._line` with no store is
`_request_line(nonce, ...)`) and reads the process's answer as before. No diagnostic, verdict, field, limit or fault
order changes.

The two new client tests (RLIMIT_AS and RSS recycle) check behaviour that already existed.
