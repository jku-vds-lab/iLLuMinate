from dash import dcc, page_container
import dash_mantine_components as dmc

from .server import app

app.layout = dmc.MantineProvider(
    children=dmc.Box(
        [
            dcc.Location(id="url"),
            dcc.Store(id="data-store", storage_type="session"),
            dcc.Store(id="data-topic-store", storage_type="session"),
            dcc.Store(id="topic-store", storage_type="session"),
            dcc.Store(id="topic-docs-store", storage_type="session"),
            dcc.Store(id="topic-labels-store", storage_type="session"),
            dcc.Store(id="topic-row-meta-store", storage_type="session"),
            dcc.Store(id="topic-col-meta-store", storage_type="session"),
            dcc.Store(id="style-features-store", storage_type="session"),
            dcc.Store(id="style-loadings-store", storage_type="session"),
            dcc.Store(id="style-scores-store", storage_type="session"),
            dcc.Store(id="style-decomposed-scores-store", storage_type="session"),
            dcc.Store(id="style-factors-store", storage_type="session"),
            dcc.Store(id="style-factor-labels-store", storage_type="session"),
            dcc.Store(id="style-factor-row-meta-store", storage_type="session"),
            dcc.Store(id="style-feature-detail-store", storage_type="session"),
            dcc.Store(id="selected-topic-store", storage_type="session"),
            dcc.Store(id="format-stats-store", storage_type="session"),
            dcc.Store(id="format-col-meta-store", storage_type="session"),
            dcc.Store(id="style-col-meta-store", storage_type="session"),

            page_container,
            
            dmc.Affix(
                dmc.Image(src="/assets/logo.png", style={"maxWidth": "10vw"}, h="auto"), position={"top": 20, "right": 20}
            ),
        ],
    )
)

if __name__ == "__main__":
    app.run(debug=True)
