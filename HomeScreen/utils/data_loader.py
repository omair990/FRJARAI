import json

def load_materials(path):
    with open(path, "r") as f:
        data = json.load(f)
    return data["materials"]
