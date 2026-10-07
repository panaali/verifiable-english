"""Registry of test-only wire contract hooks used by legacy profile contracts."""

from dataclasses import dataclass
from typing import Callable

@dataclass
class Registry:
    hooks: dict[str, Callable]
    classifiers: dict[str, Callable]
    views: dict[str, Callable]
    adapters: dict[str, Callable]

    def __init__(self):
        self.hooks, self.classifiers, self.views, self.adapters = {}, {}, {}, {}

    def register(self, *, hooks=None, classifiers=None, views=None, adapters=None):
        for attr, entries in (("hooks", hooks), ("classifiers", classifiers),
                              ("views", views), ("adapters", adapters)):
            if entries:
                getattr(self, attr).update(entries)
        return self
