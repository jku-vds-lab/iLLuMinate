import base64
import io
import dash_iconify
import pandas as pd
import dash
from dash import html, dcc, Input, Output, State, no_update
import dash_mantine_components as dmc

from app.components.upload_card import upload_card
from app.components.experiments_gallery import experiment_gallery

dash.register_page(__name__, path="/")

DATA = [
    {
        "title": "Audeince Adaptation",
        "description": "How would GPT-4o trailor its AI explanation to different educational levels?",
    },
    {
        "title": "Prompt Politeness",
        "description": "The impact of prompt politeness on Llamma's response to one philosophical question?",
    },
    {
        "title": "Persona Impact",
        "description": "The impact of persona-based preassumptions on GPT-3.5's response to a physical question.",
    },
    {
        "title": "Human vs. LLM",
        "description": "Comparing Human style in storytelling with GPT-4o and GPT-3.5 under one prompt.",
    },
    {
        "title": "Advice Giving",
        "description": "How do different LLMs give advice?",
    }
]

def layout():
    return dmc.Center(
            style={"minHeight": "100vh", "padding": "clamp(12px, 2vw, 40px)"},
            children=[
                html.Div(
                    style={
                        "width": "100%",
                        "maxWidth": "2200px",
                        "overflow": "hidden",   
                    },
                    children=[
                        html.Div(
                            style={
                                "display": "flex",
                                "flexWrap": "nowrap",          
                                "alignItems": "center",
                                "justifyContent": "center",
                                "gap": "clamp(12px, 2.5vw, 64px)",
                                "width": "100%",
                            },
                            children=[
                                html.Div(
                                    style={
                                        "flex": "45 45 0",        
                                        "minWidth": 0,            
                                        "display": "flex",
                                        "justifyContent": "center",
                                        "alignItems": "center",
                                    },
                                    children=[
                                        dmc.Image(
                                            src="/assets/parrot.png",
                                            alt="Illustration",
                                            fit="contain",
                                            style={
                                                "width": "100%",
                                                "height": "auto",
                                                "maxWidth": "min(900px, 40vw)",
                                            },
                                        )
                                    ],
                                ),
                                html.Div(
                                    style={
                                        "flex": "55 55 0",        
                                        "minWidth": 0,           
                                    },
                                    children=[
                                        dmc.Stack(
                                            gap="md",
                                            style={"minWidth": 0},
                                            children=[
                                                dmc.Title(
                                                    "Visual Fingerprints for LLM Generation Comparison",
                                                    c="#1e94db",
                                                    order=1,
                                                    style={
                                                        "fontSize": "clamp(22px, 2.8vw, 64px)",
                                                        "lineHeight": 1.1,
                                                    },
                                                ),
                                                dmc.Text(
                                                    "Creating visual fingerprints to compare open-ended LLM output under different generation conditions.",
                                                    c="dimmed",
                                                    style={"fontSize": "clamp(14px, 1.2vw, 22px)"},
                                                ),
                                                dmc.Text("Select a dataset", fw=700, style={"textAlign": "center"}),

                                                html.Div(
                                                    style={
                                                        "overflowX": "auto",
                                                        "paddingBottom": "6px",
                                                    },
                                                    children=[
                                                        experiment_gallery(DATA)
                                                    ],
                                                ),

                                                dmc.Text("Or upload your own CSV", fw=700, c="#17a6c5", style={"textAlign": "center"}),
                                                upload_card("upload-csv", "upload-filename"),
                                                dmc.Card(
                                                    id="preview-card",      
                                                    shadow="sm",
                                                    style={"display": "none"},
                                                    children=[
                                                        html.Div(id="preview-table"),
                                                        dmc.Space(h="sm"),
                                                        dmc.Button(
                                                            "Confirm",
                                                            variant="gradient",
                                                            fullWidth=True,
                                                            id="confirm-dataset",
                                                            rightSection=dash_iconify.DashIconify(icon="material-symbols:arrow-forward-ios", width=20),
                                                        )
                                                ])
                                            ],
                                        )
                                    ],
                                ),
                            ],
                        )
                    ],
                )
            ],
        )

@dash.callback(
    Output("data-store", "data"),
    Output("preview-card", "style"),
    Output("preview-table", "children"),
    Input("upload-csv", "contents"),
    State("upload-filename", "filename"),
    prevent_initial_call=True,
)
def handle_upload(contents, filename):
    if not contents:
        return no_update, no_update, no_update
    
    content_type, content_string = contents.split(",", 1)
    decoded = base64.b64decode(content_string)

    df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))

    preview = df.head(10)

    preview_subset = preview.reindex(columns=["comp_key", "response"], fill_value="")
    table = dmc.Table(
        striped=True,
        highlightOnHover=True,
        withTableBorder=True,
        withColumnBorders=True,
        data={
            "head": ["comp_key", "response"],
            "body": preview_subset.values.tolist(),
        },
    )


    return (
        df.to_dict("records"),
        {"display": "block"},
        table,
    )

@dash.callback(
    Output("url", "pathname"),
    Input("confirm-dataset", "n_clicks"),
    prevent_initial_call=True,
)
def go_to_analysis(n_clicks):
    if not dash.ctx.triggered_id: 
        return no_update

    if n_clicks and n_clicks > 0:
        return "/vis"

    return no_update
