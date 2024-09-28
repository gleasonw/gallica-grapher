from fasthtml.common import serve, fast_app, Div, P, Ul
from fasthtml import ft
from gallica.main import fetch_records_from_gallica
from gallica.models import ContextSearchArgs

app, rt = fast_app()


@rt("/")
async def get():
    test = await fetch_records_from_gallica(ContextSearchArgs(terms=["brazza"]))
    if test is None:
        return Div(P("No results"))

    return Div(
        Ul(
            ft.Li(test.records[0].context[0].right_context),
        ),
        Div(P("Hello there"), hx_get="/change"),
    )


serve()
