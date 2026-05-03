
from dash import dcc, html
import dash_mantine_components as dmc

from app.analysis.utils import highlight_text, get_word_cloud


def topic_detail_panel(
    definition,
    topic_info,
    topic_docs,
    response,
    topic_sentences,
):
    return dmc.Accordion(
        value=["topic-info", "response-info"],
        multiple=True,
        children=[
            dmc.AccordionItem(
                value="topic-info",
                children=[
                    dmc.AccordionControl(
                        "Topic Information",
                        style={"fontWeight": 600},
                    ),
                    dmc.AccordionPanel([
                        dmc.Text(definition, fw=400),
                        dmc.Space(h=20),
                        dmc.Image(
                            src=get_word_cloud(topic_info),
                            w="100%",
                            h="auto",
                        ),
                        dmc.Space(h=20),
                        dmc.Text("Representative sentences:", fw=500),
                        html.Ul([
                            html.Li(doc, style={"fontWeight": 400})
                            for doc in topic_docs
                        ]),
                    ]),
                ],
            ),
            dmc.AccordionItem(
                value="response-info",
                children=[
                    dmc.AccordionControl(
                        "Selected Response",
                        style={"fontWeight": 600},
                    ),
                    dmc.AccordionPanel([
                        dcc.Markdown(
                            highlight_text(response, topic_sentences),
                            dangerously_allow_html=True,
                            style={"fontWeight": 400},
                        ),
                    ]),
                ],
            ),
        ],
    )

def style_detail_panel(
    factor_dir,
    label_content,
    feature_descriptions,
    response,
    snippets,
):
    factor_children = []

    if label_content:
        factor_children.extend([
            dmc.Text(
                f"{label_content['label']}: {label_content['description']}",
                fw=400,
            ),
            dmc.Space(h=20),
        ])

    factor_children.append(
        html.Ul([
            html.Li(description, style={"fontWeight": 400})
            for description in feature_descriptions
        ])
    )

    return dmc.Accordion(
        value=["response-info"],
        multiple=True,
        children=[
            dmc.AccordionItem(
                value="pos-info" if factor_dir == "pos" else "neg-info",
                children=[
                    dmc.AccordionControl(
                        "Positive Pole" if factor_dir == "pos" else "Negative Pole",
                        style={"fontWeight": 600},
                    ),
                    dmc.AccordionPanel(factor_children),
                ],
            ),
            dmc.AccordionItem(
                value="response-info",
                children=[
                    dmc.AccordionControl(
                        "Selected Response",
                        style={"fontWeight": 600},
                    ),
                    dmc.AccordionPanel([
                        dcc.Markdown(
                            highlight_text(response, snippets),
                            dangerously_allow_html=True,
                            style={"fontWeight": 400},
                        ),
                    ]),
                ],
            ),
        ],
    )
