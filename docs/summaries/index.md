# Summary

A table of contents, placed right after the report title. It lists section titles with dotted leaders and page numbers, and each entry links to its page.

The summary is not written inside `content`. It's a single key at the top level of the report:

```yaml
title: Batch Record 001
summary: true
sections:
  - title: Materials
  - title: Yield
```

To change the defaults, give it a mapping instead:

```yaml
summary:
  title: Table of contents
  depth: 3
```

## Fields

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `title` | string | `Contents` | The heading above the list. |
| `depth` | int | `2` | How many levels to list. `1` lists only top-level sections, `2` adds their children, and so on. |

`summary: true` uses both defaults. `summary: false`, or leaving the key out, means no table of contents.

## What gets listed

- Every [section](../sections/index.md) title down to `depth` levels, with its number when `style.numbered` is on.
- [`title`](../headings/index.md) blocks inside a section's content, unless they have `toc: false`. They count as one level below their section, so with the default `depth: 2` a title inside a top-level section is listed, but one inside a child section is not.

## Notes

- The page numbers are filled in after the whole report has been laid out, so they are always correct.
- The table of contents gets its own page after the title, and the first section starts on a new page. A long table of contents continues onto more pages as needed.
- Top-level entries are bold. Deeper levels are indented.
