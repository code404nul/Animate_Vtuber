from json import load

with open('config.json', 'r') as f:
    _config = load(f)

def size_stt():
    return _config["size_stt"]

def language():
    return _config["language"]

def device():
    return _config["device"]
