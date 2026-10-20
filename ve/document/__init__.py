"""ve-document@1: byte-partitioned source, reviewed metadata and P0 admission.

Front matter is JSON between two ``---`` lines. The source is every body byte
outside ``ve`` fences; unit spans are offsets into that exact byte sequence.
``ve <unit-id>`` fences supply an optional English or strict formula for a
unit. The JSON front matter may instead bind a formula AST or a W1 norm.

A ``ve-document@1`` document is checked by Lean's ``document`` mode (lean-first batch 16b): its checks, unit
statuses, identities and coverage are Lean's, and this module builds the document from that answer and displays
it. Python's own loader below (``_load_document``) runs only for a ``ve-document@2`` document after Lean's discourse
admission, and for a document the mode answers ``CheckerUnavailable`` or ``ResourceLimit`` for: the profiles,
contents and routes listed in docs/lean-first/b16b/DELTA.md, each retained until its batch composes it in the mode.

The package (architecture plan AR-16a, which split `ve/document.py` along its call graph; each module imports only
the ones before it):

- `source`: the text read, its front matter, source bytes, fences, unit parts, identities and environment;
- `containers`: the unit roles and containers both load paths build;
- `lean`: the relay of Lean's `document` mode and the binding of its answer to the document sent;
- `load`: `load_document`, and Python's own loader (the retained path);
- `report`: `check_document`, the coverage and the premises;
- `render`: `render_document`;
- `cli`: `ve document`.

The names below are those callers import from `ve.document`. A test that patches a name patches it in the module
that looks it up (for example `ve.document.load._load_document`), not here.
"""
from __future__ import annotations

from ..environment import Environment
from ..readings import rights_meaning_id
from ..wire import digest
from .source import (MAX_DOCUMENT_BYTES, STATUSES, SUPPORTS, _body, _english_fences, _environment, _parts, _split,
                     base_environment, front_matter, stored_identities)
from .containers import _content_bearing, _s1_attached
from .lean import _bind_document_answer, _document_case, _lean_answer, _lean_document
from .load import _content, _load_document, _meaning, load_document
from .report import (_check_narrowing_choices, _checking_environment, _fixed_and_active, _fixed_premises, _report,
                     check_document, coverage, coverage_defaults, quantity_admission_input)
from .render import render_document
from .cli import main
