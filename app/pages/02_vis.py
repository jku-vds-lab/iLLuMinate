
import dash
from dash import Input, Output, State, dcc, no_update
import dash_iconify
import dash_mantine_components as dmc

import pandas as pd

from app.analysis.format import compute_format_matrix, get_format_stats
from app.analysis.style import compute_style_matrix
from app.analysis.topic import compute_topic_matrix
from app.analysis.utils import *

from app.components import fingerprints_panel
from app.components.heatmap import *
from app.enums import VariationMode

from app.callbacks import *


dash.register_page(__name__, path="/vis")


def layout():
    return dmc.Tabs(
        mt="xs",
        value="topic",
        fw=650,
        children=[
            dmc.TabsList(
                [
                    dmc.TabsTab("Topics", value="topic", leftSection=dash_iconify.DashIconify(icon="streamline-plump-color:news-paper-flat", width=20)),
                    dmc.TabsTab("Style", value="style", leftSection=dash_iconify.DashIconify(icon="streamline-plump-color:paint-palette-flat", width=20)),
                    dmc.TabsTab("Format", value="format", leftSection=dash_iconify.DashIconify(icon="streamline-plump-color:text-box-1-flat", width=20)),
                ]
            ),
            fingerprints_panel(
                var_mode=VariationMode.TOPICS,
                controls=[dcc.Download(id="topic-download")]
            ),
            fingerprints_panel(
                var_mode=VariationMode.STYLE,
                controls=[
                    dmc.Group(
                        [
                            dmc.NumberInput(label="Factors", w=100, min=1, max=10, id="style-factor-count"),
                            dmc.Button("Rerun", mt=25, id="rerun-style-analysis"),
                            ], gap=10
                    ),
                ]
            ),
            fingerprints_panel(
                var_mode=VariationMode.FORMAT,
            )
        ],
    )

@dash.callback(
    Output("topic-heatmap-switch", "checked"),
    Output("topic-heatmap-container", "children", allow_duplicate=True),
    Output("topic-row-meta-store", "data", allow_duplicate=True),
    Input("topic-heatmap-switch", "checked"),
    State("data-topic-store", "data"),
    State("topic-labels-store", "data"),
    prevent_initial_call=True,
)
def toggle_topic_heatmap_mode(checked, data, labels):
    if not dash.ctx.triggered_id:
        return no_update

    prob, col_meta, row_meta = compute_topic_matrix(pd.DataFrame.from_records(data), per_prompt=checked, labels=labels)
    heatmap = dcc.Graph(
        id="topic-heatmap",
        figure=build_heatmap_per_prompt(prob, VariationMode.TOPICS, row_meta=row_meta) if checked else build_heatmap_per_response(prob, col_meta, VariationMode.TOPICS, row_meta=row_meta),
        config={"scrollZoom": True},
        clear_on_unhover=True
    )
    
    return checked, heatmap, row_meta.reset_index().to_dict("records")

@dash.callback(
    Output("style-heatmap-switch", "checked"),
    Output("style-heatmap-container", "children", allow_duplicate=True),
    Output("style-factor-row-meta-store", "data", allow_duplicate=True),
    Input("style-heatmap-switch", "checked"),
    State("style-decomposed-scores-store", "data"),
    State("style-factor-labels-store", "data"),
    prevent_initial_call=True,
)
def toggle_style_heatmap_mode(checked, decomposed_scores, labels):
    if not dash.ctx.triggered_id:
        return no_update

    norm_scores, col_meta, row_meta = compute_style_matrix(pd.DataFrame.from_records(decomposed_scores), bipolar=False, per_prompt=checked, labels=labels)
    heatmap = dcc.Graph(
        id="style-heatmap",
        figure=build_heatmap_per_prompt(norm_scores, VariationMode.STYLE, row_meta=row_meta) if checked else build_heatmap_per_response(norm_scores, col_meta, VariationMode.STYLE, row_meta=row_meta),
        config={"scrollZoom": True},
        clear_on_unhover=True
    )
    
    return checked, heatmap, row_meta.reset_index().to_dict("records")

@dash.callback(
    Output("format-heatmap-switch", "checked"),
    Output("format-heatmap-container", "children", allow_duplicate=True),
    Input("format-heatmap-switch", "checked"),
    State("format-stats-store", "data"),
    prevent_initial_call=True,
)
def toggle_format_heatmap_mode(checked, data):
    if not dash.ctx.triggered_id:
        return no_update
    
    norm_scores, col_meta = compute_format_matrix(pd.DataFrame.from_records(data), per_prompt=checked)
    heatmap = dcc.Graph(
        id="format-heatmap",
        figure=build_heatmap_per_prompt(norm_scores, VariationMode.FORMAT, row_meta=None) if checked else build_heatmap_per_response(norm_scores, col_meta, VariationMode.FORMAT, row_meta=None),
        config={"scrollZoom": True},
        clear_on_unhover=True
        )
    
    return checked, heatmap

@dash.callback(
    Output("temporal-topic-box", "style"),
    Output("topic-grid", "style"),
    Output("data-topic-store", "data"),
    Output("topic-store", "data"),
    Output("topic-docs-store", "data"),
    Output("topic-labels-store", "data"),
    Output("topic-row-meta-store", "data"),
    Output("topic-heatmap-container", "children"),
    Output("topic-col-meta-store", "data"),
    Input("run-topic-analysis", "n_clicks"),
    State("data-store", "data"),
    prevent_initial_call=True,
    running=[
        (Output("topic-loading-overlay", "visible"), True, False),
    ],
)
def run_topic_modeling(n_clicks, data):
    if not dash.ctx.triggered_id or not n_clicks or n_clicks <= 0:
        return no_update
    
    from app.analysis.topic import topic_modeling_pipeline
    from app.components.heatmap import build_heatmap_per_response

    df, topics, docs, labels = topic_modeling_pipeline(data, with_labels=True)

    prob, col_meta, row_meta = compute_topic_matrix(df, labels=labels)

    heatmap = dcc.Graph(
        id="topic-heatmap",
        figure=build_heatmap_per_response(prob, col_meta, VariationMode.TOPICS, row_meta=row_meta), 
        config={"scrollZoom": True},
        clear_on_unhover=True
    )

    # zip_buffer = io.BytesIO()

    # with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
    #     zf.writestr("topic_modeling_df.csv", df.to_csv(index=False))

    #     zf.writestr("row_meta.csv", row_meta.reset_index().to_csv(index=False))

    #     def write_any(name, obj):
    #         if isinstance(obj, pd.DataFrame):
    #             zf.writestr(name, obj.to_csv(index=False))
    #         elif isinstance(obj, list):
    #             if len(obj) > 0 and isinstance(obj[0], dict):
    #                 zf.writestr(name, pd.DataFrame(obj).to_csv(index=False))
    #             else:
    #                 zf.writestr(name.replace(".csv", ".json"), json.dumps(obj, ensure_ascii=False, indent=2))
    #         elif isinstance(obj, dict):
    #             zf.writestr(name.replace(".csv", ".json"), json.dumps(obj, ensure_ascii=False, indent=2))
    #         else:
    #             zf.writestr(name.replace(".csv", ".txt"), str(obj))

    #     write_any("topics.csv", topics)
    #     write_any("docs.csv", docs)
    #     write_any("labels.csv", labels)

    # zip_buffer.seek(0)

    # download = dcc.send_bytes(zip_buffer.getvalue(), "topic_modeling_outputs.zip")

    return {"display": "none"}, {"display": "block"}, df.to_dict("records"), topics, docs, labels, row_meta.reset_index().to_dict("records"), heatmap, col_meta.to_dict("records")#, download

@dash.callback(
    Output("temporal-style-box", "style"),
    Output("style-grid", "style"),
    Output("style-features-store", "data"),
    Output("style-loadings-store", "data"),
    Output("style-scores-store", "data"),
    Output("style-decomposed-scores-store", "data"),
    Output("style-factors-store", "data"),
    Output("style-factor-labels-store", "data"),
    Output("style-feature-detail-store", "data"),
    Output("style-factor-row-meta-store", "data"),
    Output("style-col-meta-store", "data"),
    Output("style-heatmap-container", "children"),
    Output("style-factor-count", "value"),
    Input("run-style-analysis", "n_clicks"),
    Input("start-factor-count", "value"),
    State("data-store", "data"),
    prevent_initial_call=True,
    running=[
        (Output("style-loading-overlay", "visible"), True, False),
    ],
)
def run_biber_analysis(n_clicks, factor_count, data):
    if not dash.ctx.triggered_id or not n_clicks or n_clicks <= 0:
        return no_update
    
    from app.analysis.style import biber_analysis_pipeline
    from app.components.heatmap import build_heatmap_per_response

    features, loadings, scores, decomposed_scores, factors, feature_detail, labels = biber_analysis_pipeline(data, factor_count, with_labels=True)

    norm_scores, col_meta, row_meta = compute_style_matrix(decomposed_scores, labels=labels)

    heatmap = dcc.Graph(
        id="style-heatmap",
        figure=build_heatmap_per_response(norm_scores, col_meta, VariationMode.STYLE, row_meta=row_meta), 
        config={"scrollZoom": True},
        clear_on_unhover=True
    )

    return {"display": "none"}, {"display": "block"}, features.to_dict("records"), loadings.to_dict("records"), scores.to_dict("records"), decomposed_scores.to_dict("records"), factors, labels, feature_detail.to_dict("records"), row_meta.reset_index().to_dict("records"), col_meta.to_dict("records"), heatmap, factor_count

@dash.callback(
    Output("temporal-format-box", "style"),
    Output("format-grid", "style"),
    Output("format-stats-store", "data"),
    Output("format-col-meta-store", "data"),
    Output("format-heatmap-container", "children"),
    Input("run-format-analysis", "n_clicks"),
    State("data-store", "data"),
    prevent_initial_call=True,
    running=[
        (Output("format-loading-overlay", "visible"), True, False),
    ],
)
def run_format_analysis(n_clicks, data):
    if not dash.ctx.triggered_id or not n_clicks or n_clicks <= 0:
        return no_update
    
    from app.components.heatmap import build_heatmap_per_response

    format_df = get_format_stats(data)

    norm_scores, col_meta = compute_format_matrix(format_df)

    heatmap = dcc.Graph(
        id="format-heatmap",
        figure=build_heatmap_per_response(norm_scores, col_meta, VariationMode.FORMAT), 
        config={"scrollZoom": True},
        clear_on_unhover=True
    )

    return {"display": "none"}, {"display": "block"}, format_df.to_dict("records"), col_meta.to_dict("records"), heatmap
