"""Norsk/engelsk grensesnitt (port av Localization.swift)."""
from __future__ import annotations

import os
from enum import Enum


class AppLanguage(str, Enum):
    SYSTEM = "system"
    NORWEGIAN = "norwegian"
    ENGLISH = "english"

    @property
    def label(self) -> str:
        return {"system": "System", "norwegian": "Norsk", "english": "English"}[self.value]


class Localization:
    def __init__(self, language: AppLanguage = AppLanguage.SYSTEM) -> None:
        self.language = language
        self._listeners: list = []

    def connect(self, callback) -> None:
        self._listeners.append(callback)

    def _notify(self) -> None:
        for callback in self._listeners:
            callback()

    def set_language(self, language: AppLanguage) -> None:
        self.language = language
        self._notify()

    @property
    def code(self) -> str:
        if self.language == AppLanguage.NORWEGIAN:
            return "nb"
        if self.language == AppLanguage.ENGLISH:
            return "en"
        raw = (
            os.environ.get("LANG")
            or os.environ.get("LC_MESSAGES")
            or os.environ.get("LC_ALL")
            or "en"
        ).lower()
        if raw.startswith(("nb", "nn", "no")):
            return "nb"
        return "en"

    @property
    def is_norwegian(self) -> bool:
        return self.code == "nb"

    def t(self, key: str) -> str:
        table = NORWEGIAN if self.is_norwegian else ENGLISH
        return table.get(key) or ENGLISH.get(key) or key

    def theme_name(self, theme_id: str) -> str:
        return self.t(f"theme.{theme_id}")

    def status_text(self, status: "Status") -> str:
        return status.format(self)


class Status:
    """En liten statusverdi med samme innhold som StoreStatus i Swift."""

    def __init__(self, kind: str, *args) -> None:
        self.kind = kind
        self.args = args

    def format(self, loc: Localization) -> str:
        k = self.kind
        a = self.args
        if k == "idle":
            return loc.t("status.idle")
        if k == "searching":
            return loc.t("status.searching")
        if k == "preparing":
            return loc.t("status.preparing")
        if k == "theme":
            return loc.t("status.theme") % (loc.theme_name(a[0]), a[1])
        if k == "fetching":
            return loc.t("status.fetching") % a[0]
        if k == "downloading":
            return loc.t("status.downloading")
        if k == "applied":
            return loc.t("status.applied")
        if k == "favoriteAdded":
            return loc.t("status.favoriteAdded")
        if k == "favoriteRemoved":
            return loc.t("status.favoriteRemoved")
        if k == "favoriteApplied":
            return loc.t("status.favoriteApplied")
        if k == "savingFavorite":
            return loc.t("status.savingFavorite") % a[0]
        if k == "favoriteSaved":
            return loc.t("status.favoriteSaved")
        if k == "savingFavorites":
            return loc.t("status.savingFavorites") % (a[0], a[1])
        if k == "favoritesSaved":
            return loc.t("status.favoritesSaved") % a[0]
        if k == "screenProgress":
            return loc.t("status.screenProgress") % (a[0], a[1])
        if k == "perScreenApplied":
            return loc.t("status.perScreenApplied") % a[0]
        if k == "screenAssigned":
            return loc.t("status.screenAssigned") % a[0]
        if k == "noImages":
            return loc.t("status.noImages")
        if k == "error":
            return loc.t("status.error") % a[0]
        return ""


NORWEGIAN = {
    "tagline": "Tilfeldige 4K-bakgrunner",
    "settings.source.title": "Bildekilde",
    "settings.source.subtitle": "Velg hvor bakgrunnene hentes fra",
    "settings.title": "Bakgrunnstema",
    "settings.subtitle": "Velg hvilke typer bilder som skal hentes",
    "settings.imagesCount": "%d bilder",
    "settings.matchSummary": "%d av %d bilder passer til «%s»",
    "settings.spotlightNote": "Spotlight-bilder filtreres også etter valgt tema.",
    "settings.perscreen.title": "Bakgrunn per skjerm",
    "settings.perscreen.subtitle": "La hver skjerm få sitt eget tilfeldige bilde",
    "settings.perscreen.toggle": "Egen bakgrunn per skjerm",
    "settings.general.title": "Generelt",
    "settings.favorites.title": "Favoritter",
    "settings.favorites.subtitle": "Lagring av favorittbilder",
    "settings.favorites.toggle": "Lagre favorittbilder lokalt",
    "settings.favorites.description": "Laster ned og lagrer favorittbildene i en egen lokal mappe, slik at de alltid er tilgjengelige – også uten nett.",
    "settings.language.title": "Språk",
    "settings.language.subtitle": "Velg språk for grensesnittet",
    "button.new": "Ny bakgrunn",
    "button.loading": "Henter …",
    "preview.empty": "Ingen bakgrunn ennå",
    "preview.ready": "Klar til å hente en bakgrunn",
    "footer.count": "%d av %d bilder",
    "status.idle": "Trykk på knappen for en ny bakgrunn",
    "status.searching": "Søker etter bakgrunner …",
    "status.preparing": "Bygger bildebibliotek …",
    "status.theme": "Tema: %s – %d bilder",
    "status.fetching": "Henter «%s» i 4K …",
    "status.downloading": "Laster ned 4K-bildet …",
    "status.applied": "Bakgrunnen er satt",
    "status.favoriteAdded": "Lagt til i favoritter",
    "status.favoriteRemoved": "Fjernet fra favoritter",
    "status.favoriteApplied": "Favoritten er satt som bakgrunn",
    "status.savingFavorite": "Lagrer «%s» lokalt …",
    "status.favoriteSaved": "Favorittbildet er lagret lokalt",
    "status.savingFavorites": "Lagrer favorittbilde %d av %d lokalt …",
    "status.favoritesSaved": "Lagret %d favorittbilder lokalt",
    "status.screenProgress": "Henter bilde %d av %d …",
    "status.perScreenApplied": "Egen bakgrunn satt på %d skjermer",
    "status.screenAssigned": "Favoritt satt på skjerm %d",
    "status.noImages": "Fant ingen bilder akkurat nå",
    "status.error": "Noe gikk galt: %s",
    "favorites.title": "Favoritter",
    "favorites.subtitle": "Lagrede bakgrunner du kan bruke igjen",
    "favorites.empty": "Ingen favoritter ennå. Trykk på hjertet i forhåndsvisningen for å lagre et bilde.",
    "favorites.toggle": "Legg til eller fjern favoritt",
    "favorites.apply": "Bruk som bakgrunn",
    "favorites.remove": "Fjern fra favoritter",
    "favorites.help": "Favoritter",
    "favorites.assignedScreens": "Skjerm %s",
    "favorites.target": "Bruk på",
    "favorites.allScreens": "Alle skjermer",
    "favorites.applyToScreen": "Bruk på skjerm %d",
    "screen.short": "Skjerm %d",
    "screen.label": "Skjerm %d",
    "screen.labelPrimary": "Skjerm %d (hovedskjerm)",
    "theme.alle": "Alle",
    "theme.blomster": "Blomster",
    "theme.natur": "Natur",
    "theme.dyr": "Dyr",
    "theme.by": "By",
    "theme.landskap": "Landskap",
    "theme.hav": "Hav og vann",
    "theme.verdensrom": "Verdensrom",
    "theme.host": "Høst og vinter",
    "source.bing": "Bing Wallpaper",
    "source.spotlight": "Windows Spotlight",
}

ENGLISH = {
    "tagline": "Random 4K wallpapers",
    "settings.source.title": "Image source",
    "settings.source.subtitle": "Choose where wallpapers come from",
    "settings.title": "Wallpaper theme",
    "settings.subtitle": "Choose which kind of images to fetch",
    "settings.imagesCount": "%d images",
    "settings.matchSummary": "%d of %d images match “%s”",
    "settings.spotlightNote": "Spotlight images are filtered by the selected theme too.",
    "settings.perscreen.title": "Wallpaper per screen",
    "settings.perscreen.subtitle": "Give each screen its own random image",
    "settings.perscreen.toggle": "Separate wallpaper per screen",
    "settings.general.title": "General",
    "settings.favorites.title": "Favorites",
    "settings.favorites.subtitle": "Favorite image storage",
    "settings.favorites.toggle": "Store favorite images locally",
    "settings.favorites.description": "Downloads and stores favorite images in a dedicated local folder, so they are always available – even offline.",
    "settings.language.title": "Language",
    "settings.language.subtitle": "Choose the interface language",
    "button.new": "New wallpaper",
    "button.loading": "Fetching …",
    "preview.empty": "No wallpaper yet",
    "preview.ready": "Ready to fetch a wallpaper",
    "footer.count": "%d of %d images",
    "status.idle": "Click the button for a new wallpaper",
    "status.searching": "Searching for wallpapers …",
    "status.preparing": "Building the wallpaper library …",
    "status.theme": "Theme: %s – %d images",
    "status.fetching": "Fetching “%s” in 4K …",
    "status.downloading": "Downloading the 4K image …",
    "status.applied": "Wallpaper applied",
    "status.favoriteAdded": "Added to favorites",
    "status.favoriteRemoved": "Removed from favorites",
    "status.favoriteApplied": "Favorite applied as wallpaper",
    "status.savingFavorite": "Saving “%s” locally …",
    "status.favoriteSaved": "Favorite image saved locally",
    "status.savingFavorites": "Saving favorite image %d of %d locally …",
    "status.favoritesSaved": "Saved %d favorite images locally",
    "status.screenProgress": "Fetching image %d of %d …",
    "status.perScreenApplied": "Separate wallpapers set on %d screens",
    "status.screenAssigned": "Favorite set on screen %d",
    "status.noImages": "No images found right now",
    "status.error": "Something went wrong: %s",
    "favorites.title": "Favorites",
    "favorites.subtitle": "Saved wallpapers you can reuse",
    "favorites.empty": "No favorites yet. Tap the heart on the preview to save an image.",
    "favorites.toggle": "Add or remove favorite",
    "favorites.apply": "Apply as wallpaper",
    "favorites.remove": "Remove from favorites",
    "favorites.help": "Favorites",
    "favorites.assignedScreens": "Screen %s",
    "favorites.target": "Apply to",
    "favorites.allScreens": "All screens",
    "favorites.applyToScreen": "Apply to screen %d",
    "screen.short": "Screen %d",
    "screen.label": "Screen %d",
    "screen.labelPrimary": "Screen %d (primary)",
    "theme.alle": "All",
    "theme.blomster": "Flowers",
    "theme.natur": "Nature",
    "theme.dyr": "Animals",
    "theme.by": "City",
    "theme.landskap": "Landscape",
    "theme.hav": "Ocean & water",
    "theme.verdensrom": "Space",
    "theme.host": "Autumn & winter",
    "source.bing": "Bing Wallpaper",
    "source.spotlight": "Windows Spotlight",
}
