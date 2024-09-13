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

input_pattern_error = Style(
    """
    input:valid {
        background-color: #e8f5e9;  /* Light pastel green */
    }

    input:invalid {
        background-color: #ffebee;  /* Light pastel red */
    }
    """
)
