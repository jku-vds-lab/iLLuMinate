import dash
from dash import Input, Output, State, no_update
from dash import dcc
import pandas as pd

from app.callbacks.click.helpers import get_heatmap_cell_indices

def register_format_click_callback():
    @dash.callback(
        Output("format-details-panel", "children"),
        Input("format-heatmap", "clickData"),
        State("data-store", "data"),
        State("format-col-meta-store", "data"),
        State("format-heatmap", "figure"),
        prevent_initial_call=True,
    )
    def _on_format_cell_click(clickData, data, col_meta, fig):
        base = get_heatmap_cell_indices(clickData, fig)
        if base is None:
            return no_update

        _, col_idx = base

        col_meta_df = pd.DataFrame.from_records(col_meta)

        response_idx = int(col_meta_df.iloc[col_idx]["response_idx"])

        return dcc.Markdown(
            data[response_idx]["response"],
            style={"fontWeight": 400},
        )

    return _on_format_cell_click


register_format_click_callback()
