import sys

import github
from github.PullRequest import PullRequest

import config
import logger
from . import model
from .diff import parse_diff


def get_pr(cfg: config.GitHubConfig):
    try:
        gh = github.Github(cfg.token)
        repo = gh.get_repo(cfg.repository)
        pr = repo.get_pull(cfg.pr_number)
        return pr
    except Exception as e:
        logger.log.critical(f"Couldn't retrieve pull request: {e}")
        sys.exit(69)


def build_pr_context(pull_request: PullRequest) -> model.PullRequestContextModel:
    files = pull_request.get_files()
    context = model.PullRequestContextModel(
        title=pull_request.title,
        description=pull_request.body,
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
    return context


def post_comment(pull_request: PullRequest, message: str):
    try:
        pull_request.create_issue_comment(message)
    except github.GithubException as e:
        logger.log.warning(f"Could not post comment to GitHub: {e}")
    except Exception as e:
        logger.log.warning(f"Unknown problem posting comment: {e}")


def submit_review(
    pull_request: PullRequest,
    body: str,
    comments: list[model.GitHubCommentModel] | None = None,
):
    comments = [comment.model_dump(exclude_none=True) for comment in comments or []]
    logger.log.debug(f"Submitting review: {comments}")
    pull_request.create_review(
        body=body,
        comments=comments,
        event="COMMENT",
    )
