import pathlib
import typing

import jinja2

import code.model
import code.review.model

class PromptError(Exception):
    """Custom exception for prompt-related errors."""
    pass

PROMPT_DIR = pathlib.Path(__file__).parent / "prompts"


class Builder:
    def __init__(self, context: code.model.PullRequestContextModel):
        self._context = context
        self._templates = {
            "system": jinja2.Environment(
                loader=jinja2.FileSystemLoader(PROMPT_DIR / "system"),
            ),
            "user": jinja2.Environment(
                loader=jinja2.FileSystemLoader(PROMPT_DIR / "user"),
            ),
            "persona": jinja2.Environment(
                loader=jinja2.FileSystemLoader(PROMPT_DIR / "persona"),
            ),
        }

    def _load_template(
        self,
        name: str,
        prefix: typing.Literal["system", "user", "persona"],
    ) -> jinja2.Template:
        try:
            return self._templates[prefix].get_template(name)
        except jinja2.TemplateNotFound:
            raise PromptError(f"Template not found: {prefix}/{name}")
        except jinja2.TemplateError as e:
            raise PromptError(f"Error loading template {prefix}/{name}: {str(e)}")

    def render_template(
        self,
        name: str,
        prefix: typing.Literal["system", "user", "persona"],
        **kwargs,
    ) -> str:
        try:
            template = self._load_template(f"{name}.md", prefix=prefix)
            overview = template.render(context=self._context, prefix=prefix, **kwargs)
            return overview
        except PromptError as e:
            raise e
        except jinja2.TemplateError as e:
            raise PromptError(f"Error rendering template {prefix}/{name}.md: {str(e)}")
        except Exception as e:
            raise PromptError(f"Unexpected error rendering template {prefix}/{name}.md: {str(e)}")
