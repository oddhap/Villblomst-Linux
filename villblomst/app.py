"""App-oppstart for Villblomst."""
from __future__ import annotations

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gdk, Gio, GLib, Gtk  # noqa: E402

from . import config, style  # noqa: E402
from .localization import Localization  # noqa: E402
from .store import Store  # noqa: E402
from .window import MainWindow  # noqa: E402


class VillblomstApplication(Adw.Application):
    def __init__(self) -> None:
        super().__init__(
            application_id=config.APP_ID,
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )
        self.loc = Localization()
        self.store = Store(self.loc, dispatch=GLib.idle_add)
        self._window = None

    def do_startup(self) -> None:
        Adw.Application.do_startup(self)
        style.install()
        Gtk.Window.set_default_icon_name(config.APP_ID)
        self._register_icons()

    def _register_icons(self) -> None:
        display = Gdk.Display.get_default()
        if display is None:
            return
        theme = Gtk.IconTheme.get_for_display(display)
        theme.add_search_path(str(config.ICON_DIR))

    def do_activate(self) -> None:
        if self._window is None:
            self._window = MainWindow(self, self.store, self.loc)
            self._window.connect("destroy", self._on_window_destroyed)
        self._window.present()

    def _on_window_destroyed(self, *_args) -> None:
        self._window = None


def main(argv: list[str] | None = None) -> int:
    app = VillblomstApplication()
    return app.run(argv)
