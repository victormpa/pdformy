from __future__ import annotations

from itertools import batched

from pydantic import model_validator

from ..context import RenderContext
from .base import AnyBlock, Block, register


@register("grid")
class Grid(Block):
    """Blocks laid out in columns, wrapping into rows. A row never splits across pages."""

    content: list[AnyBlock]
    # Either a column count (equal widths) or relative column widths.
    # Defaults to a single row holding every block.
    columns: int | None = None
    ratio: list[float] | None = None
    gap: float = 5  # mm between columns

    @model_validator(mode="after")
    def _columns_match(self) -> Grid:
        if self.columns is not None and self.ratio is not None and self.columns != len(self.ratio):
            raise ValueError(f"columns is {self.columns} but ratio has {len(self.ratio)} entries")
        if self.columns is not None and self.columns < 1:
            raise ValueError("columns must be at least 1")
        return self

    @property
    def widths(self) -> list[float]:
        return self.ratio or [1.0] * (self.columns or len(self.content))

    def render(self, ctx: RenderContext) -> None:
        pdf = ctx.pdf
        for row in batched(self.content, len(self.widths)):
            with pdf.offset_rendering() as dry_run:
                self._render_row(ctx, row)
            if dry_run.page_break_triggered:
                pdf.add_page()
            self._render_row(ctx, row)

    def _render_row(self, ctx: RenderContext, row: tuple[AnyBlock, ...]) -> None:
        pdf = ctx.pdf
        left, right, top = pdf.l_margin, pdf.r_margin, pdf.y
        weights = self.widths
        usable = pdf.epw - self.gap * (len(weights) - 1)
        bottom, x = top, left
        for block, weight in zip(row, weights):
            width = usable * weight / sum(weights)
            pdf.set_left_margin(x)
            pdf.set_right_margin(pdf.w - x - width)
            pdf.set_xy(x, top)
            block.render(ctx)
            bottom = max(bottom, pdf.y)
            x += width + self.gap
        pdf.set_left_margin(left)
        pdf.set_right_margin(right)
        pdf.set_xy(left, bottom)
