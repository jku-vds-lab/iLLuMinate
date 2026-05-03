import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

from app.enums import VariationMode, variation_mode_2_color

def build_heatmap_per_response(frac, col_meta, mode: VariationMode, row_meta=None, title=""):
    x = np.arange(frac.shape[1])
    y = frac.index.tolist()
    y_labels = row_meta["label"].tolist() if row_meta is not None else y

    prompts = col_meta["prompt_key"].astype(str).tolist()
    uniq_prompts = list(dict.fromkeys(prompts))  # stable unique
    prompt_to_code = {p: i for i, p in enumerate(uniq_prompts)}
    codes = [prompt_to_code[p] for p in prompts]

    col_ids = frac.columns.tolist()

    prompt_keys = col_meta.loc[col_ids, "prompt_key"].astype(str).tolist()
    response_idxs = col_meta.loc[col_ids, "response_idx"].tolist()

    customdata = np.zeros((frac.shape[0], frac.shape[1], 3), dtype=object)
    for j in range(frac.shape[1]):
        customdata[:, j, 0] = prompt_keys[j]
        customdata[:, j, 1] = response_idxs[j]
        customdata[:, j, 2] = col_ids[j]

    palette = px.colors.qualitative.Set2
    if len(uniq_prompts) == 1:
        colorscale = [(0.0, palette[0]), (1.0, palette[0])]
    else:
        colorscale = []
        m = max(1, len(uniq_prompts) - 1)
        for p, i in prompt_to_code.items():
            t = i / m
            colorscale.append((t, palette[i % len(palette)]))

    total_height = 20 * frac.shape[0] + 100
    min_small_px = 10
    small_ratio = min_small_px / total_height
    small_ratio = max(small_ratio, 0.01) 

    total_height = 20 * frac.shape[0] + 100
    min_vertical_spacing = 3
    small_ratio_s = min_vertical_spacing / total_height
    small_ratio_s = max(small_ratio_s, 0.005) 

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[small_ratio, 1 - small_ratio],
        vertical_spacing=small_ratio_s,
    )

    fig.add_trace(
        go.Heatmap(
            z=[codes],
            x=x,
            y=["prompt_key"],
            colorscale=[[0, "gainsboro"], [1, "gainsboro"]],
            showscale=False,
            hovertemplate=None,
            customdata=[prompts],
            hoverinfo="none"
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Heatmap(
            z=frac.values,
            x=x,
            y=y_labels,
            zmin=-1 if frac.values.min() < 0 else 0, zmax=1,
            colorbar=dict(title=title),
            customdata=customdata,
            hovertemplate=None,
            hoverinfo="none",
            colorscale=[
                [0, "#e5e5e5"],
                [1, variation_mode_2_color(mode)]
            ]
        ),
        row=2, col=1
    )

    fig.update_xaxes(
        tickmode="array",
        tickvals=x,
        ticktext=frac.columns.tolist(),
        showticklabels=False,
        row=2, col=1
    )
    fig.update_xaxes(showticklabels=False, row=1, col=1)
    fig.update_yaxes(showticklabels=False, row=1, col=1)

    fig.update_yaxes(title_text="", row=1, col=1)
    fig.update_yaxes(title_text="", automargin=True, row=2, col=1)

    boundaries = []
    for i in range(1, len(prompts)):
        if prompts[i] != prompts[i-1]:
            boundaries.append(i - 0.5)

    for b in boundaries:
        fig.add_shape(
            type="line",
            x0=b, x1=b,
            y0=0, y1=1,
            xref="x", yref="paper",
            line=dict(width=3, color="white"),
            name="separator"
        )

    prompt_runs = []
    start = 0
    for i in range(1, len(prompts) + 1):
        if i == len(prompts) or prompts[i] != prompts[i - 1]:
            prompt_runs.append((prompts[i - 1], start, i - 1))
            start = i

    for label, s, e in prompt_runs:
        center = (s + e) / 2 
        fig.add_annotation(
            x=center,
            y="prompt_key",
            xref="x",
            yref="y",
            text=str(label),
            showarrow=False,
            font=dict(size=15, color="black"),
            align="center",
        )

    fig.update_layout(
        height=30 * frac.shape[0] + 100,
        margin=dict(l=120, r=40, t=40, b=40),
        hovermode="x",
        hoverdistance=1,
    )

    return fig

def build_heatmap_per_prompt(frac, mode: VariationMode, row_meta=None, title=""):
    x = np.arange(frac.shape[1])
    y = frac.index.tolist()
    prompts = frac.columns.astype(str).tolist()
    y_labels = row_meta["label"].tolist() if row_meta is not None else y
        
    fig = go.Figure(
        data=go.Heatmap(
            z=frac.values,
            x=x,
            y=y_labels,
            zmin=-1 if frac.values.min() < 0 else 0, zmax=1,
            colorbar=dict(title=title),
            # customdata=customdata,
            hovertemplate=None,
            hoverinfo="none",
            colorscale=[
                [0, "#e5e5e5"],
                [1, variation_mode_2_color(mode)]
            ]
        )
    )

    fig.update_xaxes(
        tickmode="array",
        tickvals=x,
        ticktext=prompts,
        showticklabels=True
    )

    fig.update_yaxes(title_text="", automargin=True)

    fig.update_layout(
        height=20 * frac.shape[0] + 100,
        margin=dict(l=120, r=40, t=40, b=40),
        hovermode="x",
        hoverdistance=1,
    )

    return fig
