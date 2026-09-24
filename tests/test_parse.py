from pathlib import Path

import pytest
from pydantic import ValidationError

from pdfreport import Chart, Grid, Report, Summary, Table, Text

ROOT = Path(__file__).parent.parent


def report(*content, **extra):
    return {"title": "T", "sections": [{"title": "S", "content": list(content)}], **extra}


def test_template_loads():
    r = Report.from_yaml(ROOT / "template.yaml")
    assert isinstance(r.summary, Summary)
    section_1_1 = r.sections[0].sections[0]
    assert [type(b) for b in section_1_1.content] == [Text, type(section_1_1.content[1]), Table, Chart, Chart]
    grid = r.sections[1].content[0]
    assert isinstance(grid, Grid) and grid.columns == 2


def test_shorthand_and_summary_flag():
    r = Report.from_dict(report({"text": "hello **world**"}, summary=True))
    assert r.sections[0].content[0] == Text(markdown="hello **world**")
    assert r.summary == Summary()


def test_table_header_accepts_names_and_formats_by_type():
    t = Table.model_validate({"header": ["A", {"name": "B", "type": "percent"}], "rows": [["x", 12.345]]})
    assert [c.name for c in t.header] == ["A", "B"]
    assert t.header[1].format_value(12.345) == "12.3%"
    assert t.header[1].text_align == "RIGHT"


@pytest.mark.parametrize(
    "block, message",
    [
        ({"paragraph": "x"}, "unknown block 'paragraph'"),
        ({"text": "a", "image": "b"}, "exactly one of"),
        ({"table": {"header": ["A", "B"], "rows": [["1"]]}}, "rows[0] has 1 cells, header has 2"),
        ({"image": {"source": "missing.png"}}, "image file not found"),
        ({"chart": {"type": "radar", "data": [{"x": "a", "y": 1}]}}, "chart.type"),
        ({"chart": {"type": "bar"}}, "exactly one of `data` or `series`"),
        ({"grid": {"columns": 2, "ratio": [1], "content": [{"text": "a"}]}}, "columns is 2 but ratio has 1"),
    ],
)
def test_invalid_blocks_report_their_path(block, message):
    with pytest.raises(ValidationError) as e:
        Report.from_dict(report(block), base_dir=ROOT)
    assert message in str(e.value)
    assert "sections.0.content.0" in str(e.value)


def test_unknown_section_key_is_rejected():
    with pytest.raises(ValidationError, match="sections.0.text"):
        Report.from_dict({"title": "T", "sections": [{"title": "S", "text": "old format"}]})
