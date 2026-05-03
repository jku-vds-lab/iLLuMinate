def get_heatmap_cell_indices(clickData, fig, main_idx=1):
    if not clickData:
        return None

    pt = clickData["points"][0]

    if pt.get("curveNumber") != main_idx:
        return None

    main_trace = fig["data"][main_idx]

    row_label = pt.get("y")
    y_labels = main_trace.get("y", []) or []

    if row_label not in y_labels:
        return None

    row_idx = y_labels.index(row_label)
    col_idx = pt.get("x")

    return row_idx, col_idx
