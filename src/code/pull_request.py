import sys
from typing import Optional

import github
from github.PullRequest import PullRequest

import config
import logger
from . import model
from .diff import parse_diff


def get_pr(cfg: config.GitHubConfig) -> Optional[PullRequest]:
    try:
        gh = github.Github(cfg.token)
        repo = gh.get_repo(cfg.repository)
        pr = repo.get_pull(cfg.pr_number)
        logger.log.info(f"PR retrieved: #{pr.number}")
        return pr
    except github.GithubException as e:
        logger.log.critical(f"Github API error while retrieving PR: {e}")
        raise
    except Exception as e:
        logger.log.critical(f"Unexpected error while retrieving PR: {e}")
        raise


def build_pr_context(pull_request: PullRequest) -> Optional[model.PullRequestContextModel]:
    try:
        files = pull_request.get_files()
        context = model.PullRequestContextModel(
            title=pull_request.title,
            description=pull_request.body or "",
            commit_messages=[
                commit.commit.message for commit in pull_request.get_commits()
            ],
            review_comments=[
                comment.body for comment in pull_request.get_review_comments()
            ],
            issue_comments=[comment.body for comment in pull_request.get_issue_comments()],
            patches={
                file.filename: model.FilePatchModel(
                    filename=file.filename,
                    diff=file.patch or "",
                    hunks=[] if not file.patch else parse_diff(file.patch),
                )
                for file in files
            },
            added_files=[file.filename for file in files if file.status == "added"],
            modified_files=[file.filename for file in files if file.status == "modified"],
            deleted_files=[file.filename for file in files if file.status == "removed"],
        )
        logger.log.info(f"PR Context built successfully: {context.title}")
        return context
    except github.GithubException as e:
        logger.log.critical(f"GitHub API error while building PR context: {e}")
        return None
    except Exception as e:
        logger.log.critical(f"Unexpected error while building PR context: {e}")
        return None


def post_comment(pull_request: PullRequest, message: str) -> bool:
    try:
        comment = pull_request.create_issue_comment(message)
        logger.log.info(f"Comment posted successfully: {comment.id}")
        return True
    except github.GithubException as e:
        logger.log.error(f"GitHub API error while posting comment: {e}")
        return False
    except Exception as e:
        logger.log.error(f"Unexpected error while posting comment: {e}")
        return False


def submit_review(
    pull_request: PullRequest,
    body: str,
    comments: list[model.GitHubCommentModel] | None = None,
):
    try:
        comments = [comment.model_dump(exclude_none=True) for comment in comments or []]
        logger.log.debug(f"Submitting review: {comments}")
        review = pull_request.create_review(
            body=body,
            comments=comments,
            event="COMMENT",
        )
        logger.log.info(f"Review submitted successfully: {review.id}")
        return True
    except github.GithubException as e:
        logger.log.error(f"GitHub API error while submitting review: {e}")
        return False
    except Exception as e:
        logger.log.error(f"Unexpected error while submitting review: {e}")
        return False
