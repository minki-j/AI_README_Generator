from fasthtml.common import *

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
    