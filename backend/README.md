# Back-end Server for WriteMeReadMe application. 

### This server is running on Modal Labs["https://modal.com"]

To run the server locally:
```bash
modal serve app.main
```

To deploy the server:
```bash
modal deploy app.main
```

To run the agent without running a server:
```bash
python run_graph_locally.py
```


When new packages are added, you need to add that in the image method .pip_install() of the file app/common.py