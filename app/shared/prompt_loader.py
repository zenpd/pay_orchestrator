from __future__ import annotations
import functools
from pathlib import Path
import yaml
from shared.logger import get_logger

log = get_logger("shared.prompt_loader")
_PROMPTS_DIR = Path(__file__).parent.parent / "config" / "prompts"


class PromptManager:
    def __init__(self) -> None:
        self._cache: dict[str, dict] = {}

    def load(self, agent_name: str) -> dict:
        if agent_name in self._cache:
            return self._cache[agent_name]
        path = _PROMPTS_DIR / f"{agent_name}.yaml"
        if not path.exists():
            log.warning("prompt_not_found", agent=agent_name)
            return {}
        with path.open() as fh:
            data = yaml.safe_load(fh) or {}
        self._cache[agent_name] = data
        return data

    def get_system_prompt(self, agent_name: str) -> str:
        return self.load(agent_name).get("system", "")


@functools.lru_cache(maxsize=1)
def _get_manager() -> PromptManager:
    return PromptManager()


def get_system_prompt(agent_name: str) -> str:
    return _get_manager().get_system_prompt(agent_name)
