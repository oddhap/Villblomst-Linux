"""Felles konfigurasjon: stier, palett og app-metadata."""
from __future__ import annotations

import os
from pathlib import Path

APP_ID = "com.github.oddhap.Villblomst"
APP_NAME = "Villblomst"
VERSION = "1.0.0"

# Brukerens datamappe (~/.local/share/villblomst)
DATA_HOME = Path(
    os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
) / "villblomst"

IMAGE_DIR = DATA_HOME / "Wallpapers"
FAVORITES_DIR = DATA_HOME / "Favorites"
THUMB_DIR = DATA_HOME / "Thumbnails"
COMPOSITE_FILE = DATA_HOME / "composite.png"
POOL_FILE = DATA_HOME / "pool.json"
STATE_FILE = DATA_HOME / "state.json"
FAVORITES_FILE = DATA_HOME / "favorites.json"
SCREENS_FILE = DATA_HOME / "screens.json"
SETTINGS_FILE = DATA_HOME / "settings.json"

ICON_DIR = Path(__file__).resolve().parent.parent / "data" / "icons"

POOL_MAX_AGE_SECONDS = 60 * 60 * 24 * 7  # 7 dager
RECENT_LIMIT = 12
POOL_MONTHS_BACK = 60

# Villblomst-paletten (samme som macOS-versjonen)
CREAM = "#fcf9f0"
SKY = "#e8f2fa"
LEAF_LIGHT = "#e6f5e0"
LEAF = "#6ba86b"
LEAF_DEEP = "#3d7849"
BLOSSOM = "#f5b8c7"
PETAL = "#fde6eb"
INK = "#2e3d30"


def ensure_dirs() -> None:
    """Oppretter alle datamapper appen trenger."""
    for directory in (DATA_HOME, IMAGE_DIR, FAVORITES_DIR, THUMB_DIR):
        directory.mkdir(parents=True, exist_ok=True)
