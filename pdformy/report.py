from __future__ import annotations

import getpass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from fpdf import FPDF
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .blocks.band import PageBand, draw_footer, draw_header, measure_band
from .blocks.section import Section
from .blocks.summary import Summary
from .context import RenderContext, Theme


class ReportPDF(FPDF):
    def __init__(
        self,
        theme: Theme,
        *,
        header: PageBand | None = None,
        footer: PageBand | None = None,
        base_dir: Path = Path("."),
        variables: dict[str, str] | None = None,
    ) -> None:
        super().__init__(orientation=theme.orientation, format=theme.page_format)
        self.theme = theme
        self.page_header = header
        self.page_footer = footer
        self.base_dir = base_dir
        self.band_variables = variables or {}
        self._footer_reserve = theme.margin
        self.set_margins(theme.margin, theme.margin)
        self.set_auto_page_break(True, margin=theme.margin)
        for style, path in theme.font_files.items():
            fpdf_style = {"regular": "", "bold": "B", "italic": "I", "bold_italic": "BI"}[style]
            self.add_font(theme.font, fpdf_style, str(path))

    def _band_ctx(self) -> RenderContext:
        return RenderContext(pdf=self, theme=self.theme, base_dir=self.base_dir)

    def _page_variables(self) -> dict[str, str]:
        return {
            **self.band_variables,
            "current_page": str(self.page_no()),
            "total_pages": self.str_alias_nb_pages or "{nb}",
        }

    def header(self) -> None:
        ctx = self._band_ctx()
        variables = self._page_variables()
        reserve = self.theme.margin
        if self.page_footer is not None and self.page_footer.visible_on(self.page):
            reserve = max(self.theme.margin, measure_band(self.page_footer, ctx, variables))
        self._footer_reserve = reserve
        self.set_auto_page_break(True, margin=reserve)

        if self.page_header is not None and self.page_header.visible_on(self.page):
            draw_header(self.page_header, ctx, variables)

    def footer(self) -> None:
        if self.page_footer is not None:
            if self.page_footer.visible_on(self.page):
                draw_footer(
                    self.page_footer,
                    self._band_ctx(),
                    self._page_variables(),
                    self._footer_reserve,
                )
            return
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
    header: PageBand | None = None
    footer: PageBand | None = None
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
        now = datetime.now().astimezone()
        offset = now.strftime("%z")
        offset = f"{offset[:-2]}:{offset[-2:]}" if offset else ""
        variables = {
            "datetime": f"{now.strftime('%Y-%m-%d %H:%M')} {offset}".rstrip(),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M"),
            "user": getpass.getuser(),
            "title": self.title,
            "subtitle": self.subtitle or "",
            "author": self.author or "",
        }
        pdf = ReportPDF(
            self.style,
            header=self.header,
            footer=self.footer,
            base_dir=self.base_dir,
            variables=variables,
        )
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
