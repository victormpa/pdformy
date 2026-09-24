# PDFormy

Build PDF reports from YAML files (or straight from Python) with [fpdf2](https://py-pdf.github.io/fpdf2/). A report is a tree of sections, and each section holds an ordered list of blocks: text, images, tables, charts and grids. The YAML is checked with pydantic before anything is drawn, so a mistake is reported with its location instead of producing a broken PDF.

Check the [documentation](https://victormpa.github.io/pdformy/) for more details.

## Installation

```bash
poetry install pdformy
```

## Usage

```bash
pdformy template.yaml -o out.pdf
```