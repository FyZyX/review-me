import asyncio
import sys
import traceback
import github.GithubException

from ai.anthropic import AnthropicError
import ai.assistant
from ai.prompt import PromptError
from ai.tool import ToolError
from code.model import InvalidSeverityError
import code.pull_request
import config
import logger
from app import App


def main():
    try:
        cfg = config.from_env()
        pr = code.pull_request.get_pr(cfg.github)
        context = code.pull_request.build_pr_context(pr)
        builder = ai.prompt.Builder(context)
        assistant = ai.assistant.Assistant(cfg.llm, builder)
        app = App(pr, context, assistant, debug=cfg.debug)
        asyncio.run(app.run())
    except github.GithubException as e:
        logger.log.critical(f"Exit with GithubException: {e}")
        sys.exit(69)
    except InvalidSeverityError as e:
        logger.log.error(f"Exit with InvalidSeverityError: {e}")
        sys.exit(255)
    except ToolError as e:
        logger.log.error(f"Exit with ToolError: {e}")
        sys.exit(7)
    except AnthropicError as e:
        logger.log.errror(f"Exit with AnthropicError: {e}")
        sys.exit(8)
    except PromptError as e:
        logger.log.error(f"Exit with PromptError: {e}")
        sys.exit(135)
    except ValueError as e:
        logger.log.error(f"Exit with ValueError: {e}")
        sys.exit(123)
    except Exception as e:
        logger.log.critical(f"Exit with Unexpected Exception: {e}")
        if 'pr' in locals():
            code.pull_request.post_comment(
                pr,
                f"Sorry, I couldn't review your code because:\n"
                f"```{traceback.format_exc()}```",
            )
        sys.exit(42)


if __name__ == "__main__":
    main()
