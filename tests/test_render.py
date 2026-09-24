from pathlib import Path

from pypdf import PdfReader

from pdformy import Grid, Report, Section, Table, Text, Theme
from pdformy.context import RenderContext
from pdformy.report import ReportPDF

ROOT = Path(__file__).parent.parent


def outline_titles(reader: PdfReader, items=None) -> list:
    """Nested outline as [title, [children]] pairs."""
    result = []
    for item in reader.outline if items is None else items:
        if isinstance(item, list):
            result[-1][1].extend(outline_titles(reader, item))
        else:
            result.append([item.title, []])
    return result


def test_template_renders(tmp_path):
    out = Report.from_yaml(ROOT / "template.yaml").build(tmp_path / "t.pdf")
    reader = PdfReader(out)
    text = "\n".join(page.extract_text() for page in reader.pages)

    for expected in [
        "Template Example",
        "Contents",
        "Section 1.1",
        "Row 2 Cell 2",
        "100.5",
        "Grid view",
        "Image 2.1",
    ]:
        assert expected in text
    assert outline_titles(reader) == [
        ["Section 1", [["Section 1.1", []]]],
        ["Grid view", []],
    ]
    # The TOC lists each section with its page number.
    assert "Grid view" in reader.pages[0].extract_text()


def test_python_api_and_numbering(tmp_path):
    report = Report(
        title="EBR 001",
        style=Theme(numbered=True),
        sections=[
            Section(
                title="Materials",
                content=[Table(header=["Item", "Qty"], rows=[["API", 10]])],
            ),
            Section(
                title="Steps",
                sections=[
                    Section(title="Mixing", content=[Text(markdown="Mix *well*.")])
                ],
            ),
        ],
    )
    reader = PdfReader(report.build(tmp_path / "ebr.pdf"))
    assert outline_titles(reader) == [
        ["1  Materials", []],
        ["2  Steps", [["2.1  Mixing", []]]],
    ]


def test_grid_ends_below_tallest_cell_and_restores_margins():
    theme = Theme()
    pdf = ReportPDF(theme)
    pdf.add_page()
    ctx = RenderContext(pdf=pdf, theme=theme)
    short, tall = Text(markdown="short"), Text(
        markdown="\n\n".join(["tall paragraph"] * 6)
    )

    top = pdf.y
    tall.render(ctx)
    tall_bottom = pdf.y
    pdf.set_y(top)

    margins = (pdf.l_margin, pdf.r_margin)
    Grid(content=[short, tall]).render(ctx)
    assert (pdf.l_margin, pdf.r_margin) == margins
    assert pdf.x == pdf.l_margin
    assert abs(pdf.y - tall_bottom) < 0.01


def test_grid_row_moves_to_next_page_when_it_does_not_fit():
    theme = Theme()
    pdf = ReportPDF(theme)
    pdf.add_page()
    ctx = RenderContext(pdf=pdf, theme=theme)
    pdf.set_y(pdf.page_break_trigger - 10)
    Grid(content=[Text(markdown="a\n\nb\n\nc\n\nd"), Text(markdown="e")]).render(ctx)
    assert pdf.page == 2
