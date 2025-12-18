# storage.py
import json
import os
from threading import Lock

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

_lock = Lock()

def _path(filename):
    return os.path.join(DATA_DIR, filename)

def load_json(filename, default):
    path = _path(filename)
    if not os.path.exists(path):
        save_json(filename, default)
        return default
    with _lock, open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(filename, data):
    path = _path(filename)
    with _lock, open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
