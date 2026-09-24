from __future__ import annotations

from typing import Literal

from pydantic import ValidationInfo, field_validator

from ..context import RenderContext
from .base import Block, register

Align = Literal["left", "center", "right"]


def parse_width(value: str | float, available: float) -> float:
    """`"50%"` is relative to the available width, a number is in mm."""
    if isinstance(value, str) and value.endswith("%"):
        return available * float(value[:-1]) / 100
    return min(float(value), available)


def aligned_x(ctx: RenderContext, width: float, align: Align) -> float:
    pdf = ctx.pdf
    offset = {"left": 0, "center": (pdf.epw - width) / 2, "right": pdf.epw - width}[align]
    return pdf.l_margin + offset


def render_caption(ctx: RenderContext, caption: str | None, x: float, width: float) -> None:
    if caption:
        ctx.pdf.ln(1.5)
        ctx.set_text(ctx.theme.caption_size, "I", ctx.theme.muted_color)
        ctx.pdf.set_x(x)
        ctx.pdf.multi_cell(width, ctx.theme.caption_size * 0.45, caption, align="C", new_x="LMARGIN", new_y="NEXT")


@register("image")
class Image(Block):
    shorthand = "source"

    source: str
    caption: str | None = None
    width: str | float = "100%"
    align: Align = "center"

    @field_validator("source")
    @classmethod
    def _exists(cls, source: str, info: ValidationInfo) -> str:
        base_dir = (info.context or {}).get("base_dir")
        if base_dir is not None and not (base_dir / source).is_file():
            raise ValueError(f"image file not found: {base_dir / source}")
        return source

    def render(self, ctx: RenderContext) -> None:
        path = ctx.resolve(self.source)
        if not path.is_file():
            raise FileNotFoundError(f"image file not found: {path}")
        width = parse_width(self.width, ctx.pdf.epw)
        x = aligned_x(ctx, width, self.align)
        ctx.pdf.image(path, x=x, w=width)
        render_caption(ctx, self.caption, x, width)
        ctx.gap()
