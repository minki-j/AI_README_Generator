# WriteMeReadMe

To build the Docker image (terminal at the workdir):
```bash
docker build -t readmegen .
```

To run the container:
```bash
docker run -p 8000:8000 readmegen
```

<br>You can access to the web server at http://localhost:8000/ </br>

To run locally:
```bash
export $(grep -v '^#' .env | xargs)
uvicorn app.fasthtml_app:app --reload
```

To deploy the web server:
```bash
modal deploy app.modal_app
```
