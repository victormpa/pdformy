# Grid

Places blocks side by side in columns. When there are more blocks than columns, they wrap into further rows.

```yaml
- grid:
    columns: 2
    content:
      - image:
          source: assets/before.png
          caption: Before
      - image:
          source: assets/after.png
          caption: After
```

Use `ratio` for columns of different widths. Here the chart takes two thirds of the width and the table one third:

```yaml
- grid:
    ratio: [2, 1]
    content:
      - chart:
          type: line
          data: [{x: 1, y: 3}, {x: 2, y: 5}, {x: 3, y: 4}]
      - table:
          header: [Run, Result]
          rows: [[1, Pass], [2, Pass], [3, Fail]]
```

## Fields

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `content` | list of blocks | required | The blocks to lay out, filled left to right, then row by row. |
| `columns` | int | number of blocks | How many equal-width columns per row. |
| `ratio` | list of numbers | none | Relative column widths. Its length sets the number of columns. |
| `gap` | number | `5` | Space between columns, in mm. |

With neither `columns` nor `ratio`, every block goes in a single row of equal-width columns. If both are given, `columns` must equal the length of `ratio`.

## Layout

- Each block is drawn inside its cell as if the cell were the page. A `width: 50%` image takes half of the cell, and a table fills the cell.
- The next row starts below the tallest cell of the current row.
- A row that doesn't fit on the rest of the page moves to the next page as a whole. Rows are never split across pages.
- If the last row has fewer blocks than columns, the blocks fill the leftmost cells and the rest stay empty.
- Any block can go in a grid, including another grid. [Sections](../sections/index.md) can't.

!!! warning
    A cell taller than a full page is not split, and the layout will break. Keep tall tables and long text outside of grids.
