from modal import App, Image, Volume

app = App("WriteMeReadMe_app")

image = (
    Image.debian_slim(python_version="3.12.2")
    .pip_install(
        "python_fasthtml",
    )
)

vol = Volume.from_name("WriteMeReadMe")
