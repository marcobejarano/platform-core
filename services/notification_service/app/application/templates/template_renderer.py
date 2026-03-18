from pathlib import Path

from jinja2 import Environment, FileSystemLoader


class TemplateRenderer:
    def __init__(self) -> None:
        template_path = Path(__file__).parent

        self.env = Environment(
            loader=FileSystemLoader(template_path),
            autoescape=False,
        )

    def render(self, template_name: str, **context) -> str:
        template = self.env.get_template(template_name)
        return template.render(**context)
