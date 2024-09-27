from fasthtml.common import *

readme_sections = [
    ("Project Title", "Brief name or heading of the project."),
    ("Description", "Overview of the project, including its purpose and key features."),
    (
        "Table of Contents",
        "A list of links or sections that users can easily navigate to within the README file.",
    ),
    (
        "Installation",
        "Instructions on how to install or set up the project locally, including dependencies or environment setup.",
    ),
    (
        "Usage",
        "How to use the project, with example commands, code snippets, or expected outcomes.",
    ),
    (
        "Configuration",
        "Optional settings or configurations that users can adjust to customize the project.",
    ),
    ("Features", "List of major functionalities or features of the project."),
    (
        "Screenshots / Demos",
        "Visual examples or demonstrations of the project in action.",
    ),
    (
        "Contributing",
        "Guidelines for those who want to contribute to the project, such as pull request instructions or code style rules.",
    ),
    (
        "Testing",
        "Information about how to run the tests and ensure that the project works as intended.",
    ),
    ("Roadmap", "Future plans for development, features, or improvements."),
    (
        "License",
        "The type of open-source license the project is distributed under (e.g., MIT, GPL).",
    ),
    (
        "Acknowledgments",
        "A section to thank contributors, libraries, or any other resources the project depends on.",
    ),
    ("FAQ", "Frequently Asked Questions to address common concerns or issues."),
    (
        "Contact",
        "Information for users or developers to reach out with questions or issues.",
    ),
    ("Changelog", "List of major updates or version history."),
    ("Authors", "List of people who created or contributed to the project."),
    ("Support", "Information on how to get support or report bugs."),
    (
        "Dependencies",
        "A list of external libraries, frameworks, or tools required for the project.",
    ),
    (
        "Build With",
        "Tools, technologies, or frameworks used in the project (e.g., React, Node.js).",
    ),
]


def subtitle_selector(options: list[tuple[str, str]] = readme_sections):
    options = [
        Li(
            class_="subtitle-option",
            style="list-style-type: none; margin-left: 0;",
        )(
            Label(class_="subtitle-label", style="display: flex; align-items: flex-start;")(
                Input(
                    type="radio",
                    name="readme_subtitle",
                    value=title,
                    class_="subtitle-input",
                ),
                Span(class_="subtitle-title", style="margin-left: 5px; font-weight: bold;")(title),
                Span(class_="subtitle-description", style="margin-left: 5px;")(description),
            )
        )
        for title, description in options
    ]
    return Ul(
        id="readme_subtitle_selector",
        class_="subtitle-selector",
        style="padding-left: 0;",
    )(*options)