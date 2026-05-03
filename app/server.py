from dash import Dash

def create_app() -> Dash:
    app = Dash(
        __name__,
        use_pages=True,                   
        suppress_callback_exceptions=True 
    )
    app.title = "iLLuMinate"
    return app

app = create_app()

server = app.server
