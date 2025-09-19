import os
from pathlib import Path
from git import Repo, InvalidGitRepositoryError
from watson.core.index import add_project, save_index

PROJECTS_ROOT = Path.home() / "stark"
INDEX_PATH = PROJECTS_ROOT / ".watson" / "projects.json"

def guess_title(path: Path) -> str:
    readme = path / "README.md"
    if readme.exists():
        with open(readme, 'r') as f:
            return f.read().splitlines()[0].strip('# \n')  # First non-empty line as title
    return path.name.title()  # Fallback to dir name

def scan_projects():
    index = {"version": "1.0", "projects": []}
    if INDEX_PATH.exists():
        import json
        with open(INDEX_PATH, 'r') as f:
            index = json.load(f)

    # Clear existing to rescan
    index["projects"] = []

    for item in PROJECTS_ROOT.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            is_git = False
            last_commit = None
            try:
                repo = Repo(item)
                is_git = True
                last_commit = repo.head.commit.committed_datetime.isoformat() if repo.head else None
            except InvalidGitRepositoryError:
                pass

            proj = {
                "name": item.name,
                "title": guess_title(item),
                "description": "Auto-generated; edit in index",  # TODO: Enhance later
                "status": "active",
                "path": str(item.absolute()),
                "is_git": is_git,
                "last_commit": last_commit,
                "last_change_summary": None
            }
            index["projects"].append(proj)

    save_index(index)
    print(f"Scanned {len(index['projects'])} projects into {INDEX_PATH}")

if __name__ == "__main__":
    scan_projects()
