# Image

Places an image file (PNG, JPEG, GIF or SVG) with an optional caption.

```yaml
- image: assets/logo.png
```

```yaml
- image:
    source: assets/line_3.png
    caption: Figure 1. Line 3 layout
    width: 60%
    align: left
```

## Fields

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `source` | string | required | Path to the image, relative to the YAML file. Absolute paths also work. *Shorthand*: `- image: path.png` sets this field. |
| `caption` | string | none | Small, italic, centered text below the image. |
| `width` | `"N%"` or number | `"100%"` | A percentage of the available width, or a width in mm. The height follows the image's aspect ratio. |
| `align` | `left`, `center`, `right` | `center` | Horizontal position when the image is narrower than the available width. |

## Notes

- A missing file is reported when the YAML is loaded, before anything is drawn:

    ```
    report.yaml: invalid report
      sections.0.content.0: image.source: image file not found: assets/missing.png
    ```

- "Available width" is the page width minus the margins, or the cell width when the image is inside a [grid](../grids/index.md).
- A width in mm larger than the available width is reduced to fit. A percentage over `100%` is not, and the image will run past the margin.
