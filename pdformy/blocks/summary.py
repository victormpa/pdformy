from __future__ import annotations

from fpdf import FPDF
from fpdf.fonts import TextStyle
from fpdf.outline import OutlineSection, TableOfContents
from pydantic import BaseModel, ConfigDict

from ..context import RenderContext


class Summary(BaseModel):
    """Table of contents, filled in with page numbers once the whole report is laid out."""

    model_config = ConfigDict(extra="forbid")

    title: str = "Contents"
    depth: int = 2  # number of section levels listed

    def render(self, ctx: RenderContext) -> None:
        ctx.set_text(ctx.theme.heading_size(0), "B")
        ctx.pdf.multi_cell(0, ctx.theme.heading_size(0) * 0.5, self.title, new_x="LMARGIN", new_y="NEXT")
        ctx.gap(3)
        ctx.pdf.insert_toc_placeholder(_DepthTOC(ctx, self.depth).render_toc, allow_extra_pages=True)


class _DepthTOC(TableOfContents):
    def __init__(self, ctx: RenderContext, depth: int) -> None:
        theme = ctx.theme
        super().__init__(level_indent=6, line_spacing=1.6)
        self.depth = depth
        self.styles = [
            TextStyle(font_family=theme.font, font_style="B" if level == 0 else "",
                      font_size_pt=theme.font_size, color=theme.text_color)
            for level in range(depth)
        ]

    def get_text_style(self, pdf: FPDF, item: OutlineSection) -> TextStyle:
        return self.styles[item.level]

    def render_toc(self, pdf: FPDF, outline: list[OutlineSection]) -> None:
        super().render_toc(pdf, [s for s in outline if s.level < self.depth])
