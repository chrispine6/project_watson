"""
handle json crud for the project index
"""

import json
import os
from pathlib import Path
from typing import  List, Dict, Any

INDEX_PATH = Path.home() / "stark" / "watson" / "projects.json"

def ensure_index_dir():
    INDEX_PATH.parent.mkdir(exist_ok=True)

def load_index() -> Dict[str, Any]:
    ensure_index_dir()
    if INDEX_PATH.exists():
        with open(INDEX_PATH, 'r') as f:
            return json.load(f)
    return {"version": "1.0", "projects": []}

def save_index(data: Dict[str, Any]):
    ensure_index_dir()
    with open(INDEX_PATH, 'w') as f:
        json.dump(data, f, indent=2)

def update_project(name: str, updates: Dict[str, Any]):
    index = load_index()
    for proj in index["projects"]:
        if proj["name"] == name:
            proj.update(updates)
            save_index(index)
            return True
    return False

def add_project(project: Dict[str, Any]):
    index = load_index()
    index["projects"].append(project)
    save_index(index)

print(load_index())
