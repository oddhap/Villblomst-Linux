#!/usr/bin/env bash
# Installerer Villblomst for din bruker (~/.local).
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$HOME/.local/share/villblomst"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/scalable/apps"
DESKTOP_FILE="$DESKTOP_DIR/com.github.oddhap.Villblomst.desktop"
WRAPPER="$BIN_DIR/villblomst"

echo "Sjekker avhengigheter …"
missing=0
python3 - <<'PY' || missing=1
import importlib
for module in ("gi", "requests", "PIL"):
    try:
        importlib.import_module(module)
    except ImportError:
        raise SystemExit(f"Mangler Python-modul: {module}")
print("Alle Python-avhengigheter er på plass.")
PY
if [ "$missing" -ne 0 ]; then
    echo
    echo "Installer manglende pakker, for eksempel:"
    echo "  sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 python3-requests python3-pil"
    exit 1
fi

echo "Kopierer appfiler til $APP_DIR …"
rm -rf "$APP_DIR"
mkdir -p "$APP_DIR"
cp -r "$DIR/villblomst" "$APP_DIR/villblomst"
cp -r "$DIR/data" "$APP_DIR/data"
find "$APP_DIR" -name '__pycache__' -type d -prune -exec rm -rf {} +

echo "Lager startskript i $WRAPPER …"
mkdir -p "$BIN_DIR"
cat > "$WRAPPER" <<EOF
#!/usr/bin/env bash
exec env PYTHONPATH="$APP_DIR" python3 -m villblomst "\$@"
EOF
chmod +x "$WRAPPER"

echo "Installerer ikon og skrivebordsfil …"
mkdir -p "$ICON_DIR" "$DESKTOP_DIR"
cp "$DIR/data/icons/com.github.oddhap.Villblomst.svg" "$ICON_DIR/"
cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=Villblomst
GenericName=Wallpaper
Comment=Random 4K wallpapers from Bing and Windows Spotlight
Exec=$WRAPPER
Icon=com.github.oddhap.Villblomst
Terminal=false
Categories=Utility;Graphics;
StartupNotify=true
Keywords=wallpaper;bakgrunn;bing;spotlight;4k;
EOF

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$DESKTOP_DIR" >/dev/null 2>&1 || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" >/dev/null 2>&1 || true
fi

echo
echo "Ferdig! Start Villblomst:"
echo "  - via appmenyen («Villblomst»)"
echo "  - eller kommandoen: villblomst"
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo
    echo "Merk: $BIN_DIR er ikke i PATH. Legg til i ~/.profile:"
    echo '  export PATH="$HOME/.local/bin:$PATH"'
fi
