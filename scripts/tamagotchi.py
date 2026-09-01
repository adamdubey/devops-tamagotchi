import argparse
import json
import random
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

STATE_FILE = ROOT / "state.json"
README_FILE = ROOT / "README.md"
ASSETS_DIR = ROOT / "assets"


# ---------------------------------------------------------
# CLI
# ---------------------------------------------------------

parser = argparse.ArgumentParser()

parser.add_argument(
    "--render-only",
    action="store_true",
    help="Render the dashboard without mutating Tamagotchi state",
)

args = parser.parse_args()


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def format_duration(seconds):
    if seconds is None:
        return "N/A"

    seconds = int(seconds)

    if seconds < 60:
        return f"{seconds}s"

    minutes = seconds // 60
    remaining_seconds = seconds % 60

    if minutes < 60:
        return f"{minutes}m {remaining_seconds}s"

    hours = minutes // 60
    remaining_minutes = minutes % 60

    return f"{hours}h {remaining_minutes}m"


# ---------------------------------------------------------
# LOAD STATE
# ---------------------------------------------------------

with open(STATE_FILE, encoding="utf-8") as f:
    state = json.load(f)


# ---------------------------------------------------------
# NORMAL HEALTH CHECK
# ---------------------------------------------------------
#
# --render-only:
#   Leave state untouched and only regenerate the dashboard.
#
# Normal run:
#   Simulate telemetry.
#
# Active incidents stay active until poke_prod.py heals them.
# ---------------------------------------------------------

if not args.render_only:

    if state["status"] == "incident":
        state["cpu"] = random.randint(88, 100)
        state["memory"] = random.randint(85, 100)

        if state.get("message") in (None, "", "server is happy"):
            state["message"] = "incident still active"

    else:
        roll = random.random()

        if roll < 0.08:
            state["status"] = "degraded"
            state["message"] = "prod is having a moment"

        elif roll < 0.23:
            state["status"] = "degraded"
            state["message"] = "server feels kinda weird"

        else:
            state["status"] = "healthy"
            state["message"] = "server is happy"

        if state["status"] == "healthy":
            state["cpu"] = random.randint(10, 55)
            state["memory"] = random.randint(20, 65)

        elif state["status"] == "degraded":
            state["cpu"] = random.randint(60, 85)
            state["memory"] = random.randint(65, 90)

    state["uptime_hours"] += 1

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")


# ---------------------------------------------------------
# DISPLAY CONFIG
# ---------------------------------------------------------

status_config = {
    "healthy": {
        "icon": "🟢",
        "label": "HEALTHY",
        "face": "(づ ◕‿◕ )づ",
        "accent": "#3fb950",
        "card": "#0d2818",
    },
    "degraded": {
        "icon": "🟡",
        "label": "DEGRADED",
        "face": "(・_・;)",
        "accent": "#d29922",
        "card": "#2d250d",
    },
    "incident": {
        "icon": "🔴",
        "label": "INCIDENT",
        "face": "(╯°□°)╯︵ ┻━┻",
        "accent": "#f85149",
        "card": "#2d1117",
    },
}

cfg = status_config.get(
    state["status"],
    {
        "icon": "⚪",
        "label": "UNKNOWN",
        "face": "(?_?)",
        "accent": "#8b949e",
        "card": "#161b22",
    },
)


# ---------------------------------------------------------
# METRICS
# ---------------------------------------------------------

cpu_segments = min(10, max(0, state["cpu"] // 10))
memory_segments = min(10, max(0, state["memory"] // 10))

cpu_bar = "█" * cpu_segments + "░" * (10 - cpu_segments)
memory_bar = "█" * memory_segments + "░" * (10 - memory_segments)

last_mttr = format_duration(state.get("last_mttr_seconds"))
average_mttr = format_duration(state.get("average_mttr_seconds"))

updated_at = datetime.now(timezone.utc)

updated_display = updated_at.strftime("%Y-%m-%d %H:%M UTC")
dashboard_version = updated_at.strftime("%Y%m%d-%H%M%S%f")

ASSETS_DIR.mkdir(parents=True, exist_ok=True)

SVG_FILE = ASSETS_DIR / f"dashboard-{dashboard_version}.svg"


# ---------------------------------------------------------
# SVG DASHBOARD
# ---------------------------------------------------------

svg = f"""
<svg width="720" height="460" viewBox="0 0 720 460"
     xmlns="http://www.w3.org/2000/svg">

  <style>
    .bg {{
      fill: #0d1117;
    }}

    .card {{
      fill: {cfg["card"]};
      stroke: {cfg["accent"]};
      stroke-width: 3;
    }}

    .title {{
      fill: {cfg["accent"]};
      font: bold 26px monospace;
    }}

    .text {{
      fill: #c9d1d9;
      font: 18px monospace;
    }}

    .status {{
      fill: {cfg["accent"]};
      font: bold 20px monospace;
    }}

    .small {{
      fill: #8b949e;
      font: 14px monospace;
    }}

    .face {{
      fill: {cfg["accent"]};
      font: bold 25px monospace;
    }}

    .message {{
      fill: {cfg["accent"]};
      font: bold 17px monospace;
    }}
  </style>

  <rect
    class="bg"
    width="720"
    height="460"
    rx="18"
  />

  <rect
    class="card"
    x="20"
    y="20"
    width="680"
    height="420"
    rx="14"
  />

  <text class="title" x="50" y="65">
    🖥️ DEVOPS TAMAGOTCHI
  </text>

  <text class="status" x="50" y="115">
    STATUS     {cfg["icon"]} {cfg["label"]}
  </text>

  <text class="text" x="50" y="155">
    CPU        {cpu_bar}  {state["cpu"]}%
  </text>

  <text class="text" x="50" y="195">
    MEMORY     {memory_bar}  {state["memory"]}%
  </text>

  <text class="text" x="50" y="235">
    UPTIME     {state["uptime_hours"]}h
  </text>

  <text class="text" x="50" y="275">
    INCIDENTS  {state["incidents"]}
  </text>

  <text class="text" x="50" y="315">
    LAST MTTR  {last_mttr}
  </text>

  <text class="text" x="50" y="355">
    AVG MTTR   {average_mttr}
  </text>

  <text class="face" x="430" y="170">
    {cfg["face"]}
  </text>

  <text class="message" x="430" y="215">
    {state["message"]}
  </text>

  <text class="small" x="50" y="405">
    Last check: {updated_display}
  </text>

</svg>
""".strip() + "\n"


# ---------------------------------------------------------
# WRITE NEW VERSIONED SVG
# ---------------------------------------------------------

SVG_FILE.write_text(
    svg,
    encoding="utf-8",
)


# ---------------------------------------------------------
# UPDATE README TO POINT TO NEW ASSET
# ---------------------------------------------------------

if README_FILE.exists():
    readme = README_FILE.read_text(encoding="utf-8")

    new_dashboard_path = (
        f"./assets/dashboard-{dashboard_version}.svg"
    )

    # Replace an already-versioned dashboard filename.
    updated_readme = re.sub(
        r"\./assets/dashboard-[^\"')\s>]+\.svg",
        new_dashboard_path,
        readme,
    )

    # Handle migration from the original fixed filename.
    updated_readme = updated_readme.replace(
        "./assets/dashboard.svg",
        new_dashboard_path,
    )

    README_FILE.write_text(
        updated_readme,
        encoding="utf-8",
    )


# ---------------------------------------------------------
# CLEAN UP OLD GENERATED DASHBOARDS
# ---------------------------------------------------------
#
# Keep only the newly generated dashboard.
# The git commit will record the old one as deleted and
# the new one as added.
# ---------------------------------------------------------

for old_dashboard in ASSETS_DIR.glob("dashboard-*.svg"):
    if old_dashboard != SVG_FILE:
        old_dashboard.unlink()


# ---------------------------------------------------------
# OUTPUT
# ---------------------------------------------------------

mode = "render-only" if args.render_only else "health-check"

print(
    f"[{mode}] "
    f"{cfg['icon']} {cfg['label']} | "
    f"CPU {state['cpu']}% | "
    f"MEM {state['memory']}% | "
    f"LAST MTTR {last_mttr} | "
    f"AVG MTTR {average_mttr}"
)

print(f"Dashboard: {SVG_FILE.name}")
