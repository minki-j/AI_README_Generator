from fasthtml.common import *

gridlink = (
    Link(
        rel="stylesheet",
        href="https://cdnjs.cloudflare.com/ajax/libs/flexboxgrid/6.3.1/flexboxgrid.min.css",
        type="text/css",
    ),
)

loader_css = Style(
    """
    .my-indicator{
        display:none;
    }
    .htmx-request .my-indicator{
        display:inline;
    }
    .htmx-request.my-indicator{
        display:inline;
    }
    .bordered-container {
        border: 1px solid #000;
        border-radius: 4px;
        padding: 16px;
    }

                   """
)
