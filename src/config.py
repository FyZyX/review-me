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

        github_token = os.environ["GITHUB_TOKEN"]
        repository = os.environ["GITHUB_REPOSITORY"]
        event_path = os.environ["GITHUB_EVENT_PATH"]

        strategy = os.environ.get("LLM_STRATEGY", "anthropic")
        model = os.environ.get("MODEL", "claude-3-5-sonnet-20240620")
        persona = os.environ.get("PERSONA", "default")

        with open(event_path, "r") as f:
            event = json.load(f)

        pr_number = event["pull_request"]["number"]

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
        sys.exit(42)
