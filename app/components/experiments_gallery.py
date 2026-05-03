import dash_iconify
import dash_mantine_components as dmc

def make_experiment_card(title, description):
    return dmc.Card(
        withBorder=True,
        shadow="sm",
        radius="md",
        p="lg",
        children=[
            dmc.Stack(
                [
                    dmc.Group(
                        [
                            dash_iconify.DashIconify(
                                icon="material-symbols:insights",
                                color="#17a6c5",
                                # width=48,  # bigger base icon
                                style={
                                    "width": "clamp(20px, 3vw, 40px)",
                                    "height": "auto"
                                },
                            ),
                            dmc.Text(
                                title,
                                fw=700,
                                c="grey"
                            ),
                        ],
                        gap="xs",
                        justify="left",
                        # wrap="nowrap",
                    ),
                    dmc.Text(
                        description,
                        c="dimmed",
                        ta="left",
                    ),
                ],
                gap=0,
                align="left",
                justify="left",
            ),
            dmc.Space(h="sm"),
            dmc.Button(
                "Select",
                # color="blue",
                fullWidth=True,
                variant="gradient",
                size="md",
                rightSection=dash_iconify.DashIconify(icon="material-symbols:arrow-forward-ios", width=20),
            ),
        ],
    )

def experiment_gallery(data):
    cards = [make_experiment_card(d["title"], d["description"]) for d in data]

    return dmc.Carousel(
        [
            dmc.CarouselSlide(
                    card,
            )
            for card in cards
        ],
        slideSize={"base": "100%", "md": "50%"},
        slideGap=10,
        emblaOptions={"loop": True, "align": "center"},
        withIndicators=True,
        
    )
