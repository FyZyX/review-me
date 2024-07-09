import dataclasses
import json
import os
import sys

import logger


@dataclasses.dataclass
class GitHubConfig:
    token: str
    repository: str
    pr_number: int


@dataclasses.dataclass
class LlmConfig:
    strategy: str
    model: str
    persona: str


@dataclasses.dataclass
class AppConfig:
    github: GitHubConfig
    llm: LlmConfig
    debug: bool = False


def from_env() -> AppConfig:
    try:
        debug = bool(os.environ.get("DEBUG", False))

        github_token = os.environ.get("GITHUB_TOKEN")
        if not github_token:
            raise ValueError("GITHUB_TOKEN environment variable is not set")

        repository = os.environ.get("GITHUB_REPOSITORY")
        if not repository:
            raise ValueError("GITHUB_REPOSITORY environment variable is not set")

        event_path = os.environ.get("GITHUB_EVENT_PATH")
        if not event_path:
            raise ValueError("GITHUB_EVENT_PATH environment variable is not set")

        strategy = os.environ.get("LLM_STRATEGY", "anthropic")
        model = os.environ.get("MODEL", "claude-3-5-sonnet-20240620")
        persona = os.environ.get("PERSONA", "pirate")

        try:
            with open(event_path, "r") as f:
                event = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse GitHub event JSON: {e}")

        try:
            pr_number = event["issue"]["number"]
        except KeyError:
            raise ValueError("Failed to extract PR number from GitHub event")

        config = AppConfig(
            github=GitHubConfig(
                token=github_token,
                repository=repository,
                pr_number=pr_number,
            ),
            llm=LlmConfig(
                strategy=strategy,
                model=model,
                persona=persona,
            ),
            debug=debug,
        )

        return config
    except Exception as e:
        logger.log.critical(f"Failed to load environment: {e}")
        raise
