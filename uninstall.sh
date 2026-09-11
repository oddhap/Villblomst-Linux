#!/usr/bin/env bash
# Fjerner Villblomst installert med install.sh (beholder nedlastede bilder).
set -euo pipefail

rm -rf "$HOME/.local/share/villblomst"
rm -f "$HOME/.local/bin/villblomst"
rm -f "$HOME/.local/share/applications/com.github.oddhap.Villblomst.desktop"
rm -f "$HOME/.local/share/icons/hicolor/scalable/apps/com.github.oddhap.Villblomst.svg"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$HOME/.local/share/applications" >/dev/null 2>&1 || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" >/dev/null 2>&1 || true
fi

echo "Villblomst er avinstallert."
