from modal import App, Image, Volume

app = App("frontend_ai-readme-generator")

image = Image.debian_slim(python_version="3.12.2").pip_install(
    "python_fasthtml", "requests"
)

main_vol = Volume.from_name("main")
