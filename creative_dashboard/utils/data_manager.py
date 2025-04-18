import json
import os

DATA_FILE = "data/data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "projects": [],
            "rewards": [],
            "current_week": 1
        }

    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {
                "projects": [],
                "rewards": [],
                "current_week": 1
            }

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
