# Heading

Two blocks for headings inside a section's `content`: `title` and `subtitle`.

Every [section](../sections/index.md) already draws its own title and subtitle. Use these blocks to split a section's content further without creating a new section.

## `title`

A bold heading. By default it sits one level below the enclosing section and is listed in the PDF outline (bookmarks) and the [table of contents](../summaries/index.md).

```yaml
- title: Deviations
```

```yaml
- title:
    text: Reviewer notes
    level: 2
    toc: false
```

### Fields

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `text` | string | required | The heading text. *Shorthand*: `- title: "..."` sets this field. |
| `level` | int | one below the section | Outline level. `0` is the level of top-level sections. It also picks the font size from `style.heading_sizes`. |
| `toc` | bool | `true` | Set to `false` to leave the heading out of the PDF outline and the table of contents. |

### Notes

- A title is never left alone at the bottom of a page. If there isn't room for it plus about 25 mm of what follows, it moves to the next page.
- The font size comes from `style.heading_sizes` (default `[16, 13, 11.5, 10.5]`), indexed by level. Levels past the end of the list reuse its last size.
- Titles are not numbered, even with `style.numbered: true`. Only section titles are.

## `subtitle`

A muted, italic line, slightly larger than body text.

```yaml
- subtitle: Figures are provisional until QA sign-off.
```

### Fields

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `text` | string | required | The subtitle text. *Shorthand*: `- subtitle: "..."` sets this field. |
