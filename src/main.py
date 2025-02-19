import asyncio
import sys
import traceback

import ai.assistant
import ai.prompt
import code.pull_request
import config
import logger
from app import App


async def run_app(cfg, pr):
    context = await code.pull_request.build_pr_context(pr)
    logger.log.debug(f"Context built successfully: {context.title}")
    builder = ai.prompt.Builder(context)
    assistant = ai.assistant.Assistant(cfg.llm, builder)

    app = App(pr, context, assistant, debug=cfg.debug)
    await app.run()


def main():
    cfg = config.from_env()
    pr = code.pull_request.get_pr(cfg.github)
    logger.log.debug(f"Pull request retrieved: #{pr.number}")

    try:
        asyncio.run(run_app(cfg, pr))
    except Exception as e:
        logger.log.error(f"Problem during run: {e}")
        code.pull_request.post_comment(
            pr,
            f"Sorry, couldn't review your code because\n"
            f"```{traceback.format_exc()}```",
        )
        sys.exit(42)


if __name__ == "__main__":
    main()
