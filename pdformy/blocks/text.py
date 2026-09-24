from __future__ import annotations

import mistletoe

from ..context import RenderContext
from .base import Block, register


@register("text")
class Text(Block):
    """Markdown text (bold, italic, code, links, lists, headings)."""

    shorthand = "markdown"

    markdown: str

    def render(self, ctx: RenderContext) -> None:
        ctx.set_text()
        ctx.pdf.write_html(
            mistletoe.markdown(self.markdown),
            font_family=ctx.theme.font,
            li_prefix_color=ctx.theme.text_color,
        )
        ctx.gap()
