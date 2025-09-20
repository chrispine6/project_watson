from pathlib import Path
from typing import List, Dict, Any
from git import Repo, GitCommandError, InvalidGitRepositoryError
from watson.core.index import load_index, save_index, update_project

PROJECTS_ROOT = Path.home() / "stark"

def validate_path(project_path: Path) -> bool:
    """ ensure path is under project root"""
    return project_path.resolve().parent == PROJECTS_ROOT.resolve()

