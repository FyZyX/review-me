review_files = {
    "name": "review_files",
    "description": "Review a list of files more carefully. "
                   "It should be used whenever the user needs a PR review.",
    "input_schema": {
        "type": "object",
        "properties": {
            "files": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Name of the file to review"
                        },
                        "reason": {
                            "type": "string",
                            "description": "The reason or rationale for the review"
                        }
                    },
                    "required": ["filename", "reason"]
                }
            }
        },
        "required": ["files"]
    }
}

post_feedback = {
    "name": "post_feedback",
    "description": "Create GitHub pull request review comments from the provided "
                   "feedback. This tool should be used to post detailed, "
                   "line-specific comments on code changes. Each feedback item "
                   "should correspond to a specific location in the code, identified "
                   "by line number. Each line number MUST belong to a hunk in the "
                   "file diff. Use this for constructive feedback, suggestions "
                   "for improvement, or highlighting potential issues in the code. "
                   "Ensure comments are clear, specific, and actionable.",
    "input_schema": {
        "type": "object",
        "properties": {
            "feedback": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "The original file path"
                        },
                        "start_line": {
                            "type": "integer",
                            "description": "Start line for multi-line comments "
                                           "(inclusive). "
                                           "MUST be *less than* `end_line`. "
                                           "The start line MUST be in the "
                                           "same hunk as the end line."
                        },
                        "end_line": {
                            "type": "integer",
                            "description": "The end line in multi-line comments "
                                           "(inclusive). "
                                           "MUST be *greater than* `start_line`."
                        },
                        "start_side": {
                            "type": "string",
                            "enum": ["LEFT", "RIGHT"],
                            "description": "Side for the start line in multi-line "
                                           "comments"
                        },
                        "end_side": {
                            "type": "string",
                            "enum": ["LEFT", "RIGHT"],
                            "description": "LEFT for original code, "
                                           "RIGHT for modified code"
                        },
                        "body": {
                            "type": "string",
                            "description": "The actual feedback or comment on this "
                                           "section of code"
                        },
                    },
                    "required": ["path", "start_line", "end_line", "body"]
                }
            }
        },
        "required": ["feedback"]
    }
}

submit_review = {
    "name": "submit_review",
    "description": "Provide a final evaluation for the GitHub pull request. "
                   "This tool should be used after generating individual comments to "
                   "create an overall summary and determine the final review action "
                   "(approve, comment, or request changes).",
    "input_schema": {
        "type": "object",
        "properties": {
            "feedback": {
                "type": "string",
                "description": "Final thoughts and overall feedback on the Pull Request"
            },
            "event": {
                "type": "string",
                "enum": ["APPROVE", "COMMENT", "REQUEST_CHANGES"],
                "description": "The final review action to take"
            },
        },
        "required": ["feedback", "event"]
    }
}