import base64
from io import BytesIO
from pathlib import Path

import pandas as pd

from wordcloud import WordCloud

from scipy.cluster.hierarchy import linkage, leaves_list
from scipy.spatial.distance import pdist

def cluster_order(mat, metric="euclidean", method="average"):
    Z = linkage(pdist(mat, metric=metric), method=method)
    return leaves_list(Z)

def postprocess_heatmap_matrix(matrix, per_prompt=False, row_meta=None):
    if per_prompt:
        matrix = (
            matrix.T
                .groupby(level="comp_key", sort=False)
                .mean()
                .T
        )
        col_meta = None
    else:
        col_meta = pd.DataFrame({
            "comp_key": [c[0] for c in matrix.columns],
            "response_idx": [c[1] for c in matrix.columns],
        })

        col_ids = [f"r{i:03d}" for i in range(matrix.shape[1])]
        col_meta.index = col_ids
        matrix.columns = col_ids

        ordered_cols = []

        for comp_key, meta_sub in col_meta.groupby("comp_key", sort=False):
            cols = meta_sub.index.tolist()
            sub_order = cluster_order(matrix[cols].values.T)
            ordered_cols.extend([cols[i] for i in sub_order])

        matrix = matrix[ordered_cols]
        col_meta = col_meta.loc[ordered_cols]

    matrix = matrix.iloc[cluster_order(matrix.values), :]

    return matrix, col_meta

def highlight_text(text, sentences):
    for sen in sentences:
        text = text.replace(sen, f"<mark>{sen}</mark>")
    return text

def get_word_cloud(topic):
    freqs = dict(topic)

    wc = WordCloud(width=900, height=450, background_color="white", random_state=42)
    wc = wc.generate_from_frequencies(freqs)

    buf = BytesIO()
    wc.to_image().save(buf, format="PNG")
    encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"

def get_root_path():
    return Path(__file__).resolve().parent.parent

