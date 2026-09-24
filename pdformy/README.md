# pdfreport

Builds PDF reports from YAML files (or straight from Python) with [fpdf2](https://py-pdf.github.io/fpdf2/). A report is a tree of sections, and each section holds an ordered list of blocks: text, images, tables, charts and grids. The YAML is checked with pydantic before anything is drawn, so a mistake is reported with its location instead of producing a broken PDF.

## Usage

Run from `pdformy/`:

```bash
poetry install    # or: source .venv/bin/activate
python -m pdfreport ../template.yaml -o out.pdf
```

Without `-o`, the file goes to the report's `output` field, or `<title>.pdf` if that is empty, relative to the YAML file. [`template.yaml`](../template.yaml) is a working example of every block.

When the YAML is invalid, the command exits with code 1 and prints one line per error:

```
bad.yaml: invalid report
  sections.0.content.0: table: rows[0] has 1 cells, header has 2
  sections.0.content.1: chart.type: Input should be 'bar', 'line', 'pie' or 'scatter'
```

## Report structure

```yaml
title: Batch Record 001
subtitle: Line 3        # optional
author: QA              # optional, PDF metadata
output: ebr_001.pdf     # optional, default output file
summary: true           # optional table of contents
style:                  # optional theme overrides
  numbered: true
sections:
  - title: Materials
    subtitle: Dispensed quantities
    content:
      - text: Quantities are in **kg**.
      - table: {header: [Item, Qty], rows: [[API, 10]]}
    sections:           # nested sections, any depth
      - title: Excipients
        content: []
```

A section always renders in this order: its title, its subtitle, the blocks in `content`, then its child `sections`. Each section title becomes an entry in the PDF outline (bookmarks) and in the table of contents.

## Blocks

Each item in `content` is a mapping with one key that names the block. Blocks marked *shorthand* can be written as a plain value: `- text: "Hello"` or `- image: assets/logo.png`.

| Block | Fields | Notes |
| --- | --- | --- |
| `text` | `markdown` (shorthand) | Markdown: bold, italic, `code`, links, lists, headings. |
| `image` | `source` (shorthand), `caption`, `width` (`50%` or mm, default `100%`), `align` (`left`/`center`/`right`) | `source` is relative to the YAML file. A missing file is an error when the YAML is loaded. |
| `table` | `header`, `rows`, `caption` | A `header` entry is either a column name or `{name, type, align, width, format}`. `type` is one of `string`, `int`, `float`, `percent`, `date`. It sets the default formatting (`d`, `.2f`, `.1f%`, `%Y-%m-%d`) and alignment (numbers align right). `format` takes a Python format spec, or a strftime pattern for dates. `width` is a relative weight. Every row must have as many cells as the header. |
| `chart` | `type` (`bar`/`line`/`pie`/`scatter`), `data: [{x, y}]` or `series: [{name, data}]`, `title`, `x_label`, `y_label`, `caption`, `width`, `aspect` (height/width, default `0.5`), `align` | Drawn with matplotlib and embedded as vector SVG. A legend appears when there are two or more series. A pie chart takes a single series. |
| `grid` | `content`, `columns` or `ratio`, `gap` (mm, default 5) | Places blocks side by side. `columns: 2` gives equal widths and wraps the blocks into rows of two. `ratio: [2, 1]` sets relative widths. Without either, all blocks go in a single row. A row that doesn't fit on the current page moves to the next one. |
| `title` | `text` (shorthand), `level`, `toc` | A heading inside a section's content. By default it sits one level below the section and is listed in the outline and TOC. |
| `subtitle` | `text` (shorthand) | Muted, italic line. |

## Summary (table of contents)

```yaml
summary: true               # uses the defaults
summary:
  title: Contents
  depth: 2                  # section levels listed
```

The TOC is rendered right after the report title, and page numbers are filled in once the whole document is laid out. Entries link to their pages.

## Style

`style` overrides the fields of `Theme` in [`context.py`](context.py). The most useful ones:

| Field | Default | |
| --- | --- | --- |
| `page_format`, `orientation`, `margin` | `A4`, `portrait`, `18` mm | |
| `font`, `font_size` | `helvetica`, `10` pt | |
| `font_files` | none | TTF paths `{regular, bold, italic, bold_italic}`, needed for characters outside Latin-1 |
| `heading_sizes` | `[16, 13, 11.5, 10.5]` | one size per section level, the last one repeats |
| `numbered` | `false` | prefixes titles with `1`, `1.1`, ... |
| `chart_colors` | 8-hue categorical palette | used in a fixed order |

## Python API

The YAML keys map one-to-one onto the classes, so a report can be built in code:

```python
from pdfreport import Report, Section, Table, Text, Chart, Point, Theme

Report(
    title="EBR 001",
    summary=True,
    style=Theme(numbered=True),
    sections=[
        Section(title="Materials", content=[Table(header=["Item", "Qty"], rows=[["API", 10]])]),
        Section(title="Yield", content=[
            Text(markdown="Yield per step:"),
            Chart(type="bar", data=[Point(x="Mix", y=98.5), Point(x="Dry", y=97.1)]),
        ]),
    ],
).build("ebr_001.pdf")
```

`Report.from_yaml(path)` (or `pdfreport.load(path)`) and `Report.from_dict(data, base_dir)` build the same objects from YAML or a dict. `build(out)` writes the PDF and returns its path. `render()` returns the `fpdf.FPDF` object without writing it.

## Adding a block

Subclass `Block`, declare the fields, implement `render(ctx)` and register the YAML key. The class must be imported (e.g. from [`__init__.py`](__init__.py)) before any YAML is parsed.

```python
from pdfreport import Block, register
from pdfreport.context import RenderContext

@register("signature")
class Signature(Block):
    shorthand = "name"
    name: str

    def render(self, ctx: RenderContext) -> None:
        ctx.set_text()
        ctx.pdf.cell(0, 8, f"Signed: {self.name} ____________", new_x="LMARGIN", new_y="NEXT")
        ctx.gap()
```

`RenderContext` provides the `pdf`, the `theme`, `resolve(path)` for paths relative to the YAML file, and helpers: `set_text`, `gap`, `ensure_space`. Blocks must draw inside `pdf.l_margin`/`pdf.epw` instead of the page width, because a grid narrows the margins to each cell.

## Tests

```bash
python -m pytest -q
```

[`tests/test_parse.py`](../tests/test_parse.py) covers validation and error paths. [`tests/test_render.py`](../tests/test_render.py) renders the template and checks its text, outline and grid layout with pypdf.

## Limitations

- The built-in fonts (`helvetica`, `times`, `courier`) only cover Latin-1. For anything else, set `style.font_files`.
- A grid cell taller than one page is not split and will lay out wrongly.
