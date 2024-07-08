import asyncio
import code.model
import code.pull_request
import code.review.model

import ai.assistant
import ai.tool
import logger
from github.PullRequest import PullRequest


class App:
    def __init__(
            self,
            pull_request: PullRequest,
            context: code.model.PullRequestContextModel,
            assistant: ai.assistant.Assistant,
            debug: bool = False,
    ):
        self._pr = pull_request
        self._context = context
        self._assistant = assistant
        self._debug = debug

    async def _review_file(
            self,
            observations: list[code.review.model.ObservationModel],
            context: code.review.model.FileContextModel,
            delay: float,
    ) -> tuple[
        list[code.model.GitHubCommentModel],
        list[code.model.GitHubCommentModel],
    ]:
        if not context.patch.diff:
            return [], []

        # Stagger request start times to comply with rate limits
        logger.log.debug(f"Waiting {delay} seconds before reviewing")
        await asyncio.sleep(delay)

        prioritized_comments, remaining_comments = await self._assistant.review_file(
            observations=observations,
            context=context,
        )

        return prioritized_comments, remaining_comments

    async def _review_files(
            self,
            observations: list[code.review.model.ObservationModel],
            contexts: list[code.review.model.FileContextModel],
    ) -> tuple[
        list[code.model.GitHubCommentModel],
        list[code.model.GitHubCommentModel],
    ]:
        prioritized_comments, remaining_comments = [], []

        for prioritized, remaining in await asyncio.gather(*[
            asyncio.create_task(self._review_file(
                observations,
                context,
                delay=i * 5),
            )
            for i, context in enumerate(contexts)
        ]):
            for comment in prioritized:
                prioritized_comments.append(comment)
            for comment in remaining:
                remaining_comments.append(comment)

        return prioritized_comments, remaining_comments

    async def run(self):
        overview = await self._assistant.overview(self._context)
        status = overview.initial_assessment.status
        if status != code.review.model.Status.REVIEW_REQUIRED:
            code.pull_request.submit_review(
                pull_request=self._pr,
                body=overview.initial_assessment.summary,
            )
            return

        observations = overview.observations
        file_contexts = overview.file_contexts
        logger.log.debug(
            f"Files to review: \n"
            f"- {"\n- ".join([context.path for context in file_contexts])}"
        )

        prioritized_comments, remaining_comments = await self._review_files(
            observations=observations,
            contexts=file_contexts,
        )

        feedback = await self._assistant.get_feedback(
            prioritized_comments=prioritized_comments,
            remaining_comments=remaining_comments,
        )
        logger.log.info(f"Overall Feedback: {feedback.evaluation}")

        if self._debug:
            logger.log.debug("Running in debug, no review submitted")
            return

        code.pull_request.submit_review(
            pull_request=self._pr,
            body=f"{feedback.overall_comment}\n\n"
                 f"{feedback.justification}\n"
                 f"Final Evaluation: {feedback.evaluation}",
            comments=prioritized_comments,
        )
