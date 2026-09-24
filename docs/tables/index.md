# Table

A table with a bold, shaded header row. Each column can have a type that controls how its values are formatted and aligned.

```yaml
- table:
    header: [Item, Lot, Qty]
    rows:
      - [API, L-2291, 10]
      - [Lactose, L-1840, 42]
```

```yaml
- table:
    header:
      - name: Step
        width: 2
      - name: Started
        type: date
        format: "%d/%m/%Y"
      - name: Yield
        type: percent
      - name: Mass (kg)
        type: float
        format: ",.3f"
    rows:
      - [Mixing, 2026-03-02, 98.5, 1250.4]
      - [Drying, 2026-03-03, 97.1, 1214.08]
      - [Packing, 2026-03-05, 99.2, 1204.37]
    caption: Table 2. Yield per step
```

## Fields

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `header` | list of columns | required | One entry per column: either a plain name, or a [column mapping](#columns). |
| `rows` | list of lists | required | The cell values. Every row must have exactly as many cells as `header`. |
| `caption` | string | none | Small, italic, centered text below the table. |

### Columns

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `name` | string | required | The header text. |
| `type` | `string`, `int`, `float`, `percent`, `date` | `string` | Sets the default format and alignment (see below). |
| `format` | string | from `type` | A Python format spec (`.1f`, `,d`, `08.3f`), or a strftime pattern for `date` columns. |
| `align` | `left`, `center`, `right` | from `type` | Overrides the default alignment. |
| `width` | number | `1` | A relative width. A column with `width: 2` is twice as wide as one without a width. |

| `type` | Default format | Example value | Shown as | Default alignment |
| --- | --- | --- | --- | --- |
| `string` | as written | `L-2291` | `L-2291` | left |
| `int` | `d` | `42.9` | `42` | right |
| `float` | `.2f` | `1250.4` | `1250.40` | right |
| `percent` | `.1f` then `%` | `98.5` | `98.5%` | right |
| `date` | `%Y-%m-%d` | `2026-03-02` | `2026-03-02` | left |

## Notes

- `percent` doesn't multiply by 100. Write `98.5` to get `98.5%`, not `0.985`.
- `int` cuts off decimals instead of rounding: `42.9` becomes `42`.
- A `date` column only reformats real YAML dates, meaning unquoted `2026-03-02`. A quoted `"2026-03-02"` is a string and is shown exactly as written.
- An empty or `null` cell stays blank in every column type.
- The table always fills the available width: the page width minus the margins, or the cell width inside a [grid](../grids/index.md).
- When a table runs past the end of a page, it continues on the next page and the header row is repeated.
- A row with the wrong number of cells is reported when the YAML is loaded:

    ```
    report.yaml: invalid report
      sections.0.content.0: table: rows[1] has 2 cells, header has 3
    ```
