"""Windows Spotlight API-klient (port av SpotlightSource.swift).

Endepunkt og responsformat er basert på ORelio/Spotlight-Downloader
(https://github.com/ORelio/Spotlight-Downloader), lisensiert under CDDL-1.0.
Dette er en uavhengig Python-reimplementering av v4 "selection"-API-et.
"""
from __future__ import annotations

import locale as _locale
import os
from dataclasses import dataclass

import requests

from .scraper import ScraperError, USER_AGENT


@dataclass(frozen=True)
class SpotlightImage:
    id: str
    url: str
    title: str
    copyright: str

    @property
    def search_text(self) -> str:
        return f"{self.title} {self.copyright}"

    @property
    def display_title(self) -> str:
        return f"{self.title} ({self.copyright})" if self.copyright else self.title


def locale_info() -> tuple[str, str]:
    # Prøv LANG/LC_ALL, faller tilbake til nb-NO / en-US.
    raw = (
        os.environ.get("LC_ALL")
        or os.environ.get("LC_MESSAGES")
        or os.environ.get("LANG")
        or _locale.getlocale()[0]
        or "en_US"
    )
    normalized = raw.split(".")[0].split("@")[0].replace("_", "-")
    parts = normalized.split("-")
    if len(parts) > 1 and len(parts[1]) == 2:
        country = parts[1].upper()
        return f"{parts[0]}-{country}", country
    return "en-US", "US"


def _first_line(value: str | None) -> str | None:
    if not value:
        return None
    line = value.replace("\r", "\n").split("\n")
    first = next((part.strip() for part in line if part.strip()), "")
    return first or None


def fetch_once(locale: str, country: str, session: requests.Session) -> list[SpotlightImage]:
    url = (
        "https://fd.api.iris.microsoft.com/v4/api/selection"
        f"?&placement=88000820&bcnt=4&country={country}&locale={locale}&fmt=json"
    )
    response = session.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    if not 200 <= response.status_code < 300:
        raise ScraperError(f"Nettsiden svarte med HTTP {response.status_code}")

    try:
        root = response.json()
        items = root["batchrsp"]["items"]
    except (ValueError, KeyError, TypeError) as exc:
        raise ScraperError("Fant ingen Spotlight-bilder") from exc

    images: list[SpotlightImage] = []
    for wrapper in items:
        try:
            inner = wrapper["item"]
            if isinstance(inner, str):
                import json

                inner = json.loads(inner)
            ad = inner["ad"]
            asset = ad["landscapeImage"]["asset"]
        except (KeyError, TypeError, ValueError):
            continue

        title = _first_line(ad.get("iconHoverText"))
        if not title:
            cleaned = (ad.get("title") or "").strip()
            title = cleaned or ""
        copyright_text = (ad.get("copyright") or "").strip()
        image_id = asset.split("?")[0].rsplit("/", 1)[-1].rsplit(".", 1)[0]
        if not image_id:
            continue
        images.append(SpotlightImage(image_id, asset, title, copyright_text))
    return images


def collect(
    needed: int, theme, recent: set[str], session: requests.Session
) -> list[SpotlightImage]:
    """Henter flere batcher og filtrerer på tema, som macOS-versjonen."""
    info_locale, country = locale_info()
    collected: list[SpotlightImage] = []
    seen: set[str] = set()
    themed: list[SpotlightImage] = []

    for _ in range(8):
        batch = fetch_once(info_locale, country, session)
        for image in batch:
            if image.id not in seen:
                seen.add(image.id)
                collected.append(image)
        themed = [
            img
            for img in collected
            if img.id not in recent and theme.matches(img.search_text)
        ]
        if len(themed) >= max(needed, 4):
            break
    return themed if themed else collected
