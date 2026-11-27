"""The web app's own assistant model table.

ve_experiments.claude_cli.MODELS pins the frozen experiment models and is not
changed here. The web app adds Claude Sonnet 5.5 as its default; the ledger,
call caps and account selection are the experiment client's, unchanged.
"""
from dataclasses import asdict, dataclass
from pathlib import Path

from ve_experiments.assist_haiku import ClaudeProposer
from ve_experiments.claude_cli import MODELS as EXPERIMENT_MODELS, ClaudeCLI, Controls

ASSIST_MODELS = {"sonnet-5.5": "claude-sonnet-5-5",
                 **{name: EXPERIMENT_MODELS[name] for name in ("haiku", "sonnet", "opus")}}
DEFAULT_ASSIST_MODEL = "sonnet-5.5"


@dataclass(frozen=True)
class AssistControls(Controls):
    """Controls whose model comes from ASSIST_MODELS instead of the experiment pins."""
    def __post_init__(self):
        if self.model not in ASSIST_MODELS.values():
            raise ValueError("Use a model id from the web app's assistant table")
        # Every other check of the experiment controls still applies.
        Controls(**{**asdict(self), "model": EXPERIMENT_MODELS["haiku"]})


class AssistProposer(ClaudeProposer):
    """ClaudeProposer for a web app model; the CLI client, ledger and account are the same."""
    def __init__(self, ledger, *, model, controls, account_config_dir, allow_builtin_agents_md=False):
        if model not in ASSIST_MODELS or controls.model != ASSIST_MODELS[model]:
            raise ValueError("Proposer model and controls model must match")
        self.model, self.model_id = model, controls.model
        self.client = ClaudeCLI(Path(ledger), controls, None, account_config_dir=account_config_dir,
                                allow_builtin_agents_md=allow_builtin_agents_md)
