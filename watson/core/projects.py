from pathlib import Path
import os
from typing import List, Dict, Any
from git import Repo, GitCommandError, InvalidGitRepositoryError
from github import Github, Auth, GithubException
from watson.core.index import load_index, save_index, add_project, update_project

PROJECTS_ROOT = Path.home() / "stark"

def validate_path(project_path: Path) -> bool:
    """ ensure path is under project root"""
    return project_path.resolve().parent == PROJECTS_ROOT.resolve()


def list_projects(filter_status: str = 'all') -> List[Dict[str, Any]]:
    index = load_index()
    if filter_status == "all":
        return index["projects"]
    return [p for p in index["projects"] if p["status"] == filter_status]

print(list_projects('active'))

def get_status(project_name: str) -> str:
    index = load_index()
    proj = next((p for p in index["projects"] if p["name"] == project_name), None)
    if not proj:
        return "project not found"
    path = Path(proj["path"])
    if not validate_path(path):
        return "invalid project path"
    status = f"project: {proj['title']} ({proj['status']})\nDescription: {proj['description']}\n"
    if proj['is_git']:
        try:
            repo = Repo(path)
            commits = repo.git.log('--oneline', '-5') # last 5 commits
            status += f"last commits:\n{commits}\n"
            last_commit = repo.head.commit.committed_datetime.isoformat()
            last_summary = repo.head.commit.summary
            update_project(project_name, {'last_commit': last_commit, 'last_change_summary': last_summary})
        except GitCommandError as e:
            status += f"git error: {str(e)}\n"
    else:
        status += "not a git repository; last changes unknown\n"
    return status
print(get_status('project_watson'))

def create_project(title: str, description: str = "", use_git: bool = True, name: str = None, create_github: bool = False) -> str:
    if not name:
        name = title.lower().replace(' ', '-')

    path = PROJECTS_ROOT / name
    if path.exists():
        return "project directory already exists"

    if not validate_path(path):
        return "invalid project path"

    path.mkdir(parents=True, exist_ok=False)

    is_git = False
    repo = None
    if use_git:
        try:
            repo = Repo.init(path)
            is_git = True
        except GitCommandError as e:
            return f"git init error: {str(e)}"

    if create_github and is_git:
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            return "github access token not set in env"
        try:
            auth = Auth.Token(token)
            gh = Github(auth=auth)
            user = gh.get_user()
            remote_repo = user.create_repo(name, description = description or "watson managed project", private=True)
            repo.create_remote('origin', remote_repo.clone_url)

            # initial commit- add readme
            readme_path = path / "README.md"
            with open(readme_path, 'w') as f:
                f.write(f"# {title}\n\n{description or 'no description'}\n")
            repo.index.add(['README.md'])
            repo.index.commit("initial commit by watson")
            
            # Get the current branch name and push to it
            current_branch = repo.active_branch.name
            repo.git.push('origin', current_branch)

            print(f"created git repo: {remote_repo.html_url}")
        except GithubException as e:
            return f"github repo creation error: {str(e)}"
    proj = {
        "name": name,
        "title": title,
        "description": description or "no description",
        "path": str(path.absolute()),
        "status": "active",
        "is_git": is_git,
        "last_commit": None,
        "last_change_summary": None
    }
    add_project(proj)
    return f"Created project '{name}' at {path}. Git: {is_git}"

# print(create_project("New Test App 9", description="Testing create", use_git=True, create_github=True))

