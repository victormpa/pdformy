"""Build PDF reports from YAML (or Python) with fpdf2."""

from pathlib import Path

from .blocks.band import PageBand
from .blocks.base import Block, register
from .blocks.chart import Chart, Point, Series
from .blocks.grid import Grid
from .blocks.heading import Subtitle, Title
from .blocks.image import Image
from .blocks.section import Section
from .blocks.summary import Summary
from .blocks.table import Column, Table
from .blocks.text import Text
from .context import RenderContext, Theme
from .report import Report

__all__ = [
    "Block", "Chart", "Column", "Grid", "Image", "PageBand", "Point", "RenderContext", "Report",
    "Section", "Series", "Subtitle", "Summary", "Table", "Text", "Theme", "Title", "load", "register",
]


def load(path: Path | str) -> Report:
    return Report.from_yaml(path)
