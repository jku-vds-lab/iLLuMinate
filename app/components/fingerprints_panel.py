import dash_mantine_components as dmc
from dash import html

from app.enums import VariationMode, variation_mode_2_label

def fingerprints_loading(
        var_mode: VariationMode

):
    return dmc.Box(
                    [
                        dmc.LoadingOverlay(
                            id=f"{var_mode.value}-loading-overlay",
                            visible=False,
                            zIndex=10,
                            loaderProps={"type": "dots", "size": "xl"}
                        ),
                        dmc.Center(
                            dmc.Button(
                                f"Generate {variation_mode_2_label(var_mode)} Fingerprints",
                                id=f"run-{var_mode.value}-analysis",
                                variant="gradient",
                                size="xl",
                            ) if var_mode != VariationMode.STYLE else dmc.Group(
                                [
                                    dmc.Button(
                                        f"Generate {variation_mode_2_label(var_mode)} Fingerprints",
                                        id=f"run-{var_mode.value}-analysis",
                                        variant="gradient",
                                        size="xl",
                                    ),
                                    dmc.NumberInput(label="Factors", w=100, value=3, min=1, max=10, id="start-factor-count"),
                                ]
                            ),
                            style={"minHeight": "70vh"},
                        ),
                    ],
                    style={"position": "relative", "minHeight": "70vh"},
                    id=f"temporal-{var_mode.value}-box"
            )

def fingerprints_grid(
    var_mode: VariationMode,
    controls: list = [],
):
    return dmc.Grid(
        id=f"{var_mode.value}-grid",
        style={"display": "none"},
        align="stretch",
        gutter=0,
        children=[
            dmc.GridCol(
                dmc.Stack(
                    [
                        dmc.Group([
                            dmc.Switch(
                                id=f"{var_mode.value}-heatmap-switch",
                                label="Collapse Responses",
                                checked=False,
                                mt=25,
                            ),
                            *controls
                        ], p="1%"),
                        dmc.Box(html.Div(id=f"{var_mode.value}-heatmap-container"), p=0),
                    ],
                    gap="md",
                ),
                span=9,
            ),
            dmc.GridCol(
                id=f"{var_mode.value}-details-panel",
                span=3,
                style={
                    "borderLeft": "2px solid #ddd",
                    "height": "90vh",
                    "overflowY": "auto",
                    "padding": "1rem",
                },
            ),
        ],
    )

def fingerprints_panel(
    var_mode: VariationMode,
    controls: list = [],
):
    return dmc.TabsPanel([
        fingerprints_loading(var_mode),
        fingerprints_grid(var_mode, controls)
    ], value=var_mode.value, px=0)
