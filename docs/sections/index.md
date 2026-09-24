# Section

Sections give a report its structure. Each one has a title, an optional subtitle, a list of content blocks, and optional child sections, nested to any depth.

Sections are not written inside `content`. They go in the report's top-level `sections` list, or in another section's `sections` list:

```yaml
title: Batch Record 001
sections:
  - title: Materials
    subtitle: Dispensed quantities
    content:
      - text: Quantities are in **kg**.
      - table:
          header: [Item, Qty]
          rows: [[API, 10], [Lactose, 42]]
    sections:
      - title: Excipients
        content:
          - text: All excipients were within their expiry dates.
      - title: Packaging
  - title: Yield
    content:
      - chart:
          type: bar
          data: [{x: Mixing, y: 98.5}, {x: Drying, y: 97.1}]
```

## Fields

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `title` | string | required | Drawn as a heading, and added to the PDF outline and the [table of contents](../summaries/index.md). |
| `subtitle` | string | none | A muted, italic line under the title. |
| `content` | list of blocks | `[]` | [Text](../text/index.md), [image](../images/index.md), [table](../tables/index.md), [chart](../charts/index.md), [grid](../grids/index.md), [title and subtitle](../headings/index.md) blocks, drawn in order. |
| `sections` | list of sections | `[]` | Child sections, drawn after this section's `content`. |

## Rendering order

A section draws its title, then its subtitle, then every block in `content`, then each child section in turn. A child section's content always comes after all of its parent's content, whatever order the keys appear in the YAML.

## Levels and numbering

Top-level sections are level 0, their children level 1, and so on. The level sets:

- the heading size, from `style.heading_sizes` (default `[16, 13, 11.5, 10.5]`; deeper levels reuse the last size);
- the indentation in the PDF outline and the table of contents.

Set `style.numbered: true` to prefix each section title with its position:

```yaml
style:
  numbered: true
```

This gives `1  Materials`, `1.1  Excipients`, `1.2  Packaging`, `2  Yield`. The numbers also appear in the outline and the table of contents.
