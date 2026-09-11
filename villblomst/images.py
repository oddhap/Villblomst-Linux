"""Bildehjelpere: avrundede miniatyrbilder og forhåndsvisninger."""
from __future__ import annotations

import hashlib
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

from . import config


def _rounded_thumbnail(source: Path, width: int, height: int, radius: int) -> Image.Image:
    with Image.open(source) as image:
        fitted = ImageOps.fit(image.convert("RGB"), (width, height), Image.LANCZOS)
    mask = Image.new("L", (width, height), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, width - 1, height - 1), radius, fill=255)
    output = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    output.paste(fitted, (0, 0))
    output.putalpha(mask)
    return output


def thumbnail_path(source: Path, width: int, height: int, radius: int = 14) -> Path:
    """Lager (eller gjenbruker) et avrundet miniatyrbilde på disk."""
    config.ensure_dirs()
    try:
        stamp = source.stat().st_mtime_ns
    except OSError:
        stamp = 0
    digest = hashlib.sha1(
        f"{source}:{stamp}:{width}x{height}:{radius}".encode()
    ).hexdigest()[:16]
    destination = config.THUMB_DIR / f"{digest}.png"
    if not destination.exists():
        _rounded_thumbnail(source, width, height, radius).save(destination, "PNG")
    return destination


def preview(source: Path, width: int = 404, height: int = 330, radius: int = 22) -> Path:
    return thumbnail_path(source, width, height, radius)
