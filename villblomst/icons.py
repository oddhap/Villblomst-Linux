"""Laster SVG-ikoner fra data/icons og fargelegger dem."""
from __future__ import annotations

from functools import lru_cache

import gi

gi.require_version("GdkPixbuf", "2.0")
from gi.repository import GdkPixbuf  # noqa: E402

from . import config  # noqa: E402


@lru_cache(maxsize=512)
def pixbuf(name: str, color: str, size: int = 20) -> GdkPixbuf.Pixbuf:
    path = config.ICON_DIR / f"{name}.svg"
    svg = path.read_text("utf-8").replace("currentColor", color)
    loader = GdkPixbuf.PixbufLoader.new_with_type("svg")
    loader.set_size(size, size)
    loader.write(svg.encode("utf-8"))
    loader.close()
    return loader.get_pixbuf()


def image(name: str, color: str, size: int = 20):
    from gi.repository import Gtk

    return Gtk.Image.new_from_pixbuf(pixbuf(name, color, size))
