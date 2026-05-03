import dash
from dash import Input, Output, State, no_update

import pandas as pd

from app.analysis.tokenizer import tokenize_response
from .helpers import get_heatmap_cell_indices
from app.components import style_detail_panel

MAIN_TRACE_IDX = 1


def get_selected_style_cell(clickData, fig, row_meta, col_meta):
    base = get_heatmap_cell_indices(clickData, fig)
    if base is None:
        return None

    row_idx, col_idx = base

    row_meta_df = pd.DataFrame.from_records(row_meta)
    factor_idx = row_meta_df.iloc[row_idx]["id"]

    parts = factor_idx.split("_")
    factor_id = "_".join(parts[:2])
    factor_dir = parts[-1] if len(parts) > 2 else "pos"

    col_meta_df = pd.DataFrame.from_records(col_meta)
    response_idx = int(col_meta_df.iloc[col_idx]["response_idx"])

    return factor_id, factor_dir, response_idx

def find_factor(factors, factor_id):
    return next(
        (factor for factor in factors if factor["factor_id"] == factor_id),
        None,
    )

def get_feature_descriptions(factor, factor_dir, feature_detail):
    feature_details = pd.DataFrame.from_records(feature_detail)

    feature_names = [
        item["feature"]
        for item in factor[factor_dir]["features"]
    ]

    descriptions_by_feature = feature_details.set_index("Feature")["Description"]

    return [
        f"{'_'.join(name.split('_')[2:])}: {descriptions_by_feature.get(name, '')}"
        for name in feature_names
    ]

def get_factor_label_content(labels, factor_id, factor_dir):
    factor_idx = f"{factor_id}_{factor_dir}"

    return (
        labels.get(factor_idx)
        or labels.get(f"{factor_idx}_pos")
        or labels.get(factor_id)
    )

def get_evidence_snippets(
    response,
    response_idx,
    factor_id,
    factor_dir,
    scores,
    features,
    loadings,
):
    from app.analysis.style import score_windows_for_factor

    scores_df = pd.DataFrame.from_records(scores)
    features_df = pd.DataFrame.from_records(features)
    loadings_df = pd.DataFrame.from_records(loadings)

    main_sents = [
        sentence
        for sentence in tokenize_response(response)
        if len(sentence.split()) > 5
    ]

    feature_matrix = features_df.drop(columns=["prompt_key"]).set_index("response_idx").T

    sent_scores = score_windows_for_factor(
        main_sents,
        loadings_df.set_index("feature")[factor_id],
        feature_matrix.mean(axis=1),
        feature_matrix.std(axis=1, ddof=1),
    )

    if factor_dir == "pos":
        sent_scores = sent_scores.clip(lower=0)
    else:
        sent_scores = (-sent_scores).clip(lower=0)

    doc_score = scores_df.loc[
        scores_df.response_idx == str(response_idx),
        factor_id,
    ].iloc[0]

    if not doc_score:
        return []

    picked = pick_evidence_sentence_indices(sent_scores)

    return [main_sents[int(idx)] for idx in picked]

def pick_evidence_sentence_indices(sent_scores, coverage=0.6):
    total_score = float(sent_scores.sum())
    target = coverage * total_score

    picked = []
    cumulative = 0.0

    for idx in sent_scores.sort_values(ascending=False).index:
        score = float(sent_scores.loc[idx])

        if score <= 0:
            continue

        picked.append(idx)
        cumulative += score

        if cumulative >= target:
            break

    return picked

def register_style_click_callback():
    @dash.callback(
        Output("style-details-panel", "children"),
        Input("style-heatmap", "clickData"),
        State("style-heatmap", "figure"),
        State("style-scores-store", "data"),
        State("style-factor-labels-store", "data"),
        State("style-features-store", "data"),
        State("style-loadings-store", "data"),
        State("style-factors-store", "data"),
        State("style-feature-detail-store", "data"),
        State("data-store", "data"),
        State("style-factor-row-meta-store", "data"),
        State("style-col-meta-store", "data"),
        prevent_initial_call=True,
    )
    def _on_style_cell_click(
        clickData,
        fig,
        scores,
        labels,
        features,
        loadings,
        factors,
        feature_detail,
        data,
        row_meta,
        col_meta,
    ):
        if not clickData:
            return no_update

        selection = get_selected_style_cell(clickData, fig, row_meta, col_meta)

        if selection is None:
            return no_update

        factor_id, factor_dir, response_idx = selection

        factor = find_factor(factors, factor_id)

        if factor is None:
            return no_update

        feature_descriptions = get_feature_descriptions(
            factor=factor,
            factor_dir=factor_dir,
            feature_detail=feature_detail,
        )

        label_content = get_factor_label_content(
            labels=labels,
            factor_id=factor_id,
            factor_dir=factor_dir,
        )

        response = data[int(response_idx)]["response"]

        snippets = get_evidence_snippets(
            response=response,
            response_idx=response_idx,
            factor_id=factor_id,
            factor_dir=factor_dir,
            scores=scores,
            features=features,
            loadings=loadings,
        )

        return style_detail_panel(
            factor_dir=factor_dir,
            label_content=label_content,
            feature_descriptions=feature_descriptions,
            response=response,
            snippets=snippets,
        )

    return _on_style_cell_click


register_style_click_callback()
