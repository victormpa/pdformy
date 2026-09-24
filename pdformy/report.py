from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from fpdf import FPDF
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .blocks.section import Section
from .blocks.summary import Summary
from .context import RenderContext, Theme


class ReportPDF(FPDF):
    def __init__(self, theme: Theme) -> None:
        super().__init__(orientation=theme.orientation, format=theme.page_format)
        self.theme = theme
        self.set_margins(theme.margin, theme.margin)
        self.set_auto_page_break(True, margin=theme.margin)
        for style, path in theme.font_files.items():
            fpdf_style = {"regular": "", "bold": "B", "italic": "I", "bold_italic": "BI"}[style]
            self.add_font(theme.font, fpdf_style, str(path))

    def footer(self) -> None:
        self.set_y(-self.theme.margin / 1.6)
        self.set_font(self.theme.font, "", self.theme.caption_size)
        self.set_text_color(*self.theme.muted_color)
        self.cell(0, 4, self.get_page_label() or str(self.page_no()), align="C")


class Report(BaseModel):
    """Root of a report. Build it from YAML with `Report.from_yaml` or directly in Python."""

    model_config = ConfigDict(extra="forbid")

    title: str
    subtitle: str | None = None
    author: str | None = None
    summary: Summary | None = None
    style: Theme = Theme()
    sections: list[Section] = []
    # Directory relative paths (images) resolve against. Set by from_yaml.
    base_dir: Path = Field(default=Path("."), exclude=True)

    @field_validator("summary", mode="before")
    @classmethod
    def _summary_flag(cls, value: Any) -> Any:
        if value is True:
            return Summary()
        if value is False:
            return None
        return value

    @classmethod
    def from_dict(cls, data: dict[str, Any], base_dir: Path | str = ".") -> Report:
        base_dir = Path(base_dir)
        report = cls.model_validate(data, context={"base_dir": base_dir})
        report.base_dir = base_dir
        return report

    @classmethod
    def from_yaml(cls, path: Path | str) -> Report:
        path = Path(path)
        data = yaml.safe_load(path.read_text())
        if not isinstance(data, dict):
            raise ValueError(f"{path}: expected a mapping at the top level")
        return cls.from_dict(data, base_dir=path.parent)

    def render(self) -> ReportPDF:
        pdf = ReportPDF(self.style)
        pdf.set_title(self.title)
        if self.author:
            pdf.set_author(self.author)
        ctx = RenderContext(pdf=pdf, theme=self.style, base_dir=self.base_dir)

        pdf.add_page()
        ctx.set_text(self.style.title_size, "B")
        pdf.multi_cell(0, self.style.title_size * 0.5, self.title, new_x="LMARGIN", new_y="NEXT")
        if self.subtitle:
            ctx.gap(1)
            ctx.set_text(self.style.font_size + 3, "", self.style.muted_color)
            pdf.multi_cell(0, 7, self.subtitle, new_x="LMARGIN", new_y="NEXT")
        ctx.gap(8)

        if self.summary is not None:
            self.summary.render(ctx)
        for index, section in enumerate(self.sections, start=1):
            section.render(ctx.child(index))
        return pdf

    def build(self, out: Path | str | None = None) -> Path:
        """Render to `out` (default: `<title>.pdf` next to the YAML) and return the path written."""
        if out is None:
            out = self.base_dir / f"{self.title}.pdf"
        out = Path(out)
        out.parent.mkdir(parents=True, exist_ok=True)
        self.render().output(str(out))
        return out
