"""Benchmark: every YAML under tests/templates must parse and render to a PDF."""

from pathlib import Path

import pytest
from pypdf import PdfReader

from pdformy import Report

TEMPLATES = sorted((Path(__file__).parent / "templates").glob("*.yaml"))


@pytest.mark.parametrize("path", TEMPLATES, ids=[p.stem for p in TEMPLATES])
def test_template_scenario_renders(path: Path, tmp_path: Path) -> None:
    report = Report.from_yaml(path)
    out = report.build(tmp_path / f"{path.stem}.pdf")

    reader = PdfReader(out)
    assert len(reader.pages) >= 1
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    assert report.title in text
