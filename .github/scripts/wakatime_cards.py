import json
import sys
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

USER = "TriTacLe"
# Browsers, notes, meeting apps and AI agents are not hands-on editing.
SKIP_EDITORS = {"Firefox", "Chrome", "Chromium", "Safari", "Edge", "Brave", "Opera", "Arc", "Vivaldi",
                "Obsidian", "Zoom", "Teams", "Slack", "Claude Code"}


def card(title, rows, width, height, row_gap, pct=False):
    top = rows[0]["total_seconds"] if rows else 1
    total = sum(r["total_seconds"] for r in rows) or 1
    bar_w = width - 210
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{title}">',
        "<style>text{font-family:'Segoe UI',Ubuntu,sans-serif}</style>",
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="4.5" fill="#141321" stroke="#e4e2e2"/>',
        f'<text x="20" y="35" fill="#fe428e" font-size="18" font-weight="600">{title}</text>',
    ]
    for i, r in enumerate(rows):
        y = 68 + i * row_gap
        bar = round(bar_w * r["total_seconds"] / top)
        value = f'{round(100 * r["total_seconds"] / total)}%' if pct else f'{round(r["total_seconds"] / 3600)} h'
        parts += [
            f'<text x="20" y="{y}" fill="#a9fef7" font-size="14">{escape(r["name"])}</text>',
            f'<rect x="125" y="{y - 9}" width="{bar_w}" height="8" rx="4" fill="#2a2840"/>',
            f'<rect x="125" y="{y - 9}" width="{max(bar, 4)}" height="8" rx="4" fill="#fe428e"/>',
            f'<text x="{width - 20}" y="{y}" fill="#a9fef7" font-size="14" text-anchor="end">{value}</text>',
        ]
    parts.append("</svg>")
    return "\n".join(parts)


url = f"https://wakatime.com/api/v1/users/{USER}/stats?is_including_today=true"
with urllib.request.urlopen(url, timeout=30) as resp:
    data = json.load(resp)["data"]

out = Path(sys.argv[1])
editors = [e for e in data["editors"] if e["name"] not in SKIP_EDITORS and e["total_seconds"] > 0][:5]
systems = [s for s in data["operating_systems"] if s["name"] != "Unknown OS" and s["total_seconds"] > 0][:3]
# Sizes match the GitHub stats card (195 high) and the WakaTime card (265 high) they sit next to.
(out / "editors.svg").write_text(card("Editors", editors, 300, 195, 26))
(out / "os.svg").write_text(card("Operating systems", systems, 260, 265, 70, pct=True))
