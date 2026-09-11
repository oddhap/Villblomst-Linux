"""GTK CSS for Villblomst (blomsterinspirert lyst tema)."""
from __future__ import annotations

from gi.repository import Gdk, Gtk

CSS = """
.villblomst-gradient {
  background-image: linear-gradient(135deg, #fcf9f0 0%, #e6f5e0 42%, #e8f2fa 72%, #fde6eb 100%);
}
.popover-bg { background-color: #fcf9f0; }

.app-badge {
  background-image: linear-gradient(160deg, #6ba86b, #3d7849);
  border-radius: 999px;
  min-width: 54px;
  min-height: 54px;
  box-shadow: 0 6px 16px rgba(61,120,73,0.35);
}
.header-title { font-size: 23px; font-weight: 800; color: #2e3d30; }
.header-sub { font-size: 13px; color: rgba(61,120,73,0.85); }

.icon-btn {
  background-color: rgba(255,255,255,0.9);
  border: 1px solid rgba(107,168,107,0.3);
  border-radius: 999px;
  min-width: 36px;
  min-height: 36px;
  padding: 0;
  box-shadow: none;
}
.icon-btn:hover { background-color: #ffffff; }

.count-badge {
  background-color: #3d7849;
  color: #ffffff;
  font-size: 10px;
  font-weight: 700;
  border-radius: 999px;
  padding: 1px 6px;
  min-height: 0;
}

.preview-card {
  border-radius: 22px;
  border: 1px solid rgba(107,168,107,0.25);
  background-color: rgba(255,255,255,0.85);
  box-shadow: 0 10px 28px rgba(61,120,73,0.18);
}
.preview-overlay-btn {
  background-color: rgba(0,0,0,0.32);
  border: none;
  border-radius: 999px;
  min-width: 36px;
  min-height: 36px;
  padding: 0;
}
.preview-overlay-btn:hover { background-color: rgba(0,0,0,0.5); }

.caption { font-size: 13px; color: rgba(46,61,48,0.72); }

.action-btn {
  background-image: linear-gradient(135deg, #6ba86b, #3d7849);
  color: #ffffff;
  border: none;
  border-radius: 16px;
  padding: 15px 18px;
  font-size: 15px;
  font-weight: 700;
  box-shadow: 0 8px 20px rgba(61,120,73,0.35);
}
.action-btn:hover { box-shadow: 0 10px 24px rgba(61,120,73,0.45); }
.action-btn:disabled { opacity: 0.75; }

.status-label { font-size: 12px; color: rgba(61,120,73,0.9); }
.footer-label { font-size: 11px; color: rgba(46,61,48,0.45); }

.section-title { font-size: 16px; font-weight: 700; color: #2e3d30; }
.section-sub { font-size: 12px; color: rgba(46,61,48,0.6); }
.hint-label { font-size: 12px; color: rgba(46,61,48,0.6); }

.chip {
  background-color: rgba(255,255,255,0.9);
  border: 1px solid rgba(107,168,107,0.25);
  border-radius: 10px;
  padding: 9px 8px;
  color: #3d7849;
  font-weight: 600;
  box-shadow: none;
}
.chip:hover { background-color: #ffffff; }
.chip.selected {
  background-image: linear-gradient(135deg, #6ba86b, #3d7849);
  border-color: transparent;
  color: #ffffff;
}
.chip.selected label { color: #ffffff; }

.theme-card {
  background-color: rgba(255,255,255,0.9);
  border: 1px solid rgba(107,168,107,0.25);
  border-radius: 14px;
  padding: 12px;
  box-shadow: none;
}
.theme-card:hover { background-color: #ffffff; }
.theme-card.selected {
  background-image: linear-gradient(135deg, #6ba86b, #3d7849);
  border-color: transparent;
  box-shadow: 0 6px 16px rgba(61,120,73,0.3);
}
.theme-name { font-size: 14px; font-weight: 700; color: #2e3d30; }
.theme-count { font-size: 11px; color: rgba(46,61,48,0.55); }
.theme-card.selected .theme-name { color: #ffffff; }
.theme-card.selected .theme-count { color: rgba(255,255,255,0.85); }

.fav-tile {
  background-color: rgba(255,255,255,0.9);
  border: 1px solid rgba(107,168,107,0.25);
  border-radius: 12px;
  padding: 8px;
  box-shadow: none;
}
.fav-tile:hover { background-color: #ffffff; }
.fav-title { font-size: 11px; color: rgba(46,61,48,0.8); }
.fav-assign { font-size: 10px; font-weight: 600; color: #3d7849; }
"""


def install() -> None:
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS.encode("utf-8"))
    display = Gdk.Display.get_default()
    if display is not None:
        Gtk.StyleContext.add_provider_for_display(
            display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
