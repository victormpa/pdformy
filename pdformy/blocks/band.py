"""Page header and footer bands (pinned to the top or bottom of each page)."""

from __future__ import annotations

import re
from typing import Any, Literal

import mistletoe
from pydantic import BaseModel, ConfigDict, field_validator

from ..context import RenderContext
from .base import AnyBlock, Block
from .text import Text

_VAR = re.compile(r"\{\{(\w+)\}\}")
_SLOT_ALIGN = {"start": "left", "center": "center", "end": "right"}
_GAP = 2  # mm between the three columns
_RULE_PAD = 1.5  # mm of space around the hairline


class PageBand(BaseModel):
    """A three-column band drawn on every page (after `skip` pages)."""

    model_config = ConfigDict(extra="forbid")

    skip: int = 0
    start: AnyBlock | None = None
    center: AnyBlock | None = None
    end: AnyBlock | None = None

    @field_validator("skip")
    @classmethod
    def _skip_non_negative(cls, value: int) -> int:
        if value < 0:
            raise ValueError("skip must be >= 0")
        return value

    def visible_on(self, page: int) -> bool:
        return page > self.skip

    @property
    def slots(self) -> list[tuple[Literal["start", "center", "end"], Block | None]]:
        return [
            ("start", self.start),
            ("center", self.center),
            ("end", self.end),
        ]


def interpolate(text: str, variables: dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        if name not in variables:
            raise ValueError(f"unknown header/footer variable: {{{{{name}}}}}")
        return variables[name]

    return _VAR.sub(replace, text)


def interpolate_block(block: Block, variables: dict[str, str]) -> Block:
    """Replace `{{name}}` in string fields without re-validating (e.g. image paths)."""
    updates: dict[str, Any] = {}
    for name in type(block).model_fields:
        value = getattr(block, name)
        if isinstance(value, str):
            updates[name] = interpolate(value, variables)
        elif isinstance(value, Block):
            updates[name] = interpolate_block(value, variables)
        elif isinstance(value, list):
            updates[name] = [
                interpolate_block(item, variables)
                if isinstance(item, Block)
                else interpolate(item, variables)
                if isinstance(item, str)
                else item
                for item in value
            ]
    return block.model_copy(update=updates)


def interpolate_band(band: PageBand, variables: dict[str, str]) -> PageBand:
    return band.model_copy(
        update={
            position: interpolate_block(block, variables) if block is not None else None
            for position, block in band.slots
        }
    )


def measure_band(band: PageBand, ctx: RenderContext, variables: dict[str, str]) -> float:
    """Height of the band including the hairline, without leaving ink on the page."""
    pdf = ctx.pdf
    top = pdf.y
    auto, margin = pdf.auto_page_break, pdf.b_margin
    pdf.set_auto_page_break(False)
    try:
        with pdf.offset_rendering():
            _render_row(interpolate_band(band, variables), ctx)
            content = pdf.y - top
    finally:
        pdf.set_auto_page_break(auto, margin)
    height = content + 2 * _RULE_PAD
    if height > pdf.eph / 3:
        raise ValueError("header/footer band is taller than one third of the page")
    return height


def draw_header(band: PageBand, ctx: RenderContext, variables: dict[str, str]) -> None:
    """Draw the band at the current y and leave the cursor below the hairline."""
    pdf = ctx.pdf
    auto, margin = pdf.auto_page_break, pdf.b_margin
    pdf.set_auto_page_break(False)
    try:
        _render_row(interpolate_band(band, variables), ctx)
        pdf.ln(_RULE_PAD)
        _hairline(ctx)
        pdf.ln(_RULE_PAD)
    finally:
        pdf.set_auto_page_break(auto, margin)


def draw_footer(band: PageBand, ctx: RenderContext, variables: dict[str, str], height: float) -> None:
    """Draw the band in the reserved bottom margin."""
    pdf = ctx.pdf
    auto, margin = pdf.auto_page_break, pdf.b_margin
    pdf.set_auto_page_break(False)
    try:
        pdf.set_y(pdf.h - height)
        _hairline(ctx)
        pdf.ln(_RULE_PAD)
        _render_row(interpolate_band(band, variables), ctx)
    finally:
        pdf.set_auto_page_break(auto, margin)


def _hairline(ctx: RenderContext) -> None:
    pdf = ctx.pdf
    pdf.set_draw_color(*ctx.theme.rule_color)
    pdf.set_line_width(0.2)
    y = pdf.y
    pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)


def _render_row(band: PageBand, ctx: RenderContext) -> None:
    pdf = ctx.pdf
    left, right, top = pdf.l_margin, pdf.r_margin, pdf.y
    usable = pdf.epw - _GAP * 2
    width = usable / 3
    bottom, x = top, left
    for position, block in band.slots:
        pdf.set_left_margin(x)
        pdf.set_right_margin(pdf.w - x - width)
        pdf.set_xy(x, top)
        if block is not None:
            _render_slot(ctx, block, position)
        bottom = max(bottom, pdf.y)
        x += width + _GAP
    pdf.set_left_margin(left)
    pdf.set_right_margin(right)
    pdf.set_xy(left, bottom)


def _render_slot(
    ctx: RenderContext,
    block: Block,
    position: Literal["start", "center", "end"],
) -> None:
    if isinstance(block, Text):
        ctx.set_text(ctx.theme.caption_size, "", ctx.theme.muted_color)
        html = mistletoe.markdown(block.markdown)
        align = _SLOT_ALIGN[position]
        if align != "left":
            html = html.replace("<p>", f'<p align="{align}">')
        ctx.pdf.write_html(
            html,
            font_family=ctx.theme.font,
            li_prefix_color=ctx.theme.muted_color,
        )
        return
    block.render(ctx)
