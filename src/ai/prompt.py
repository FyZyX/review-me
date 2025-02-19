import pathlib
import typing

import jinja2

import code.model
import code.review.model

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
        return self._templates[prefix].get_template(name)

    def render_template(
        self,
        name: str,
        prefix: typing.Literal["system", "user", "persona"],
        **kwargs,
    ) -> str:
        template = self._load_template(f"{name}.md", prefix=prefix)
        overview = template.render(context=self._context, prefix=prefix, **kwargs)
        return overview
