# Villblomst (Linux)

A small native Linux app (GTK4 + libadwaita) that downloads a random 4K
wallpaper from the [Bing Wallpaper Archive](https://bingwallpaper.anerg.com/) or
**Windows Spotlight**, and sets it as your desktop background with a single
click.

This is the Linux port of the macOS app
[oddhap/Villblomst](https://github.com/oddhap/Villblomst), rewritten in Python
with GTK4/libadwaita for GNOME-based desktops such as **Zorin OS**.

## Features

- **Two 4K image sources** – the Bing Wallpaper Archive and Windows Spotlight,
  both downloaded at full 3840×2160 resolution.
- **Theme picker** – choose which kind of images to fetch (flowers, nature,
  animals, city, landscape, ocean, space, autumn/winter, or everything).
- **Bilingual interface** – Norwegian and English, switchable at runtime with a
  system-language default.
- **Favorites** – save the wallpapers you like and re-apply them any time, with
  an option to store the full-size images in a local folder for offline use.
- **Multiple screens** – give each screen its own random wallpaper, or assign a
  saved favorite to a specific screen.
- **Sets the desktop background** on GNOME via `gsettings`.
- **Remembers your theme** and keeps a local collection of wallpapers,
  refreshed automatically every 7 days.
- **Light wildflower/plant UI theme** with custom generated icons.
- **No third-party dependencies** beyond `requests` and `Pillow`.

## Requirements

- Linux with a GNOME-based desktop (tested on Zorin OS 18 / GNOME, X11)
- Python 3.10+
- GTK 4 and libadwaita 1 (PyGObject)

On Debian/Ubuntu/Zorin:

```bash
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 python3-requests python3-pil
```

## Install and run

```bash
git clone https://github.com/oddhap/Villblomst-Linux.git
cd Villblomst-Linux
./install.sh
```

`install.sh` copies the app to `~/.local/share/villblomst`, creates the
`villblomst` command, and registers an icon and desktop entry so the app appears
in your application menu.

Run directly from source without installing:

```bash
./run.sh
```

## Usage

1. Open **Villblomst**.
2. Click **New wallpaper** to fetch and apply a random wallpaper.
3. Click the gear icon to open **Settings**, then pick an image source and a
   theme.
4. Scroll to the **Language** section in Settings to switch between System,
   Norsk, and English.
5. Tap the heart on the preview to add the current wallpaper to **Favorites**.
   Open the heart button in the header to re-apply or remove saved wallpapers.
6. With more than one display, turn on **Separate wallpaper per screen** in
   Settings to fetch a separate image for each screen. To place a saved favorite
   on one screen, open Favorites, pick the screen under **Apply to**, then tap
   the favorite.

Themes are matched against the wallpaper's caption text, so several themes can
overlap. Approximate distribution of the built-in archive:

| Theme | Wallpapers |
| --- | --- |
| All | ~1800 |
| Nature | ~448 |
| Ocean & water | ~429 |
| Landscape | ~352 |
| Animals | ~291 |
| City | ~252 |
| Flowers | ~105 |
| Autumn & winter | ~94 |
| Space | ~72 |

## Image sources

### Bing Wallpaper Archive

1. `scraper.py` fetches monthly archive pages (`/archive/us/yyyyMM`) and collects
   every wallpaper entry (slug + caption).
2. The pool is filtered by the selected theme using keyword matching on the
   caption.
3. For the chosen wallpaper, the detail page (`/detail/us/<slug>`) is fetched
   and the **Download 4K** link is extracted with a regular expression.
4. The image is downloaded to `~/.local/share/villblomst/Wallpapers/` and applied
   with `gsettings`.

The wallpaper pool is cached in `~/.local/share/villblomst/pool.json` for 7
days.

### Windows Spotlight

`spotlight.py` calls Microsoft's Spotlight selection API
(`fd.api.iris.microsoft.com/v4/api/selection`) with the system region and
locale, and requests landscape images at 3840×2160. No archive caching is needed
because the API returns a fresh batch on every request.

## Project structure

```
villblomst/
  app.py               App entry point (Adw.Application)
  window.py            Main window and light wildflower theme
  settings_window.py   Source, theme, per-screen and language settings
  favorites_window.py  Saved wallpapers panel
  store.py             State, caching, download and wallpaper handling
  wallpaper.py         gsettings and per-screen composition
  scraper.py           Bing archive scraping and 4K URL extraction
  spotlight.py         Windows Spotlight API client
  themes.py            Theme definitions and keyword matching
  localization.py      Norwegian/English strings and language handling
  icons.py             SVG icon loading
  images.py            Thumbnails and rounded previews
  style.py             GTK CSS
data/icons/            SVG icons and app icon
install.sh             One-step install
run.sh                 Run from source
```

## Favorites

Tap the heart on the preview to save the current wallpaper. Saved wallpapers
appear under the heart button in the header, where you can re-apply them as the
desktop background or remove them. Favorite metadata is stored in
`~/.local/share/villblomst/favorites.json`.

Turn on **Store favorite images locally** in Settings to download and keep the
full-size image of every favorite in
`~/.local/share/villblomst/Favorites/`, so a favorite can be re-applied without
an internet connection. Enabling the option also downloads any existing
favorites that are missing a local copy.

## Multiple screens

GNOME does not natively support a different wallpaper per monitor. Villblomst
works around this by composing a single image that spans the monitor layout
(read from `xrandr`) and applying it with `picture-options 'spanned'`. This works
best on X11 and when the monitors are laid out side by side.

## Data locations

Everything is stored under `~/.local/share/villblomst/`:

- `Wallpapers/` – downloaded images
- `Favorites/` – full-size images of saved favorites
- `pool.json` – cached wallpaper pool (7 days)
- `state.json` – the last applied wallpaper
- `favorites.json` – saved favorites
- `screens.json` – favorites assigned to screens
- `settings.json` – source, theme, language and per-screen choice

## Uninstall

```bash
./uninstall.sh
```

## Acknowledgements

The Windows Spotlight integration is based on the API research and
implementation in
[ORelio/Spotlight-Downloader](https://github.com/ORelio/Spotlight-Downloader),
released under
[CDDL-1.0](https://opensource.org/licenses/CDDL-1.0). Thanks to ORelio for
documenting the Spotlight API endpoints.

## Notes and disclaimer

- All wallpapers are copyright their respective owners and are provided by the
  Bing Wallpaper Archive and by Microsoft Windows Spotlight. This project only
  automates downloading them for personal use; it does not claim any rights to
  the images.
- The wallpaper pool and theme counts are approximate and depend on what the
  sources currently offer.

## License

The source code is released under the [MIT License](LICENSE).
