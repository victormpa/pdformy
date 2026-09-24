from __future__ import annotations

from ..context import RenderContext
from .base import Block, register

# Keep a heading together with at least this much of what follows it.
KEEP_WITH_NEXT = 25  # mm


@register("title")
class Title(Block):
    """Section heading. Registers an outline entry, which also feeds the Summary (TOC)."""

    shorthand = "text"

    text: str
    # Outline level. Defaults to one below the enclosing section.
    level: int | None = None
    toc: bool = True

    def render(self, ctx: RenderContext) -> None:
        level = len(ctx.number) if self.level is None else self.level
        size = ctx.theme.heading_size(level)
        line_h = size * 0.5
        ctx.ensure_space(line_h + KEEP_WITH_NEXT)
        if self.toc:
            ctx.pdf.start_section(self.text, level=level)
        ctx.set_text(size, "B")
        ctx.pdf.multi_cell(0, line_h, self.text, new_x="LMARGIN", new_y="NEXT")
        ctx.gap(1.5)


@register("subtitle")
class Subtitle(Block):
    shorthand = "text"

    text: str

    def render(self, ctx: RenderContext) -> None:
        size = ctx.theme.font_size + 1.5
        ctx.set_text(size, "I", ctx.theme.muted_color)
        ctx.pdf.multi_cell(0, size * 0.5, self.text, new_x="LMARGIN", new_y="NEXT")
        ctx.gap(2)
