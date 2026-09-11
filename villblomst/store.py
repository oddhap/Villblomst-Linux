"""App-tilstand: hurtigbuffer, nedlasting, favoritter og bakgrunnsbytte."""
from __future__ import annotations

import json
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from . import config, spotlight, wallpaper
from .localization import AppLanguage, Localization, Status
from .scraper import FALLBACK, Wallpaper, detail_4k_url, download, month_strings, pool, make_session
from .themes import THEMES, WallpaperTheme, theme_by_id


@dataclass
class Favorite:
    slug: str
    title: str
    remote_url: str | None = None


class Store:
    def __init__(self, localization: Localization, dispatch=None) -> None:
        config.ensure_dirs()
        self.loc = localization
        self._dispatch = dispatch or (lambda fn: fn())
        self._lock = threading.RLock()
        self._listeners: list = []

        self.status = Status("idle")
        self.is_loading = False
        self.is_preparing = False

        # Innstillinger
        self.source = "bing"
        self.theme_id = "alle"
        self.per_screen = False
        self.language = AppLanguage.SYSTEM

        # Tilstand
        self.preview_file: Path | None = None
        self.wallpaper_title = ""
        self.current_slug: str | None = None
        self.current_remote_url: str | None = None
        self.current_file: Path | None = None
        self.pool: list[Wallpaper] = []
        self.pool_count = 0
        self.total_count = 0
        self.theme_counts: dict[str, int] = {}
        self._recent: list[str] = []
        self._screen_files: dict[int, Path] = {}

        self.favorites: list[Favorite] = []
        self.screen_assignments: dict[str, Favorite] = {}

        self.session = make_session()
        self._load_settings()
        self._load_favorites()
        self._load_screen_assignments()
        self._restore_state()
        self._load_cached_pool()

    # ------------------------------------------------------------------ lytting
    def connect(self, callback) -> None:
        self._listeners.append(callback)

    def _notify(self) -> None:
        for callback in list(self._listeners):
            self._dispatch(callback)

    def _set_status(self, status: Status, loading: bool | None = None) -> None:
        with self._lock:
            self.status = status
            if loading is not None:
                self.is_loading = loading
        self._notify()

    # ----------------------------------------------------------- egenskaper
    @property
    def theme(self) -> WallpaperTheme:
        return theme_by_id(self.theme_id)

    @property
    def source_name(self) -> str:
        return self.loc.t(f"source.{self.source}")

    @property
    def selected_theme_name(self) -> str:
        return self.loc.theme_name(self.theme_id)

    @property
    def source_attribution(self) -> str:
        return "bingwallpaper.anerg.com" if self.source == "bing" else "Windows Spotlight (Microsoft)"

    @property
    def screen_count(self) -> int:
        return wallpaper.screen_count()

    @property
    def status_text(self) -> str:
        return self.loc.status_text(self.status)

    @property
    def uses_per_screen(self) -> bool:
        return self.per_screen and self.screen_count > 1

    @property
    def is_current_favorite(self) -> bool:
        return any(f.slug == self.current_slug for f in self.favorites)

    def assigned_screen_numbers(self, favorite: Favorite) -> list[int]:
        return sorted(
            int(index)
            for index, value in self.screen_assignments.items()
            if value.slug == favorite.slug
        )

    def favorite_file(self, favorite: Favorite) -> Path:
        return config.IMAGE_DIR / f"{favorite.slug}.jpg"

    # --------------------------------------------------------- innstillinger
    def _load_settings(self) -> None:
        try:
            data = json.loads(config.SETTINGS_FILE.read_text("utf-8"))
        except (OSError, ValueError):
            return
        self.source = data.get("source", self.source)
        self.theme_id = data.get("theme", self.theme_id)
        self.per_screen = bool(data.get("per_screen", self.per_screen))
        self.language = AppLanguage(data.get("language", self.language.value))
        self.loc.language = self.language

    def _save_settings(self) -> None:
        payload = {
            "source": self.source,
            "theme": self.theme_id,
            "per_screen": self.per_screen,
            "language": self.language.value,
        }
        try:
            config.SETTINGS_FILE.write_text(json.dumps(payload, indent=2), "utf-8")
        except OSError:
            pass

    def select_theme(self, theme: WallpaperTheme) -> None:
        self.theme_id = theme.id
        self._save_settings()
        self.pool_count = self.theme_counts.get(theme.id, len(self.pool))
        self._set_status(Status("theme", theme.id, self.pool_count))

    def select_source(self, source: str) -> None:
        self.source = source
        self._save_settings()
        if source == "bing":
            self._set_status(Status("theme", self.theme_id, self.pool_count))
        else:
            self._set_status(Status("idle"))

    def toggle_per_screen(self) -> None:
        self.per_screen = not self.per_screen
        self._save_settings()
        self._notify()

    def set_language(self, language: AppLanguage) -> None:
        self.language = language
        self.loc.set_language(language)
        self._save_settings()
        self._notify()

    # ------------------------------------------------------------- favoritter
    def _load_favorites(self) -> None:
        try:
            raw = json.loads(config.FAVORITES_FILE.read_text("utf-8"))
            self.favorites = [Favorite(**item) for item in raw]
        except (OSError, ValueError, TypeError):
            self.favorites = []

    def _save_favorites(self) -> None:
        try:
            config.FAVORITES_FILE.write_text(
                json.dumps([asdict(f) for f in self.favorites], indent=2, ensure_ascii=False),
                "utf-8",
            )
        except OSError:
            pass

    def _load_screen_assignments(self) -> None:
        try:
            raw = json.loads(config.SCREENS_FILE.read_text("utf-8"))
            self.screen_assignments = {
                str(k): Favorite(**v) for k, v in raw.items()
            }
        except (OSError, ValueError, TypeError):
            self.screen_assignments = {}

    def _save_screen_assignments(self) -> None:
        try:
            payload = {k: asdict(v) for k, v in self.screen_assignments.items()}
            config.SCREENS_FILE.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False), "utf-8"
            )
        except OSError:
            pass

    def toggle_favorite(self) -> None:
        if not self.current_slug or not self.wallpaper_title:
            return
        existing = next((f for f in self.favorites if f.slug == self.current_slug), None)
        if existing:
            self.favorites.remove(existing)
            self._save_favorites()
            self._set_status(Status("favoriteRemoved"))
        else:
            self.favorites.insert(
                0,
                Favorite(self.current_slug, self.wallpaper_title, self.current_remote_url),
            )
            self._save_favorites()
            self._set_status(Status("favoriteAdded"))

    def remove_favorite(self, favorite: Favorite) -> None:
        self.favorites = [f for f in self.favorites if f.slug != favorite.slug]
        self._save_favorites()
        self._set_status(Status("favoriteRemoved"))

    # ------------------------------------------------------------- hurtigbuffer
    def _restore_state(self) -> None:
        try:
            data = json.loads(config.STATE_FILE.read_text("utf-8"))
        except (OSError, ValueError):
            return
        self._recent = data.get("recent", [])
        self.wallpaper_title = data.get("title", "")
        self.current_slug = data.get("currentSlug")
        image_name = data.get("imageName")
        if image_name:
            candidate = config.IMAGE_DIR / image_name
            if candidate.exists():
                self.current_file = candidate
                self.preview_file = candidate

    def _persist_state(self, image_name: str | None) -> None:
        payload = {
            "recent": self._recent,
            "title": self.wallpaper_title,
            "imageName": image_name,
            "currentSlug": self.current_slug,
        }
        try:
            config.STATE_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False), "utf-8")
        except OSError:
            pass

    def _load_cached_pool(self) -> None:
        if self.pool:
            return
        try:
            cached = json.loads(config.POOL_FILE.read_text("utf-8"))
        except (OSError, ValueError):
            return
        if cached.get("version") != 2:
            return
        try:
            age = time.time() - datetime.fromisoformat(cached["date"]).timestamp()
        except (KeyError, ValueError):
            return
        if age >= config.POOL_MAX_AGE_SECONDS:
            return
        self.pool = [Wallpaper(**item) for item in cached.get("items", [])]
        self._compute_counts()

    def _save_pool(self) -> None:
        payload = {
            "version": 2,
            "date": datetime.now().isoformat(),
            "items": [asdict(w) for w in self.pool],
        }
        try:
            config.POOL_FILE.write_text(json.dumps(payload, ensure_ascii=False), "utf-8")
        except OSError:
            pass

    def _compute_counts(self) -> None:
        counts: dict[str, int] = {}
        for theme in THEMES:
            counts[theme.id] = sum(1 for w in self.pool if theme.matches(w.title))
        self.theme_counts = counts
        self.total_count = len(self.pool)
        self.pool_count = counts.get(self.theme_id, len(self.pool))

    def prepare_pool(self, force: bool = False) -> None:
        if self.is_preparing:
            return
        if not force and self.pool:
            self._compute_counts()
            self._notify()
            return
        if not force:
            self._load_cached_pool()
            if self.pool:
                self._notify()
                return

        self.is_preparing = True
        self._set_status(Status("preparing"))
        months = month_strings(config.POOL_MONTHS_BACK)

        def progress(done: int, total: int) -> None:
            self.pool_count = done
            self._set_status(Status("preparing"))

        fetched = pool(months, self.session, progress=progress)
        self.pool = fetched or FALLBACK
        if fetched:
            self._save_pool()
        self._compute_counts()
        self.is_preparing = False
        self._set_status(Status("theme", self.theme_id, self.pool_count))

    # --------------------------------------------------------------- henting
    def next_wallpaper(self) -> None:
        if self.is_loading:
            return
        if self.source == "spotlight":
            self._next_spotlight()
        else:
            self._next_bing()

    def _next_bing(self) -> None:
        self._set_status(Status("searching"), loading=True)
        if not self.pool:
            self.prepare_pool()
        if not self.pool:
            self.pool = list(FALLBACK)
            self._compute_counts()

        theme = self.theme
        themed = [w for w in self.pool if theme.matches(w.title)]
        source = themed or self.pool
        count = self.screen_count if self.uses_per_screen else 1
        picks = self._pick_many(source, count)
        if not picks:
            self._set_status(Status("noImages"), loading=False)
            return

        monitors = wallpaper.list_monitors()
        files: dict[int, Path] = {}
        try:
            for index, choice in enumerate(picks):
                if count > 1:
                    self._set_status(Status("screenProgress", index + 1, count))
                else:
                    self._set_status(Status("fetching", choice.title))
                remote = detail_4k_url(choice.slug, self.session)
                destination = config.IMAGE_DIR / f"{choice.slug}.jpg"
                if count == 1:
                    self._set_status(Status("downloading"))
                download(remote, destination, self.session)
                files[index] = destination
                self._recent.append(choice.slug)
                if index == 0:
                    self._remember_current(choice.slug, choice.title, remote, destination)

            self._trim_recent()
            self._persist_state(self.current_file.name if self.current_file else None)
            if count > 1 and len(monitors) > 1:
                self._apply_per_screen(files, monitors)
                self._set_status(Status("perScreenApplied", len(files)), loading=False)
            else:
                self._apply_single(files[0])
                self._set_status(Status("applied"), loading=False)
        except Exception as exc:  # noqa: BLE001
            self._set_status(Status("error", str(exc)), loading=False)

    def _next_spotlight(self) -> None:
        self._set_status(Status("searching"), loading=True)
        count = self.screen_count if self.uses_per_screen else 1
        recent = set(self._recent)
        try:
            candidates = spotlight.collect(max(count, 1), self.theme, recent, self.session)
        except Exception as exc:  # noqa: BLE001
            self._set_status(Status("error", str(exc)), loading=False)
            return

        available = [img for img in candidates if img.id not in recent] or candidates
        if not available:
            self._set_status(Status("noImages"), loading=False)
            return

        picks = available[:]
        import random

        random.shuffle(picks)
        if len(picks) < count:
            picks.extend(candidates)
        picks = picks[:count]

        monitors = wallpaper.list_monitors()
        files: dict[int, Path] = {}
        try:
            for index, choice in enumerate(picks):
                if count > 1:
                    self._set_status(Status("screenProgress", index + 1, count))
                else:
                    self._set_status(Status("fetching", choice.display_title))
                destination = config.IMAGE_DIR / f"{choice.id}.jpg"
                if count == 1:
                    self._set_status(Status("downloading"))
                download(choice.url, destination, self.session)
                files[index] = destination
                self._recent.append(choice.id)
                if index == 0:
                    self._remember_current(choice.id, choice.display_title, choice.url, destination)

            self._trim_recent()
            self._persist_state(self.current_file.name if self.current_file else None)
            if count > 1 and len(monitors) > 1:
                self._apply_per_screen(files, monitors)
                self._set_status(Status("perScreenApplied", len(files)), loading=False)
            else:
                self._apply_single(files[0])
                self._set_status(Status("applied"), loading=False)
        except Exception as exc:  # noqa: BLE001
            self._set_status(Status("error", str(exc)), loading=False)

    def _remember_current(self, slug: str, title: str, remote, destination: Path) -> None:
        self.current_slug = slug
        self.wallpaper_title = title
        self.current_remote_url = remote
        self.current_file = destination
        self.preview_file = destination

    def _pick_many(self, source: list[Wallpaper], count: int) -> list[Wallpaper]:
        if not source:
            return []
        import random

        available = [w for w in source if w.slug not in self._recent]
        if not available:
            self._recent = []
            available = list(source)
        picks = available[:]
        random.shuffle(picks)
        if len(picks) < count:
            extra = list(source)
            random.shuffle(extra)
            picks.extend(extra)
        return picks[:count]

    def _trim_recent(self) -> None:
        if len(self._recent) > config.RECENT_LIMIT:
            self._recent = self._recent[-config.RECENT_LIMIT:]

    # --------------------------------------------------------------- favoritter
    def apply_favorite(self, favorite: Favorite) -> None:
        if self.is_loading:
            return
        try:
            file = self._ensure_favorite_file(favorite)
            self._apply_single(file)
            self.current_slug = favorite.slug
            self.wallpaper_title = favorite.title
            self.current_remote_url = favorite.remote_url
            self.current_file = file
            self.preview_file = file
            self._persist_state(file.name)
            self._set_status(Status("favoriteApplied"))
        except Exception as exc:  # noqa: BLE001
            self._set_status(Status("error", str(exc)))

    def assign_favorite(self, favorite: Favorite, index: int) -> None:
        monitors = wallpaper.list_monitors()
        if not monitors or not (0 <= index < len(monitors)):
            return
        try:
            self._set_status(Status("fetching", favorite.title), loading=True)
            file = self._ensure_favorite_file(favorite)
            self.screen_assignments[str(index)] = favorite
            self._save_screen_assignments()
            self._screen_files[index] = file
            self._apply_per_screen(self._screen_files, monitors)
            if not self.current_slug:
                self.current_slug = favorite.slug
                self.wallpaper_title = favorite.title
                self.current_file = file
                self.preview_file = file
                self._persist_state(file.name)
            self._set_status(Status("screenAssigned", index + 1), loading=False)
        except Exception as exc:  # noqa: BLE001
            self._set_status(Status("error", str(exc)), loading=False)

    def _ensure_favorite_file(self, favorite: Favorite) -> Path:
        file = self.favorite_file(favorite)
        if file.exists():
            return file
        self._set_status(Status("fetching", favorite.title), loading=True)
        remote = favorite.remote_url or detail_4k_url(favorite.slug, self.session)
        download(remote, file, self.session)
        return file

    # ----------------------------------------------------------- bakgrunn
    def _apply_single(self, file: Path) -> None:
        wallpaper.set_wallpaper(file)
        monitors = wallpaper.list_monitors()
        self._screen_files = {index: file for index in range(len(monitors))} if monitors else {0: file}

    def _apply_per_screen(self, files: dict[int, Path], monitors) -> None:
        paths: dict[int, Path] = {}
        for index, _monitor in enumerate(monitors):
            candidate = files.get(index)
            if candidate and candidate.exists():
                paths[index] = candidate
            elif self.current_file and self.current_file.exists():
                paths[index] = self.current_file
        wallpaper.set_per_screen(paths, monitors)
        self._screen_files = dict(paths)
