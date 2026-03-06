"""Settings models for app configuration persistence."""

from dataclasses import dataclass, field
from typing import Any

import yaml


@dataclass
class LLMProviderConfig:
    """Configuration for a single LLM provider."""

    api_key: str = ""
    model: str = ""
    base_url: str = ""

    @property
    def is_configured(self, provider_type: str = "") -> bool:
        """Return True when the minimum required fields are filled in."""
        return bool(self.model)


@dataclass
class LLMSettings:
    """All LLM provider configurations + which one is active."""

    active_provider: str = "openai"
    providers: dict[str, LLMProviderConfig] = field(default_factory=dict)

    @property
    def active_config(self) -> LLMProviderConfig | None:
        """Return the active provider config, or None if nothing is selected."""
        if not self.active_provider:
            return None
        return self.providers.get(self.active_provider)

    @property
    def is_configured(self) -> bool:
        """Return True when an active provider is fully configured."""
        config = self.active_config
        if config is None:
            return False
        if self.active_provider == "ollama":
            return bool(config.model)
        if self.active_provider == "openai_compat":
            return bool(config.model and config.base_url)
        return bool(config.api_key and config.model)


@dataclass
class AgentSettings:
    """Agent-related settings."""

    executor_type: str = "lighthouse"
    llm: LLMSettings = field(default_factory=LLMSettings)


@dataclass
class Settings:
    """Unified settings object combining all setting categories."""

    agent: AgentSettings = field(default_factory=AgentSettings)
    welcome_completed: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert settings to a dictionary for serialization."""
        llm = self.agent.llm
        providers_dict = {
            ptype: {"api_key": cfg.api_key, "model": cfg.model, "base_url": cfg.base_url}
            for ptype, cfg in llm.providers.items()
        }
        return {
            "agent": {
                "executor_type": self.agent.executor_type,
                "llm": {
                    "active_provider": llm.active_provider,
                    "providers": providers_dict,
                },
            },
            "welcome_completed": self.welcome_completed,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Settings":
        """Create Settings from a dictionary."""
        agent_data = data.get("agent", {})
        llm_data = agent_data.get("llm", {})
        providers_raw = llm_data.get("providers", {})

        providers = {
            ptype: LLMProviderConfig(
                api_key=cfg.get("api_key", ""),
                model=cfg.get("model", ""),
                base_url=cfg.get("base_url", ""),
            )
            for ptype, cfg in providers_raw.items()
            if isinstance(cfg, dict)
        }

        return cls(
            agent=AgentSettings(
                executor_type=agent_data.get("executor_type", "lighthouse"),
                llm=LLMSettings(
                    active_provider=llm_data.get("active_provider", ""),
                    providers=providers,
                ),
            ),
            welcome_completed=data.get("welcome_completed", False),
        )

    def to_yaml(self) -> str:
        """Serialize settings to YAML string."""
        return yaml.dump(self.to_dict(), default_flow_style=False, sort_keys=False)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "Settings":
        """Deserialize settings from YAML string."""
        data = yaml.safe_load(yaml_str) or {}
        return cls.from_dict(data)
