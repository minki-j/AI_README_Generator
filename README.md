# WriteMeReadMe

To run locally:
```bash
export $(grep -v '^#' .env | xargs)
uvicorn app.fasthtml_app:app --reload
```

To deploy the web server:
```bash
modal deploy app.modal_app
```
