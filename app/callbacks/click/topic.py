
import dash
from dash import Input, Output, State, no_update

import pandas as pd

from .helpers import get_heatmap_cell_indices
from app.components import topic_detail_panel

MAIN_TRACE_IDX = 1

def get_selected_topic_cell(clickData, fig, row_meta, col_meta):
    base = get_heatmap_cell_indices(clickData, fig)
    if base is None:
        return None

    row_idx, col_idx = base

    row_meta_df = pd.DataFrame.from_records(row_meta)
    col_meta_df = pd.DataFrame.from_records(col_meta)

    topic = row_meta_df.iloc[row_idx]["id"]
    response_idx = int(col_meta_df.iloc[col_idx]["response_idx"])

    return topic, response_idx

def get_topic_definition(labels, topic):
    if not labels:
        return ""

    return labels.get(str(topic), {}).get("definition", "")

def get_topic_sentences(topics_data, topic, response_idx):
    topics_df = pd.DataFrame.from_records(topics_data)

    return topics_df[
        (topics_df.topic == topic)
        & (topics_df.response_idx == response_idx)
    ].sentence.tolist()

def build_topic_details_panel(
    clickData,
    fig,
    topics,
    docs,
    topics_data,
    row_meta,
    col_meta,
    labels,
    data,
):
    selection = get_selected_topic_cell(
        clickData=clickData,
        fig=fig,
        row_meta=row_meta,
        col_meta=col_meta,
    )

    if selection is None:
        return no_update

    topic, response_idx = selection

    topic_info = topics.get(str(topic), [])
    topic_docs = docs.get(str(topic), [])
    definition = get_topic_definition(labels, topic)

    topic_sentences = get_topic_sentences(
        topics_data=topics_data,
        topic=topic,
        response_idx=response_idx,
    )

    response = data[int(response_idx)]["response"]

    return topic_detail_panel(
        definition=definition,
        topic_info=topic_info,
        topic_docs=topic_docs,
        response=response,
        topic_sentences=topic_sentences,
    )

def register_topic_click_callback():
    @dash.callback(
        Output("topic-details-panel", "children"),
        Input("topic-heatmap", "clickData"),
        State("topic-heatmap", "figure"),
        State("topic-store", "data"),
        State("topic-docs-store", "data"),
        State("data-topic-store", "data"),
        State("topic-row-meta-store", "data"),
        State("topic-col-meta-store", "data"),
        State("topic-labels-store", "data"),
        State("data-store", "data"),
        prevent_initial_call=True,
    )
    def _on_topic_cell_click(
        clickData,
        fig,
        topics,
        docs,
        topics_data,
        row_meta,
        col_meta,
        labels,
        data,
    ):
        return build_topic_details_panel(
            clickData=clickData,
            fig=fig,
            topics=topics,
            docs=docs,
            topics_data=topics_data,
            row_meta=row_meta,
            col_meta=col_meta,
            labels=labels,
            data=data,
        )

    return _on_topic_cell_click

register_topic_click_callback()
