from __future__ import annotations

import json
from pathlib import Path

from src.rules.models import Rule


class RuleStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path
        self._rules: list[Rule] = []
        if path and path.exists():
            self._load()

    def _load(self) -> None:
        try:
            data = json.loads(self.path.read_text())
            self._rules = [Rule.model_validate(r) for r in data]
        except Exception:
            self._rules = []

    def save(self) -> None:
        if not self.path:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [r.model_dump(mode="json") for r in self._rules]
        self.path.write_text(json.dumps(payload, indent=2, default=str))

    def add(self, rule: Rule) -> None:
        self._rules.append(rule)

    def remove(self, rule_id: str) -> None:
        self._rules = [r for r in self._rules if r.rule_id != rule_id]

    def clear(self) -> None:
        self._rules = []

    def all(self) -> list[Rule]:
        return list(self._rules)

    def __len__(self) -> int:
        return len(self._rules)
