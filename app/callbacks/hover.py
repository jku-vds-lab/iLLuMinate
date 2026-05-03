
import dash
from dash import Input, Output, State, no_update, Patch

HOVER_SHAPE_NAMES = {"hover-row", "hover-col", "hover-cell"}


def axis_layout_key(axis_name: str) -> str:
    return "xaxis" + axis_name[1:] if axis_name.startswith("x") else "yaxis" + axis_name[1:]


def clear_hover_shapes(fig):
    existing = fig.get("layout", {}).get("shapes", []) or []
    return [s for s in existing if s.get("name") not in HOVER_SHAPE_NAMES]


def hover_patch(hoverData, fig, checked):
    if not fig:
        return no_update

    patch = Patch()
    kept = clear_hover_shapes(fig)

    def finish():
        patch["layout"]["shapes"] = kept
        return patch

    if not hoverData:
        return finish()

    pt = hoverData["points"][0]
    main_idx = 0 if bool(checked) else 1

    if pt.get("curveNumber") != main_idx:
        return finish()

    row_label = pt.get("y")
    x_val = pt.get("x")

    if row_label is None or x_val is None:
        return finish()

    main_trace = fig["data"][main_idx]

    y_labels = main_trace.get("y", []) or []
    if row_label not in y_labels:
        return finish()

    row_idx = y_labels.index(row_label)

    xaxis_name = main_trace.get("xaxis", "x")
    yaxis_name = main_trace.get("yaxis", "y")

    xlayout = fig["layout"][axis_layout_key(xaxis_name)]
    ylayout = fig["layout"][axis_layout_key(yaxis_name)]

    x_domain = xlayout.get("domain", [0, 1])
    y_domain = ylayout.get("domain", [0, 1])

    kept.append(dict(
        type="rect",
        xref="paper",
        yref=yaxis_name,
        x0=x_domain[0],
        x1=x_domain[1],
        y0=row_idx - 0.5,
        y1=row_idx + 0.5,
        fillcolor="rgba(0,0,0,0.10)",
        line=dict(width=0),
        layer="above",
        name="hover-row",
    ))

    x0 = x1 = None

    if isinstance(x_val, (int, float)):
        x0, x1 = x_val - 0.5, x_val + 0.5
    else:
        x_labels = main_trace.get("x", []) or []
        if x_val in x_labels:
            col_idx = x_labels.index(x_val)
            x0, x1 = col_idx - 0.5, col_idx + 0.5

    if x0 is not None:
        kept.extend([
            dict(
                type="rect",
                xref=xaxis_name,
                yref="paper",
                x0=x0,
                x1=x1,
                y0=y_domain[0],
                y1=y_domain[1],
                fillcolor="rgba(0,0,0,0.08)",
                line=dict(width=0),
                layer="above",
                name="hover-col",
            ),
            dict(
                type="rect",
                xref=xaxis_name,
                yref=yaxis_name,
                x0=x0,
                x1=x1,
                y0=row_idx - 0.5,
                y1=row_idx + 0.5,
                fillcolor="rgba(0,0,0,0.25)",
                line=dict(width=0),
                layer="above",
                name="hover-cell",
            ),
        ])

    return finish()

def register_hover_callback(heatmap_id: str, switch_id: str):
    @dash.callback(
        Output(heatmap_id, "figure"),
        Input(heatmap_id, "hoverData"),
        State(heatmap_id, "figure"),
        Input(switch_id, "checked"),
        prevent_initial_call=True,
    )
    def _callback(hoverData, fig, checked):
        return hover_patch(hoverData, fig, checked)

    return _callback


register_hover_callback("topic-heatmap", "topic-heatmap-switch")
register_hover_callback("style-heatmap", "style-heatmap-switch")
register_hover_callback("format-heatmap", "format-heatmap-switch")
