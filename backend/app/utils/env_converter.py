import os 

def env_converter(dotenv_directory: str):
    dotenv_path = os.path.join(dotenv_directory, ".env")
    env_dict = {}

    with open(dotenv_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key, value = line.split("=")
                env_dict[key] = value

    return env_dict
