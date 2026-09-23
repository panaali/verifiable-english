"""``ve assist``: interactive, sentence-level assisted formalisation.

See ``session.AssistSession`` (actions + ledger), ``api`` (JSON tool calling),
``cli`` (``python -m ve assist``), ``proposer`` (injected-model candidates) and
``premises`` (off-by-default premise suggestions) and ``verify`` (evaluator-side ledger
verification against the dossier and the calls ledger).
"""
from .api import call_tool, tool_schemas, tools_for_session
from .session import AssistError, AssistSession, LedgerReplayError
from .sources import load_source, p5_environment, select_p5_item, source_from_p5, source_from_text, split_sentences
from .verify import verify_session

__all__ = ["AssistError", "AssistSession", "LedgerReplayError", "call_tool", "load_source", "p5_environment",
           "select_p5_item", "source_from_p5", "source_from_text", "split_sentences", "tool_schemas",
           "tools_for_session", "verify_session"]
