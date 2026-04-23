from pathlib import Path

from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader


SRC_DIR = Path(__file__).resolve().parent


# --------------- TEMPLATE DIRECTORY AUTO-DETECTION
def _discover_dirs(folder_name: str) -> list[str]:
    """
    Search the source directory and its immediate subdirectories for matching folder_name.

    Args:
        folder_name (str): Name of the folder to search for.

    Returns:
        list[str]: List of matching directory paths.

    Example:
        >>> _discover_dirs("templates")
        ['.../project/templates',
         '.../project/module_a/templates',
         '.../project/module_b/templates']
    """
    dirs: list[str] = []

    # ----- Search Base and Domains
    shared_dir = SRC_DIR / folder_name
    if shared_dir.exists():
        dirs.append(str(shared_dir))

    for path in sorted(SRC_DIR.iterdir()):
        candidate = path / folder_name
        if path.is_dir() and candidate.exists():
            dirs.append(str(candidate))

    return dirs


# --------------- JINJA2 TEMPLATE RENDERING ENGINE
page_loader = FileSystemLoader(_discover_dirs("templates"))
page_env = Environment(loader=page_loader)
templates = Jinja2Templates(env=page_env)
