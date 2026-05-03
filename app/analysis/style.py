import pandas as pd
import polars as pl
import numpy as np

import pybiber as pb

from .labeling import label_factors
from app.analysis.utils import get_root_path, postprocess_heatmap_matrix

def get_style_features(data):
    prompts = [r['prompt_key'] for r in data]
    df = pl.DataFrame([{
            "doc_id": str(i),
            "text": record['response']
        }
        for i, record in enumerate(data)
    ])

    pipeline = pb.PybiberPipeline(model="en_core_web_sm")
    features = pipeline.run(df)
    features = features.sort(pl.col("doc_id").cast(pl.Int64))
    features = features.with_columns(
        pl.Series("prompt_key", prompts)
    )
    features = features.rename({"doc_id": "response_idx"})

    return features

def compute_saliency_mask(loadings, threshold=0.35):
    factor_cols = [c for c in loadings.columns if c.startswith("factor_")]

    abs_load = loadings[factor_cols].abs()

    keep = abs_load.gt(threshold)

    masked = loadings.copy()
    masked[factor_cols] = loadings[factor_cols].where(keep, other=0)

    has_any = keep.any(axis=1)
    masked = masked.loc[has_any].copy()

    return masked

def token_windows(text, win=60, stride=40):
    words = text.split()
    n = len(words)

    if n <= win:
        return [text]

    windows = []
    for start in range(0, n - win + 1, stride):
        end = start + win
        windows.append(" ".join(words[start:end]))

    return windows

def score_windows_for_factor(
        window_texts: list[str],
        factor_loadings,
        corpus_mean,
        corpus_std
    ):
    df = pl.DataFrame([{
            "doc_id": str(i),
            "text": txt
        }
        for i, txt in enumerate(window_texts)
    ])
    pipeline = pb.PybiberPipeline(model="en_core_web_sm")
    feats = pipeline.run(df).to_pandas().set_index('doc_id')

    cols = factor_loadings.index
    X = feats.reindex(columns=cols).fillna(0.0)
    Z = (X - corpus_mean.reindex(cols)) / corpus_std.reindex(cols).replace(0, np.nan)
    Z = Z.replace([np.inf, -np.inf], np.nan).fillna(0.0)

    pos_features = factor_loadings[factor_loadings > 0.35].index
    neg_features = factor_loadings.loc[factor_loadings < -0.35].index
    pos_score = Z[pos_features].sum(axis=1) if len(pos_features) else 0
    neg_score = Z[neg_features].sum(axis=1) if len(neg_features) else 0

    return pos_score - neg_score

def representative_snippets(
        texts,
        doc_factor_scores,
        loadings,
        mu,
        sigma,
        factor,
        ascending=False,
        top_docs = 5,
        win_tokens = 60,
        stride_tokens = 40,
        top_k_windows = 5,
    ):
    top_doc_ids = doc_factor_scores[factor].sort_values(ascending=ascending).head(top_docs).index.tolist()

    rows = []
    all_windows = []
    for doc_id in top_doc_ids:
        w = token_windows(texts[doc_id], win=win_tokens, stride=stride_tokens)
        for j, wtext in enumerate(w):
            rows.append((doc_id, j, wtext))
            all_windows.append(wtext)

    if not all_windows:
        return pd.DataFrame(columns=["factor", "doc_id", "window_id", "window_score", "doc_factor_score", "window_text"])

    w_scores = score_windows_for_factor(all_windows, loadings[factor], mu, sigma)

    out = pd.DataFrame(rows, columns=["doc_id", "window_id", "window_text"])
    out["window_score"] = w_scores.values
    out["doc_factor_score"] = out["doc_id"].map(doc_factor_scores[factor].to_dict())
    out["factor"] = factor

    out = out.sort_values("window_score", ascending=ascending).head(top_k_windows).reset_index(drop=True)
    return out

def build_factor_features_map(masked, data, loadings, scores, features, n_factors=4):
    biber_features = pd.read_csv(f'{get_root_path().parent}/data/features.csv')

    features_ = features.drop(columns=['prompt_key']).set_index('response_idx').T
    corpus_mean = features_.mean(axis=1)
    corpus_std = features_.std(axis=1, ddof=1)
    zero_var_cols = corpus_std[corpus_std < 1e-12].index.tolist()
    if zero_var_cols:
        corpus_std.loc[zero_var_cols] = 1.0

    def get_feature(feature_name, feature_score):
        feature = biber_features[biber_features.Feature == feature_name]
        return {"feature": feature.Feature.values[0],
                "description": feature.Description.values[0],
                 "category": feature.Category.values[0], 
                 "score": round(feature_score, 2)}
    factors = []
    for id in range(1, n_factors + 1):
        pos, neg = [], []
        for _, r in masked[['feature', f"factor_{id}"]][masked[f"factor_{id}"] > 0].iterrows():
            pos.append(get_feature(r["feature"], r[f"factor_{id}"]))
        for _, r in masked[['feature', f"factor_{id}"]][masked[f"factor_{id}"] < 0].iterrows():
            neg.append(get_feature(r["feature"], r[f"factor_{id}"]))

        pos_examples, neg_examples = [], []
        if pos:
            pos_examples = representative_snippets(
                {str(i): r['response'] for i, r in enumerate(data)},
                scores.set_index('response_idx'),
                loadings[['feature', f"factor_{id}"]].set_index('feature'),
                corpus_mean,
                corpus_std,
                f"factor_{id}"
            )
        if neg:
            neg_examples = representative_snippets(
                {str(i): r['response'] for i, r in enumerate(data)},
                scores.set_index('response_idx'),
                loadings[['feature', f"factor_{id}"]].set_index('feature'),
                corpus_mean,
                corpus_std,
                f"factor_{id}",
                ascending=True
            )

        factors.append({
            "factor_id": f"factor_{id}",
            "pos": {
                "features": pos,
                "examples": pos_examples.window_text.to_list()
            } if pos else {},
            "neg": {
                "features": neg,
                "examples": neg_examples.window_text.to_list()
            } if neg else {}
        })
    return factors, biber_features

def decompose_poles(scores, factors):
    out = scores.copy()
    cols_to_drop = []

    for f in factors:
        fid = f["factor_id"]

        s = out[fid]

        has_pos = len(f.get("pos", [])) > 0
        has_neg = len(f.get("neg", [])) > 0

        if has_pos and has_neg:
            out[f"{fid}_pos"] = s.clip(lower=0)
            out[f"{fid}_neg"] = (-s).clip(lower=0)
            cols_to_drop.append(fid)

        elif has_pos:
            out[fid] = s.clip(lower=0)

        elif has_neg:
            out[fid] = (-s).clip(lower=0)

    if cols_to_drop:
        out = out.drop(columns=cols_to_drop)

    return out

def biber_analysis_pipeline(data, n_factors=4, with_labels=False):
    features = get_style_features(data)
    analyzer = pb.BiberAnalyzer(features, id_column=True)
    mda_results = analyzer.mda(n_factors=n_factors)

    loadings = analyzer.mda_loadings.to_pandas()
    scores = analyzer.mda_dim_scores
    scores = scores.rename({"doc_id": "response_idx", "doc_cat": "prompt_key"}).to_pandas()

    saliency_mask = compute_saliency_mask(loadings)
    factors, feature_detail = build_factor_features_map(saliency_mask, data, loadings, scores, features.to_pandas(), n_factors=n_factors)
    decomposed_scores = decompose_poles(scores, factors)

    labels = label_factors(factors) if with_labels else None

    return features.to_pandas(), loadings, scores, decomposed_scores, factors, feature_detail, labels

def compute_style_matrix(scores, bipolar=False, per_prompt=False, labels=None):
    norm_scores = scores.copy()

    f_cols = [c for c in norm_scores.columns if c.startswith("factor")]
    mins = norm_scores[f_cols].min()
    maxs = norm_scores[f_cols].max()
    denom = (maxs - mins).where((maxs - mins) != 0, 1)

    scaled = (norm_scores[f_cols] - mins).div(denom)

    norm_scores[f_cols] = 2 * scaled - 1 if bipolar else scaled

    norm_scores = norm_scores.set_index(["prompt_key", "response_idx"]).T

    row_meta = None

    matrix, col_meta =postprocess_heatmap_matrix(
        norm_scores,
        per_prompt=per_prompt
    )

    if labels:
        row_meta = pd.DataFrame({
            "id": matrix.index,
            "label": [labels[id]["label"] for id in matrix.index],
            "description": [labels[id]["description"] for id in matrix.index],
        }).set_index("id")

    return matrix, col_meta, row_meta
