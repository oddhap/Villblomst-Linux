"""Bing Wallpaper Archive-skraper (port av Scraper.swift)."""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

import requests

BASE = "https://bingwallpaper.anerg.com"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

_ANCHOR_RE = re.compile(
    r'href="/detail/us/([^"]+)"[^>]*?data-bs-title="([^"]*)"', re.DOTALL
)
_IMG_RE = re.compile(r"""https://imgproxy\.nanxiongnandi\.com/[^"']*w:3840[^"']*""")
_ENTITY_RE = re.compile(r"&#(x?[0-9A-Fa-f]+);")
_NAMED = {
    "&amp;": "&",
    "&quot;": '"',
    "&#39;": "'",
    "&apos;": "'",
    "&lt;": "<",
    "&gt;": ">",
    "&nbsp;": " ",
    "&#43;": "+",
}


class ScraperError(Exception):
    pass


@dataclass(frozen=True)
class Wallpaper:
    slug: str
    title: str


# Noen faste favoritter i tilfelle nettet ikke er tilgjengelig første gang.
FALLBACK: list[Wallpaper] = [
    Wallpaper("WildflowerValley", "Wildflower bloom, Central Valley, California"),
    Wallpaper("RilaCrocuses", "Purple crocus flowers, Seven Rila Lakes, Bulgaria"),
    Wallpaper("LupineBloom", "Lupine flowers in bloom, Northern California"),
    Wallpaper("DutchTulips", "Grape hyacinths and tulips, Keukenhof Gardens, Netherlands"),
    Wallpaper("HoneyBeeLavender", "Honey bee on lavender flowers"),
    Wallpaper("PinkDahlia", "Pink dahlia flower"),
    Wallpaper("HertfordshireBluebells", "A path through a bluebell forest, England"),
    Wallpaper("WildLupine", "Wild lupines in bloom"),
    Wallpaper("HwangmaesanAzaleas", "Royal azaleas on Hwangmaesan Mountain, South Korea"),
    Wallpaper("RainierWildflowers", "Wildflowers in Mount Rainier National Park"),
]


def make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    session.request = _with_timeout(session.request)
    return session


def _with_timeout(func):
    def wrapper(method, url, **kwargs):
        kwargs.setdefault("timeout", 30)
        return func(method, url, **kwargs)

    return wrapper


def month_strings(back: int, from_date: date | None = None) -> list[str]:
    """Siste `back` måneder som "yyyyMM", nyeste først."""
    today = from_date or date.today()
    year, month = today.year, today.month
    out: list[str] = []
    for _ in range(back):
        out.append(f"{year:04d}{month:02d}")
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    return out


def fetch_html(url: str, session: requests.Session) -> str:
    response = session.get(url)
    if not 200 <= response.status_code < 300:
        raise ScraperError(f"Nettsiden svarte med HTTP {response.status_code}")
    response.encoding = response.apparent_encoding or "utf-8"
    return response.text


def parse_anchors(html: str) -> list[Wallpaper]:
    out: list[Wallpaper] = []
    for slug, title in _ANCHOR_RE.findall(html):
        out.append(Wallpaper(slug, decode_html(title)))
    return out


def fetch_archive(month: str, session: requests.Session) -> list[Wallpaper]:
    try:
        html = fetch_html(f"{BASE}/archive/us/{month}", session)
    except Exception:
        return []
    return parse_anchors(html)


def pool(months: list[str], session: requests.Session, progress=None) -> list[Wallpaper]:
    """Henter alle arkivsider og returnerer alle unike bakgrunner."""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    by_slug: dict[str, Wallpaper] = {}
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(fetch_archive, m, session): m for m in months}
        for done, future in enumerate(as_completed(futures), start=1):
            for item in future.result():
                by_slug[item.slug] = item
            if progress:
                progress(done, len(months))
    return sorted(by_slug.values(), key=lambda w: w.title.lower())


def detail_4k_url(slug: str, session: requests.Session) -> str:
    html = fetch_html(f"{BASE}/detail/us/{slug}", session)
    match = _IMG_RE.search(html)
    if not match:
        raise ScraperError("Fant ikke 4K-bildet")
    return match.group(0)


def download(url: str, destination, session: requests.Session) -> None:
    response = session.get(url, stream=True, timeout=90)
    if not 200 <= response.status_code < 300:
        raise ScraperError(f"Nettsiden svarte med HTTP {response.status_code}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    tmp = destination.with_suffix(destination.suffix + ".part")
    with open(tmp, "wb") as handle:
        for chunk in response.iter_content(chunk_size=65536):
            if chunk:
                handle.write(chunk)
    tmp.replace(destination)


def decode_html(value: str) -> str:
    text = value
    for key, replacement in _NAMED.items():
        text = text.replace(key, replacement)

    def replace_entity(match: re.Match[str]) -> str:
        raw = match.group(1)
        try:
            code = int(raw[1:], 16) if raw[0] in "xX" else int(raw)
            return chr(code)
        except (ValueError, OverflowError):
            return match.group(0)

    return _ENTITY_RE.sub(replace_entity, text)
