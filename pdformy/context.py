"""Rendering context and theme shared by every block."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Literal

from fpdf import FPDF
from pydantic import BaseModel, ConfigDict

RGB = tuple[int, int, int]


class Theme(BaseModel):
    """Visual defaults. Every field can be overridden from the YAML `style:` key."""

    model_config = ConfigDict(extra="forbid")

    page_format: str = "A4"
    orientation: Literal["portrait", "landscape"] = "portrait"
    margin: float = 18  # mm

    # Core fonts (helvetica, times, courier) only cover latin-1. For full Unicode,
    # point `font_files` at TTFs: {regular: ..., bold: ..., italic: ..., bold_italic: ...}.
    font: str = "helvetica"
    font_files: dict[Literal["regular", "bold", "italic", "bold_italic"], Path] = {}
    font_size: float = 10  # pt
    title_size: float = 22  # report title
    heading_sizes: list[float] = [16, 13, 11.5, 10.5]  # by section level, last one repeats
    caption_size: float = 8.5

    text_color: RGB = (33, 33, 33)
    muted_color: RGB = (100, 99, 95)
    rule_color: RGB = (205, 204, 199)
    header_fill: RGB = (238, 237, 233)
    # Categorical chart hues in fixed order (dataviz reference palette, light mode).
    chart_colors: list[str] = [
        "#2a78d6", "#eb6834", "#1baf7a", "#eda100",
        "#e87ba4", "#008300", "#4a3aa7", "#e34948",
    ]

    spacing: float = 4  # mm between blocks
    numbered: bool = False  # prefix section titles with 1, 1.1, ...

    def heading_size(self, level: int) -> float:
        return self.heading_sizes[min(level, len(self.heading_sizes) - 1)]


@dataclass(frozen=True)
class RenderContext:
    pdf: FPDF
    theme: Theme
    base_dir: Path = Path(".")
    # Position of the current section in the tree, e.g. (2, 1) for "2.1".
    # Empty at the report root.
    number: tuple[int, ...] = field(default_factory=tuple)

    @property
    def level(self) -> int:
        """Outline level of the current section (0 for top-level sections)."""
        return max(len(self.number) - 1, 0)

    def child(self, index: int) -> RenderContext:
        return replace(self, number=(*self.number, index))

    def resolve(self, path: str | Path) -> Path:
        path = Path(path)
        return path if path.is_absolute() else self.base_dir / path

    def set_text(self, size: float | None = None, style: str = "", color: RGB | None = None) -> None:
        self.pdf.set_font(self.theme.font, style, size or self.theme.font_size)
        self.pdf.set_text_color(*(color or self.theme.text_color))

    def gap(self, mm: float | None = None) -> None:
        self.pdf.ln(self.theme.spacing if mm is None else mm)

    def ensure_space(self, height: float) -> None:
        """Start a new page unless `height` mm still fit on the current one."""
        if self.pdf.y + height > self.pdf.page_break_trigger:
            self.pdf.add_page()
