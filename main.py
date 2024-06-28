import json
import os

import anthropic
import openai
from github import Github

openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_overall_comment():
    system_prompt = (
        "Your job is to review GitHub Pull Requests. "
        "You must act as an expert software engineer. "
        "You will be given a diff of the changes from the PR, "
        "and you must review the code changes in order to "
        "provide feedback as needed."
    )
    # TODO: Implement
    pass


def anthropic_chat_completion(system_prompt, prompt,
                              model="claude-3-5-sonnet-20240620"):
    client = anthropic.Anthropic()

    message = client.messages.create(
        model=model,
        max_tokens=1000,
        temperature=0,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    }
                ]
            }
        ]
    )
    return message.content


def openai_chat_completion(system_prompt, prompt, model):
    response = openai.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1_000,
    )
    return response.choices[0].message.content.strip()


def generate_file_comments(pr, model, debug=False):
    system_prompt = (
        "Your job is to review a single file diff from a GitHub Pull Request. "
        "You must act as an expert software engineer. "
        "You will be given the PR title and description, as well as a diff of the "
        "changes from the a single file in the PR."
        "You must review the code changes and provide meaningful feedback when "
        "necessary. You are *NOT* reviewing the entire PR, just this single file. "
        "Keep your comment as CONCISE as possible and clear. "
        "Only provide feedback if there is something CONCRETE and SPECIFIC to say. "
        "If it's okay as is, simply reply with the exact phrase 'LGTM.'"
    )
    commit_msgs = [commit.commit.message for commit in pr.get_commits()]

    file_comments = {}
    for file in pr.get_files():
        if file.status != "modified":
            continue
        prompt = (
            f"PR Title: {pr.title}\n\n"
            f"PR Commits: - {"\n- ".join(commit_msgs)}\n\n"
            f"PR Body:\n{pr.body}\n\n"
            f"Filename: {file.filename}\n\n"
            f"Diff:\n{file.patch}"
        )
        if debug:
            continue
        comment = openai_chat_completion(system_prompt, prompt, model)
        file_comments[file.filename] = comment
    return file_comments


def get_pr(github_token, repo, pr_number):
    gh = Github(github_token)
    repo = gh.get_repo(repo)
    pr = repo.get_pull(pr_number)
    return pr


def main():
    github_token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    event_path = os.environ.get("GITHUB_EVENT_PATH")

    with open(event_path, 'r') as f:
        event = json.load(f)

    pr_number = event["issue"]["number"]

    pr = get_pr(github_token, repo, pr_number)

    review_comments = generate_file_comments(pr, "gpt-4o")

    for comment in review_comments.values():
        pr.create_issue_comment(comment)


def test():
    github_token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    pr = get_pr(github_token, repo, 2)
    review_comments = generate_file_comments(pr, "gpt-3.5-turbo", debug=True)
    for filename, comment in review_comments.items():
        print(filename)
        print("--------")
        print(comment)
        print("========")
        print()


if __name__ == "__main__":
    test()
