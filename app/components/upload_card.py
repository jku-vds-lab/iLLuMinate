from dash import dcc
import dash_iconify
import dash_mantine_components as dmc


def upload_card(upload_id: str, filename_id: str):
    return dmc.Paper(
        shadow=False,
        radius="md",
        p="xs",
        withBorder=True,
        style={
            "borderStyle": "dashed",
            "borderWidth": "3px",
            "cursor": "pointer",
            "backgroundColor": "#f7fcfd",
        },
        children=[
            dcc.Upload(
                id=upload_id,
                children=dmc.Stack(
                    [
                        dash_iconify.DashIconify(icon="material-symbols:cloud-upload", color="#9ce5eb", width=30),
                        dmc.Button("Select CSV", variant="gradient"),
                        dmc.Text("Or drag & drop you CSV here", c="grey", fw=700),
                        dmc.Text("Supports CSV with columns: comp_key, response", c="dimmed"),
                    ],
                    align="center", gap=7, p=0
                ),
                multiple=False, 
            ),
            dmc.Text(id=filename_id, c="dimmed", size="sm")
        ]
    )
