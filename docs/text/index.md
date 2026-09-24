# Text

A paragraph of Markdown. Supports **bold**, *italic*, `code`, links, bulleted and numbered lists, and headings.

```yaml
- text: Quantities are in **kg** unless stated otherwise.
```

For more than one line, use a YAML block scalar (`|`). Blank lines separate paragraphs, and a list needs a blank line before it:

```yaml
- text: |
    The batch was released after review.
    See the [SOP](https://example.com/sop) for details.

    Checks performed:

    - Weight within tolerance
    - Label matches the batch record
    - `pH` between 6.8 and 7.2
```

## Fields

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `markdown` | string | required | The Markdown source. *Shorthand*: `- text: "..."` sets this field. |

The long form is equivalent:

```yaml
- text:
    markdown: Quantities are in **kg**.
```

## Notes

- Text uses the theme's `font`, `font_size` and `text_color`. Change them under [`style`](../index.md).
- Markdown headings (`#`, `##`) change the font size only. They are **not** added to the PDF outline or the table of contents. Use a [`title`](../headings/index.md) block for that.
- The built-in fonts only cover Latin-1. Characters outside it (e.g. `≥`, `→`, CJK) need `style.font_files`.
