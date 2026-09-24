from __future__ import annotations

import io
from typing import Literal

import matplotlib
from matplotlib.figure import Figure
from pydantic import BaseModel, ConfigDict, model_validator

from ..context import RenderContext
from .base import Block, register
from .image import Align, aligned_x, parse_width, render_caption

MM_PER_INCH = 25.4


class Point(BaseModel):
    model_config = ConfigDict(extra="forbid")

    x: str | float
    y: float


class Series(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    data: list[Point]


@register("chart")
class Chart(Block):
    """Bar, line, pie or scatter chart drawn with matplotlib and embedded as vector SVG."""

    type: Literal["bar", "line", "pie", "scatter"]
    # Either a single series as `data`, or several named `series`.
    data: list[Point] | None = None
    series: list[Series] | None = None
    title: str | None = None
    x_label: str | None = None
    y_label: str | None = None
    caption: str | None = None
    width: str | float = "100%"
    aspect: float = 0.5  # height / width
    align: Align = "center"

    @model_validator(mode="after")
    def _one_source(self) -> Chart:
        if (self.data is None) == (self.series is None):
            raise ValueError("chart needs exactly one of `data` or `series`")
        if self.type == "pie" and len(self.all_series) > 1:
            raise ValueError("a pie chart takes a single series")
        return self

    @property
    def all_series(self) -> list[Series]:
        return self.series if self.series is not None else [Series(name="", data=self.data or [])]

    def figure(self, width_mm: float, theme) -> Figure:
        text = "#%02x%02x%02x" % theme.text_color
        muted = "#%02x%02x%02x" % theme.muted_color
        rule = "#%02x%02x%02x" % theme.rule_color
        colors = theme.chart_colors
        rc = {
            "font.size": 7.5,
            "text.color": text,
            "axes.labelcolor": muted,
            "axes.edgecolor": rule,
            "xtick.color": muted,
            "ytick.color": muted,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "svg.fonttype": "path",
        }
        with matplotlib.rc_context(rc):
            fig = Figure(figsize=(width_mm / MM_PER_INCH, width_mm * self.aspect / MM_PER_INCH))
            ax = fig.add_subplot()
            series = self.all_series
            if self.type == "pie":
                points = series[0].data
                ax.pie(
                    [p.y for p in points],
                    labels=[str(p.x) for p in points],
                    colors=colors[: len(points)],
                    wedgeprops={"edgecolor": "white", "linewidth": 1.5},
                    autopct="%1.0f%%",
                )
                ax.set_aspect("equal")
            else:
                ax.grid(axis="y", color=rule, linewidth=0.5)
                ax.set_axisbelow(True)
                for i, s in enumerate(series):
                    xs, ys = [p.x for p in s.data], [p.y for p in s.data]
                    color = colors[i % len(colors)]
                    label = s.name or None
                    match self.type:
                        case "bar":
                            n = len(series)
                            bar_w = 0.8 / n
                            positions = [j - 0.4 + bar_w * (i + 0.5) for j in range(len(xs))]
                            ax.bar(positions, ys, bar_w * 0.92, color=color, label=label)
                            ax.set_xticks(range(len(xs)), [str(x) for x in xs])
                        case "line":
                            ax.plot(xs, ys, color=color, linewidth=1.5, marker="o", markersize=3, label=label)
                        case "scatter":
                            ax.scatter(xs, ys, color=color, s=14, label=label, edgecolors="white", linewidths=0.6)
                if len(series) > 1:
                    # Above the plot area, so it never covers data.
                    ax.legend(loc="lower right", bbox_to_anchor=(1, 1), ncols=len(series), frameon=False)
                if self.x_label:
                    ax.set_xlabel(self.x_label)
                if self.y_label:
                    ax.set_ylabel(self.y_label)
            if self.title:
                ax.set_title(self.title, loc="left", fontweight="bold")
            fig.tight_layout()
        return fig

    def render(self, ctx: RenderContext) -> None:
        width = parse_width(self.width, ctx.pdf.epw)
        svg = io.BytesIO()
        # No metadata: fpdf2 doesn't support the <metadata> tag and warns about it.
        self.figure(width, ctx.theme).savefig(svg, format="svg", metadata={"Date": None, "Creator": None, "Format": None, "Type": None})
        svg.seek(0)
        x = aligned_x(ctx, width, self.align)
        ctx.pdf.image(svg, x=x, w=width)
        render_caption(ctx, self.caption, x, width)
        ctx.gap()
