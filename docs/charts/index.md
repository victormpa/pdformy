# Chart

A bar, line, pie or scatter chart. Charts are drawn with matplotlib and embedded as vector graphics, so they stay sharp at any zoom level.

## Single series

Give the points directly with `data`. Each point has an `x` (a label or a number) and a numeric `y`.

```yaml
- chart:
    type: bar
    title: Yield by step
    y_label: "%"
    data:
      - {x: Mixing, y: 98.5}
      - {x: Drying, y: 97.1}
      - {x: Packing, y: 99.2}
```

## Several series

Use `series` instead of `data` to compare named series. A legend is added above the plot. Bars from different series are placed side by side.

```yaml
- chart:
    type: line
    x_label: Month
    y_label: Units
    series:
      - name: Plan
        data: [{x: Jan, y: 10}, {x: Feb, y: 14}, {x: Mar, y: 18}]
      - name: Actual
        data: [{x: Jan, y: 9}, {x: Feb, y: 15}, {x: Mar, y: 17}]
    caption: Figure 3. Plan vs. actual output
```

## Pie

A pie chart takes a single series. Each slice is labeled with its `x` and its share of the total.

```yaml
- chart:
    type: pie
    width: 60%
    aspect: 1
    data:
      - {x: Passed, y: 182}
      - {x: Reworked, y: 12}
      - {x: Rejected, y: 6}
```

## Fields

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `type` | `bar`, `line`, `pie`, `scatter` | required | The kind of chart. |
| `data` | list of points | none | A single series of `{x, y}` points. Use either `data` or `series`, not both. |
| `series` | list of `{name, data}` | none | Several named series. |
| `title` | string | none | Bold, left-aligned title above the plot. |
| `x_label` | string | none | Label for the x axis. Ignored by pie charts. |
| `y_label` | string | none | Label for the y axis. Ignored by pie charts. |
| `caption` | string | none | Small, italic, centered text below the chart. |
| `width` | `"N%"` or number | `"100%"` | A percentage of the available width, or a width in mm. |
| `aspect` | number | `0.5` | Height divided by width. Use `1` for a square, which suits pie charts. |
| `align` | `left`, `center`, `right` | `center` | Horizontal position when the chart is narrower than the available width. |

## Notes

- Colors come from `style.chart_colors`, in order: the first series uses the first color, and so on. For a pie chart, each slice gets the next color.
- Bar charts treat `x` as a category label, so the bars are evenly spaced in the order given. Line and scatter charts plot numeric `x` values on a numeric axis.
- Text in the chart uses the theme's colors but matplotlib's font, not `style.font`.
- Mistakes are reported when the YAML is loaded:

    ```
    report.yaml: invalid report
      sections.0.content.0: chart: chart needs exactly one of `data` or `series`
    ```
