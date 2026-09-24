from __future__ import annotations

import datetime as dt
from typing import Any, Literal

from fpdf.fonts import FontFace
from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from ..context import RenderContext
from .base import Block, register
from .image import render_caption

ColumnType = Literal["string", "int", "float", "percent", "date"]

DEFAULT_FORMATS: dict[ColumnType, str] = {"int": "d", "float": ".2f", "percent": ".1f", "date": "%Y-%m-%d"}


class Column(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    type: ColumnType = "string"
    align: Literal["left", "center", "right"] | None = None
    # Relative width; columns without one share the default weight of 1.
    width: float | None = None
    # Python format spec (`.3f`, `,d`) or strftime pattern for dates.
    format: str | None = None

    @property
    def text_align(self) -> str:
        align = self.align or ("right" if self.type in ("int", "float", "percent") else "left")
        return align.upper()

    def format_value(self, value: Any) -> str:
        if value is None or value == "":
            return ""
        spec = self.format or DEFAULT_FORMATS.get(self.type)
        match self.type:
            case "int":
                return format(int(value), spec)
            case "float":
                return format(float(value), spec)
            case "percent":
                return format(float(value), spec) + "%"
            case "date" if isinstance(value, (dt.date, dt.datetime)):
                return value.strftime(spec)
        return str(value)


@register("table")
class Table(Block):
    header: list[Column]
    rows: list[list[Any]]
    caption: str | None = None

    @field_validator("header", mode="before")
    @classmethod
    def _names_as_columns(cls, header: Any) -> Any:
        if isinstance(header, list):
            return [{"name": col} if isinstance(col, str) else col for col in header]
        return header

    @model_validator(mode="after")
    def _row_lengths(self) -> Table:
        for i, row in enumerate(self.rows):
            if len(row) != len(self.header):
                raise ValueError(f"rows[{i}] has {len(row)} cells, header has {len(self.header)}")
        return self

    def render(self, ctx: RenderContext) -> None:
        theme = ctx.theme
        ctx.set_text()
        pdf = ctx.pdf
        with pdf.table(
            width=pdf.epw,
            align="LEFT",  # CENTER would center on the page, ignoring grid cells
            col_widths=tuple(col.width or 1 for col in self.header),
            text_align=tuple(col.text_align for col in self.header),
            headings_style=FontFace(emphasis="BOLD", fill_color=theme.header_fill),
            line_height=theme.font_size * 0.5,
            padding=(1, 1.5),
        ) as table:
            table.row([col.name for col in self.header])
            for row in self.rows:
                table.row([col.format_value(value) for col, value in zip(self.header, row)])
        render_caption(ctx, self.caption, pdf.l_margin, pdf.epw)
        ctx.gap()
