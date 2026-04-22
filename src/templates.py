from pathlib import Path

from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader


SRC_DIR = Path(__file__).resolve().parent


def _discover_dirs(folder_name: str) -> list[str]:
    dirs: list[str] = []

    shared_dir = SRC_DIR / folder_name
    if shared_dir.exists():
        dirs.append(str(shared_dir))

    for path in sorted(SRC_DIR.iterdir()):
        candidate = path / folder_name
        if path.is_dir() and candidate.exists():
            dirs.append(str(candidate))

    return dirs


page_loader = FileSystemLoader(_discover_dirs("templates"))
page_env = Environment(loader=page_loader)
templates = Jinja2Templates(env=page_env)
