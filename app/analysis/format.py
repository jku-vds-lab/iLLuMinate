from collections import Counter
from markdown_it import MarkdownIt
import pandas as pd

from app.analysis.utils import postprocess_heatmap_matrix


def md_format_stats(text: str) -> dict:
    md = MarkdownIt("gfm-like")
    tokens = md.parse(text)

    counts = Counter()

    def walk(ts):
        for t in ts:
            yield t
            if t.children:
                yield from walk(t.children)

    for t in walk(tokens):
        # Headings
        if t.type == "heading_open":
            # counts["headings"] += 1
            counts[t.tag] += 1  # h1..h6

        # Lists
        elif t.type in ("bullet_list_open", "ordered_list_open"):
            counts["bullet_lists" if t.type == "bullet_list_open" else "ordered_lists"] += 1

        # Tables
        elif t.type == "table_open":
            counts["tables"] += 1

        # Code
        elif t.type == "fence":
            counts["fenced_code_blocks"] += 1
        elif t.type == "code_block":
            counts["indented_code_blocks"] += 1
        elif t.type == "code_inline":
            counts["inline_code"] += 1

        # Quotes / rules
        elif t.type == "blockquote_open":
            counts["blockquotes"] += 1
        elif t.type == "hr":
            counts["horizontal_rules"] += 1

        # Links / images
        elif t.type == "link_open":
            counts["links"] += 1

        # Emphasis
        elif t.type == "strong_open":
            counts["strong"] += 1
        elif t.type == "em_open":
            counts["emphasis"] += 1

        # HTML
        elif t.type == "html_block":
            counts["html_blocks"] += 1
        elif t.type == "html_inline":
            counts["html_inline"] += 1

    return dict(counts)

def get_format_stats(data):
    all_stats = []
    for i, r in enumerate(data):
        stats = md_format_stats(r["response"])
        stats["comp_key"] = r["comp_key"]
        stats["response_idx"] = i
        all_stats.append(stats)
    format_df = pd.DataFrame.from_records(all_stats).fillna(0)
    return format_df

def compute_format_matrix(stats, per_prompt=False):
    norm_scores = stats.copy()

    f_cols = [
        c for c in norm_scores.columns
        if c not in ("comp_key", "response_idx")
    ]

    mins = norm_scores[f_cols].min()
    maxs = norm_scores[f_cols].max()
    denom = (maxs - mins).where((maxs - mins) != 0, 1)

    norm_scores[f_cols] = (norm_scores[f_cols] - mins).div(denom)

    norm_scores = norm_scores.set_index(["comp_key", "response_idx"]).T

    matrix, col_meta = postprocess_heatmap_matrix(
        norm_scores,
        per_prompt=per_prompt
    )
    return matrix, col_meta
