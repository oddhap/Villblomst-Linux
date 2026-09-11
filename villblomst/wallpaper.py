"""Setter skrivebordsbakgrunn på GNOME/Zorin og håndterer flere skjermer."""
from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageOps

from . import config

GNOME_BG = "org.gnome.desktop.background"
_LISTMON_RE = re.compile(
    r"^\s*\d+:\s+[*+]*(?P<name>\S+)\s+"
    r"(?P<w>\d+)/\d+x(?P<h>\d+)/\d+\+(?P<x>-?\d+)\+(?P<y>-?\d+)",
)


@dataclass(frozen=True)
class Monitor:
    name: str
    x: int
    y: int
    width: int
    height: int
    primary: bool = False


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True, check=False)


def gsettings_available() -> bool:
    return shutil.which("gsettings") is not None


def list_monitors() -> list[Monitor]:
    """Leser skjermoppsett fra xrandr --listmonitors."""
    if shutil.which("xrandr") is None:
        return []
    result = _run(["xrandr", "--listmonitors"])
    if result.returncode != 0:
        return []

    monitors: list[Monitor] = []
    for line in result.stdout.splitlines():
        match = _LISTMON_RE.match(line)
        if not match:
            continue
        primary = line.strip().startswith("+") or "*" in line.split()[1]
        monitors.append(
            Monitor(
                name=match.group("name"),
                x=int(match.group("x")),
                y=int(match.group("y")),
                width=int(match.group("w")),
                height=int(match.group("h")),
                primary=primary,
            )
        )
    return monitors


def screen_count() -> int:
    monitors = list_monitors()
    return len(monitors) if monitors else 1


def _set(key: str, value: str) -> None:
    _run(["gsettings", "set", GNOME_BG, key, value])


def set_wallpaper(path: Path, options: str = "zoom") -> None:
    """Setter bakgrunn for alle skjermer (GNOME har én delt bakgrunn)."""
    uri = Path(path).resolve().as_uri()
    _set("picture-options", options)
    for key in ("picture-uri", "picture-uri-dark"):
        _set(key, uri)


def set_per_screen(paths: dict[int, Path], monitors: list[Monitor]) -> Path:
    """Bygger ett sammensatt bilde som dekker skjermoppsettet og setter det.

    GNOME støtter ikke egen bakgrunn per skjerm, så vi komponerer ett
    spennende bilde (picture-options 'spanned') som matcher xrandr-layouten.
    """
    if not monitors:
        raise RuntimeError("Fant ingen skjermer")

    min_x = min(m.x for m in monitors)
    min_y = min(m.y for m in monitors)
    max_x = max(m.x + m.width for m in monitors)
    max_y = max(m.y + m.height for m in monitors)

    canvas = Image.new("RGB", (max_x - min_x, max_y - min_y), (0, 0, 0))
    for index, monitor in enumerate(monitors):
        source = paths.get(index)
        if source is None:
            continue
        with Image.open(source) as image:
            fitted = ImageOps.fit(
                image.convert("RGB"),
                (monitor.width, monitor.height),
                Image.LANCZOS,
            )
        canvas.paste(fitted, (monitor.x - min_x, monitor.y - min_y))

    config.ensure_dirs()
    canvas.save(config.COMPOSITE_FILE, "PNG")
    set_wallpaper(config.COMPOSITE_FILE, options="spanned")
    return config.COMPOSITE_FILE
