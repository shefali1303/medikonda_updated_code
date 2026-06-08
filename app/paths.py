from __future__ import annotations

from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = APP_ROOT / "data"
DATA_ROOT.mkdir(exist_ok=True)


def app_root() -> Path:
    return APP_ROOT


def resource_root() -> Path:
    return APP_ROOT


def resource_path(*parts: str) -> Path:
    return resource_root().joinpath(*parts)


def user_path(*parts: str) -> Path:
    path = DATA_ROOT.joinpath(*parts)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
