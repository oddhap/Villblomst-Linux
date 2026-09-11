"""Favorittvindu med miniatyrbilder, tildeling til skjerm og fjerning."""
from __future__ import annotations

import threading

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk  # noqa: E402

from . import config, icons, images  # noqa: E402


class FavoritesWindow(Adw.Window):
    def __init__(self, store, loc) -> None:
        super().__init__(title=loc.t("favorites.title"))
        self.store = store
        self.loc = loc
        self.target_screen = -1
        self.set_default_size(420, 560)
        self.add_css_class("popover-bg")
        self.set_hide_on_close(True)

        toolbar = Adw.ToolbarView()
        header = Adw.HeaderBar()
        header.set_show_title(False)
        toolbar.add_top_bar(header)

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.body.set_margin_top(16)
        self.body.set_margin_bottom(20)
        self.body.set_margin_start(18)
        self.body.set_margin_end(18)
        scroller.set_child(self.body)
        toolbar.set_content(scroller)
        self.set_content(toolbar)

        self.store.connect(self.refresh)
        self.loc.connect(self.refresh)
        self.refresh()

    @staticmethod
    def _clear(container: Gtk.Widget) -> None:
        child = container.get_first_child()
        while child is not None:
            nxt = child.get_next_sibling()
            container.remove(child)
            child = nxt

    def refresh(self, *_args) -> None:
        self._clear(self.body)

        title = Gtk.Label(label=self.loc.t("favorites.title"), xalign=0)
        title.add_css_class("section-title")
        subtitle = Gtk.Label(label=self.loc.t("favorites.subtitle"), xalign=0)
        subtitle.add_css_class("section-sub")
        self.body.append(title)
        self.body.append(subtitle)

        if self.store.screen_count > 1:
            self.body.append(self._target_picker())

        if not self.store.favorites:
            empty = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            empty.set_halign(Gtk.Align.CENTER)
            empty.set_margin_top(30)
            empty.append(icons.image("heart-outline", config.BLOSSOM, 38))
            label = Gtk.Label(label=self.loc.t("favorites.empty"))
            label.add_css_class("hint-label")
            label.set_wrap(True)
            label.set_max_width_chars(40)
            label.set_justify(Gtk.Justification.CENTER)
            empty.append(label)
            self.body.append(empty)
            return

        flow = Gtk.FlowBox()
        flow.set_selection_mode(Gtk.SelectionMode.NONE)
        flow.set_max_children_per_line(3)
        flow.set_min_children_per_line(2)
        flow.set_row_spacing(10)
        flow.set_column_spacing(10)
        flow.set_homogeneous(True)
        for favorite in self.store.favorites:
            flow.append(self._tile(favorite))
        self.body.append(flow)

    def _target_picker(self) -> Gtk.Widget:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        label = Gtk.Label(label=self.loc.t("favorites.target"), xalign=0)
        label.add_css_class("hint-label")
        box.append(label)
        chips = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        chips.append(self._target_chip(self.loc.t("favorites.allScreens"), -1))
        for index in range(self.store.screen_count):
            chips.append(self._target_chip(self.loc.t("screen.short") % (index + 1), index))
        box.append(chips)
        return box

    def _target_chip(self, label: str, value: int) -> Gtk.Button:
        button = Gtk.Button(label=label)
        button.add_css_class("chip")
        if self.target_screen == value:
            button.add_css_class("selected")
        button.set_hexpand(False)
        button.connect("clicked", lambda *_: self._set_target(value))
        return button

    def _set_target(self, value: int) -> None:
        self.target_screen = value
        self.refresh()

    def _tile(self, favorite) -> Gtk.Widget:
        tile = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        tile.add_css_class("fav-tile")

        thumb = Gtk.Picture()
        thumb.set_size_request(118, 72)
        thumb.set_content_fit(Gtk.ContentFit.COVER)
        thumb.set_can_shrink(True)
        thumb.set_overflow(Gtk.Overflow.HIDDEN)
        file = self.store.favorite_file(favorite)
        if file.exists():
            try:
                thumb.set_filename(str(images.thumbnail_path(file, 236, 144, 10)))
            except Exception:  # noqa: BLE001
                pass

        remove = Gtk.Button()
        remove.add_css_class("preview-overlay-btn")
        remove.set_child(icons.image("xmark", "#ffffff", 11))
        remove.set_halign(Gtk.Align.END)
        remove.set_valign(Gtk.Align.START)
        remove.set_margin_top(5)
        remove.set_margin_end(5)
        remove.set_tooltip_text(self.loc.t("favorites.remove"))
        remove.connect("clicked", lambda *_: self.store.remove_favorite(favorite))

        overlay = Gtk.Overlay()
        overlay.set_child(thumb)
        overlay.add_overlay(remove)
        tile.append(overlay)

        name = Gtk.Label(label=favorite.title, xalign=0)
        name.add_css_class("fav-title")
        name.set_wrap(True)
        name.set_lines(2)
        name.set_ellipsize(3)
        tile.append(name)

        assigned = self.store.assigned_screen_numbers(favorite)
        if assigned:
            screens = ", ".join(str(i + 1) for i in assigned)
            assigned_label = Gtk.Label(
                label=self.loc.t("favorites.assignedScreens") % screens, xalign=0
            )
            assigned_label.add_css_class("fav-assign")
            tile.append(assigned_label)

        gesture = Gtk.GestureClick()
        gesture.connect("released", lambda *_: self._activate(favorite))
        tile.add_controller(gesture)
        tile.set_tooltip_text(
            self.loc.t("favorites.applyToScreen") % (self.target_screen + 1)
            if self.target_screen >= 0
            else self.loc.t("favorites.apply")
        )
        return tile

    def _activate(self, favorite) -> None:
        if self.target_screen >= 0:
            threading.Thread(
                target=self.store.assign_favorite, args=(favorite, self.target_screen), daemon=True
            ).start()
        else:
            threading.Thread(
                target=self.store.apply_favorite, args=(favorite,), daemon=True
            ).start()
