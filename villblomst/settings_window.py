"""Innstillingsvindu: kilde, tema, flerskjerm og språk."""
from __future__ import annotations

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk  # noqa: E402

from . import config, icons  # noqa: E402
from .localization import AppLanguage  # noqa: E402
from .themes import THEMES  # noqa: E402


class SettingsWindow(Adw.Window):
    def __init__(self, store, loc) -> None:
        super().__init__(title=loc.t("settings.help"))
        self.store = store
        self.loc = loc
        self.set_default_size(430, 760)
        self.add_css_class("popover-bg")
        self.set_hide_on_close(True)

        toolbar = Adw.ToolbarView()
        header = Adw.HeaderBar()
        header.set_show_title(False)
        toolbar.add_top_bar(header)

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
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

    # --------------------------------------------------------------- hjelpere
    @staticmethod
    def _clear(container: Gtk.Widget) -> None:
        child = container.get_first_child()
        while child is not None:
            nxt = child.get_next_sibling()
            container.remove(child)
            child = nxt

    def _section(self, title: str, subtitle: str) -> None:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        title_label = Gtk.Label(label=title, xalign=0)
        title_label.add_css_class("section-title")
        sub_label = Gtk.Label(label=subtitle, xalign=0)
        sub_label.add_css_class("section-sub")
        sub_label.set_wrap(True)
        box.append(title_label)
        box.append(sub_label)
        self.body.append(box)

    def _chip(self, label: str, selected: bool, callback) -> Gtk.Button:
        button = Gtk.Button(label=label)
        button.add_css_class("chip")
        if selected:
            button.add_css_class("selected")
        button.set_hexpand(True)
        button.connect("clicked", lambda *_: callback())
        return button

    # ----------------------------------------------------------------- oppdater
    def refresh(self, *_args) -> None:
        self._clear(self.body)

        # Bildekilde
        self._section(self.loc.t("settings.source.title"), self.loc.t("settings.source.subtitle"))
        sources = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        for source in ("bing", "spotlight"):
            sources.append(
                self._chip(
                    self.loc.t(f"source.{source}"),
                    self.store.source == source,
                    lambda s=source: self.store.select_source(s),
                )
            )
        self.body.append(sources)
        self.body.append(Gtk.Separator())

        # Tema
        self._section(self.loc.t("settings.title"), self.loc.t("settings.subtitle"))
        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        grid.set_column_homogeneous(True)
        for index, theme in enumerate(THEMES):
            grid.attach(self._theme_card(theme), index % 2, index // 2, 1, 1)
        self.body.append(grid)

        if self.store.source == "bing":
            summary = self.loc.t("settings.matchSummary") % (
                self.store.pool_count,
                self.store.total_count,
                self.store.selected_theme_name,
            )
        else:
            summary = self.loc.t("settings.spotlightNote")
        hint = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        hint.append(icons.image("image", config.INK, 14))
        hint_label = Gtk.Label(label=summary, xalign=0)
        hint_label.add_css_class("hint-label")
        hint_label.set_wrap(True)
        hint_label.set_hexpand(True)
        hint.append(hint_label)
        self.body.append(hint)
        self.body.append(Gtk.Separator())

        # Bakgrunn per skjerm
        self._section(
            self.loc.t("settings.perscreen.title"), self.loc.t("settings.perscreen.subtitle")
        )
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        row.add_css_class("theme-card")
        row.append(icons.image("grid", config.LEAF_DEEP, 18))
        row_label = Gtk.Label(label=self.loc.t("settings.perscreen.toggle"), xalign=0)
        row_label.set_hexpand(True)
        switch = Gtk.Switch()
        switch.set_active(self.store.per_screen)
        switch.set_valign(Gtk.Align.CENTER)
        switch.connect("state-set", self._on_per_screen)
        row.append(row_label)
        row.append(switch)
        self.body.append(row)
        self.body.append(Gtk.Separator())

        # Språk
        self._section(
            self.loc.t("settings.language.title"), self.loc.t("settings.language.subtitle")
        )
        languages = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        for language in AppLanguage:
            languages.append(
                self._chip(
                    language.label,
                    self.loc.language == language,
                    lambda lang=language: self.store.set_language(lang),
                )
            )
        self.body.append(languages)

    def _theme_card(self, theme) -> Gtk.Widget:
        selected = theme.id == self.store.theme_id
        button = Gtk.Button()
        button.add_css_class("theme-card")
        if selected:
            button.add_css_class("selected")

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        top.append(
            icons.image(
                theme.icon, "#ffffff" if selected else config.LEAF_DEEP, 20
            )
        )
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        top.append(spacer)
        if selected:
            check = Gtk.Label(label="✓")
            check.add_css_class("theme-name")
            top.append(check)
        content.append(top)

        name = Gtk.Label(label=self.loc.theme_name(theme.id), xalign=0)
        name.add_css_class("theme-name")
        content.append(name)

        if self.store.source == "bing":
            count = self.store.theme_counts.get(theme.id, 0)
            count_label = Gtk.Label(
                label=self.loc.t("settings.imagesCount") % count, xalign=0
            )
        else:
            count_label = Gtk.Label(label=" ", xalign=0)
        count_label.add_css_class("theme-count")
        content.append(count_label)

        button.set_child(content)
        button.connect("clicked", lambda *_: self.store.select_theme(theme))
        return button

    def _on_per_screen(self, switch, state):
        if state != self.store.per_screen:
            self.store.toggle_per_screen()
        return False
