"""Hovedvinduet for Villblomst."""
from __future__ import annotations

import threading

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk  # noqa: E402

from . import config, icons, images  # noqa: E402
from .favorites_window import FavoritesWindow  # noqa: E402
from .settings_window import SettingsWindow  # noqa: E402


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, application, store, loc) -> None:
        super().__init__(application=application, title="Villblomst")
        self.store = store
        self.loc = loc
        self.set_default_size(460, 730)
        self.add_css_class("villblomst-window")

        self._last_preview = None
        self._favorite_state: bool | None = None
        self._settings_window = None
        self._favorites_window = None

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        headerbar = Adw.HeaderBar()
        headerbar.set_show_title(False)
        headerbar.add_css_class("villblomst-header")
        outer.append(headerbar)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_margin_top(10)
        content.set_margin_bottom(18)
        content.set_margin_start(26)
        content.set_margin_end(26)
        outer.append(content)

        content.append(self._build_header())
        content.append(self._build_preview())
        content.append(self._build_caption())
        content.append(self._build_action())
        content.append(self._build_status())
        spacer = Gtk.Box()
        spacer.set_vexpand(True)
        content.append(spacer)
        content.append(self._build_footer())

        self.set_content(outer)

        self.store.connect(self.refresh)
        self.loc.connect(self.refresh)
        self.refresh()

        threading.Thread(target=self.store.prepare_pool, daemon=True).start()

    # --------------------------------------------------------------- bygging
    def _build_header(self) -> Gtk.Widget:
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)

        badge = Gtk.Box()
        badge.add_css_class("app-badge")
        badge.set_valign(Gtk.Align.CENTER)
        flower = icons.image("daisy", "#ffffff", 34)
        flower.set_halign(Gtk.Align.CENTER)
        flower.set_valign(Gtk.Align.CENTER)
        badge.append(flower)
        box.append(badge)

        titles = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        titles.set_valign(Gtk.Align.CENTER)
        title = Gtk.Label(label="Villblomst", xalign=0)
        title.add_css_class("header-title")
        self.subtitle = Gtk.Label(label="", xalign=0)
        self.subtitle.add_css_class("header-sub")
        titles.append(title)
        titles.append(self.subtitle)
        box.append(titles)

        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        box.append(spacer)

        # Favoritter-knapp med teller
        self.fav_button = Gtk.Button()
        self.fav_button.add_css_class("icon-btn")
        self.fav_button.set_tooltip_text(self.loc.t("favorites.help"))
        self.fav_icon = Gtk.Image()
        fav_overlay = Gtk.Overlay()
        fav_overlay.set_child(self.fav_icon)
        self.fav_count = Gtk.Label(label="0")
        self.fav_count.add_css_class("count-badge")
        self.fav_count.set_halign(Gtk.Align.END)
        self.fav_count.set_valign(Gtk.Align.START)
        self.fav_count.set_margin_top(-4)
        self.fav_count.set_margin_end(-4)
        fav_overlay.add_overlay(self.fav_count)
        self.fav_button.set_child(fav_overlay)
        self.fav_button.connect("clicked", self._open_favorites)
        box.append(self.fav_button)

        gear_button = Gtk.Button()
        gear_button.add_css_class("icon-btn")
        gear_button.set_tooltip_text(self.loc.t("settings.help"))
        gear_button.set_child(icons.image("gear", config.LEAF_DEEP, 20))
        gear_button.connect("clicked", self._open_settings)
        box.append(gear_button)

        return box

    def _build_preview(self) -> Gtk.Widget:
        card = Gtk.Box()
        card.add_css_class("preview-card")
        card.set_size_request(404, 330)

        self.picture = Gtk.Picture()
        self.picture.set_content_fit(Gtk.ContentFit.COVER)
        self.picture.set_can_shrink(True)
        self.picture.set_hexpand(True)
        self.picture.set_vexpand(True)

        self.placeholder = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.placeholder.set_halign(Gtk.Align.CENTER)
        self.placeholder.set_valign(Gtk.Align.CENTER)
        self.placeholder_icon = icons.image("flower", config.LEAF, 58)
        self.placeholder_label = Gtk.Label(label=self.loc.t("preview.empty"))
        self.placeholder_label.add_css_class("hint-label")
        self.placeholder.append(self.placeholder_icon)
        self.placeholder.append(self.placeholder_label)

        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        stack.add_named(self.picture, "picture")
        stack.add_named(self.placeholder, "placeholder")
        self.preview_stack = stack
        card.append(stack)

        overlay = Gtk.Overlay()
        overlay.set_child(card)
        overlay.set_halign(Gtk.Align.CENTER)

        self.fav_toggle = Gtk.Button()
        self.fav_toggle.add_css_class("preview-overlay-btn")
        self.fav_toggle.set_halign(Gtk.Align.END)
        self.fav_toggle.set_valign(Gtk.Align.START)
        self.fav_toggle.set_margin_top(12)
        self.fav_toggle.set_margin_end(12)
        self.fav_toggle.set_tooltip_text(self.loc.t("favorites.toggle"))
        self.fav_toggle_icon = Gtk.Image()
        self.fav_toggle.set_child(self.fav_toggle_icon)
        self.fav_toggle.connect("clicked", lambda *_: self.store.toggle_favorite())
        overlay.add_overlay(self.fav_toggle)

        return overlay

    def _build_caption(self) -> Gtk.Widget:
        self.caption = Gtk.Label(label=self.loc.t("preview.ready"))
        self.caption.add_css_class("caption")
        self.caption.set_wrap(True)
        self.caption.set_justify(Gtk.Justification.CENTER)
        self.caption.set_max_width_chars(48)
        self.caption.set_lines(2)
        self.caption.set_ellipsize(3)  # Pango.EllipsizeMode.END
        self.caption.set_size_request(-1, 36)
        return self.caption

    def _build_action(self) -> Gtk.Widget:
        self.action_button = Gtk.Button()
        self.action_button.add_css_class("action-btn")
        content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        content.set_halign(Gtk.Align.CENTER)
        self.action_spinner = Gtk.Spinner()
        self.action_sparkle = icons.image("sparkle", "#ffffff", 20)
        self.action_label = Gtk.Label(label=self.loc.t("button.new"))
        content.append(self.action_spinner)
        content.append(self.action_sparkle)
        content.append(self.action_label)
        self.action_button.set_child(content)
        self.action_button.connect("clicked", self._on_new_wallpaper)
        return self.action_button

    def _build_status(self) -> Gtk.Widget:
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=7)
        self.status_spinner = Gtk.Spinner()
        self.status_icon = icons.image("leaf", config.LEAF_DEEP, 13)
        self.status_label = Gtk.Label(label="", xalign=0)
        self.status_label.add_css_class("status-label")
        self.status_label.set_wrap(True)
        self.status_label.set_max_width_chars(52)
        box.append(self.status_spinner)
        box.append(self.status_icon)
        box.append(self.status_label)
        return box

    def _build_footer(self) -> Gtk.Widget:
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.attribution = Gtk.Label(label="", xalign=0)
        self.attribution.add_css_class("footer-label")
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        box.append(self.attribution)
        box.append(spacer)
        self.count_label = Gtk.Label(label="", xalign=1)
        self.count_label.add_css_class("footer-label")
        box.append(self.count_label)
        return box

    # -------------------------------------------------------------- handlinger
    def _on_new_wallpaper(self, *_args) -> None:
        if self.store.is_loading:
            return
        threading.Thread(target=self.store.next_wallpaper, daemon=True).start()

    def _open_settings(self, *_args) -> None:
        if self._settings_window is None:
            self._settings_window = SettingsWindow(self.store, self.loc)
        self._settings_window.refresh()
        self._settings_window.present()

    def _open_favorites(self, *_args) -> None:
        if self._favorites_window is None:
            self._favorites_window = FavoritesWindow(self.store, self.loc)
        self._favorites_window.refresh()
        self._favorites_window.present()

    # ----------------------------------------------------------------- oppdater
    def refresh(self) -> None:
        store = self.store
        self.subtitle.set_text(f"{store.source_name} · {store.selected_theme_name}")

        if store.preview_file and store.preview_file.exists():
            if store.preview_file != self._last_preview:
                try:
                    rounded = images.preview(store.preview_file)
                    self.picture.set_filename(str(rounded))
                    self._last_preview = store.preview_file
                except Exception:  # noqa: BLE001
                    pass
            self.preview_stack.set_visible_child_name("picture")
            self.fav_toggle.set_visible(bool(store.wallpaper_title))
        else:
            self.preview_stack.set_visible_child_name("placeholder")
            self.fav_toggle.set_visible(False)

        self.caption.set_text(store.wallpaper_title or self.loc.t("preview.ready"))

        loading = store.is_loading or store.is_preparing
        self.action_button.set_sensitive(not loading)
        self.action_label.set_text(self.loc.t("button.loading" if store.is_loading else "button.new"))
        self.action_spinner.set_visible(store.is_loading)
        if store.is_loading:
            self.action_spinner.start()
        else:
            self.action_spinner.stop()
        self.action_sparkle.set_visible(not store.is_loading)

        self.status_label.set_text(store.status_text)
        self.status_spinner.set_visible(store.is_preparing)
        self.status_icon.set_visible(not store.is_preparing)
        if store.is_preparing:
            self.status_spinner.start()
        else:
            self.status_spinner.stop()

        self.attribution.set_text(store.source_attribution)
        if store.source == "bing" and store.total_count:
            self.count_label.set_text(
                self.loc.t("footer.count") % (store.pool_count, store.total_count)
            )
            self.count_label.set_visible(True)
        else:
            self.count_label.set_visible(False)

        # Hjerte-tilstand
        is_favorite = store.is_current_favorite
        if is_favorite != self._favorite_state:
            self.fav_toggle_icon.set_from_pixbuf(
                icons.pixbuf(
                    "heart" if is_favorite else "heart-outline",
                    config.BLOSSOM if is_favorite else "#ffffff",
                    22,
                )
            )
            self._favorite_state = is_favorite

        self.fav_count.set_text(str(len(store.favorites)))
        self.fav_count.set_visible(bool(store.favorites))
        self.fav_icon.set_from_pixbuf(
            icons.pixbuf(
                "heart" if store.favorites else "heart-outline",
                config.BLOSSOM if store.favorites else config.LEAF_DEEP,
                20,
            )
        )
