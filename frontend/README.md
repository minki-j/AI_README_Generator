# Front-End

FastHTML on Modal Labs

To run locally:
```bash
cd frontend
export $(grep -v '^#' .env | xargs)
cd app
uvicorn fasthtml_app:app --reload
```

To deploy the web server:
```bash
modal deploy app.main
```
