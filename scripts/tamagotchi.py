import argparse
import json
import random
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = ROOT / "state.json"
SVG_FILE = ROOT / "assets" / "dashboard.svg"

parser = argparse.ArgumentParser()
parser.add_argument(
    "--render-only",
    action="store_true",
    help="Render the dashboard without mutating Tamagotchi state",
)
args = parser.parse_args()


def format_duration(seconds):
    if seconds is None:
        return "N/A"

    if seconds < 60:
        return f"{seconds}s"

    minutes = seconds // 60
    remaining_seconds = seconds % 60

    return f"{minutes}m {remaining_seconds}s"


with open(STATE_FILE) as f:
    state = json.load(f)


# ---------------------------------------------------------
# NORMAL HEALTH CHECK
# ---------------------------------------------------------
# When --render-only is NOT supplied, simulate the next
# health-check cycle and mutate state.
#
# When --render-only IS supplied, leave state untouched and
# only regenerate the SVG dashboard.
# ---------------------------------------------------------

if not args.render_only:
    roll = random.random()

    if roll < 0.08:
        state["status"] = "incident"
        state["incidents"] += 1
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

    else:
        state["cpu"] = random.randint(90, 100)
        state["memory"] = random.randint(90, 100)

    state["uptime_hours"] += 1

    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


# ---------------------------------------------------------
# DASHBOARD DISPLAY CONFIG
# ---------------------------------------------------------

status_config = {
    "healthy": {
        "icon": "🟢",
        "label": "HEALTHY",
        "face": "(づ ◕‿◕ )づ",
    },
    "degraded": {
        "icon": "🟡",
        "label": "DEGRADED",
        "face": "(・_・;)",
    },
    "incident": {
        "icon": "🔴",
        "label": "INCIDENT",
        "face": "(╯°□°)╯︵ ┻━┻",
    },
}

cfg = status_config.get(
    state["status"],
    {
        "icon": "⚪",
        "label": "UNKNOWN",
        "face": "(?_?)",
    },
)


# ---------------------------------------------------------
# METRIC FORMATTING
# ---------------------------------------------------------

cpu_segments = min(10, max(0, state["cpu"] // 10))
memory_segments = min(10, max(0, state["memory"] // 10))

cpu_bar = "█" * cpu_segments + "░" * (10 - cpu_segments)
mem_bar = "█" * memory_segments + "░" * (10 - memory_segments)

last_mttr = format_duration(state.get("last_mttr_seconds"))
avg_mttr = format_duration(state.get("average_mttr_seconds"))

updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


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
      fill: #161b22;
      stroke: #30363d;
      stroke-width: 2;
    }}

    .title {{
      fill: #f0f6fc;
      font: bold 26px monospace;
    }}

    .text {{
      fill: #c9d1d9;
      font: 18px monospace;
    }}

    .small {{
      fill: #8b949e;
      font: 14px monospace;
    }}

    .face {{
      fill: #58a6ff;
      font: bold 25px monospace;
    }}
  </style>

  <rect class="bg"
        width="720"
        height="460"
        rx="18"/>

  <rect class="card"
        x="20"
        y="20"
        width="680"
        height="420"
        rx="14"/>

  <text class="title"
        x="50"
        y="65">
    🖥️ DEVOPS TAMAGOTCHI
  </text>

  <text class="text"
        x="50"
        y="115">
    STATUS     {cfg["icon"]} {cfg["label"]}
  </text>

  <text class="text"
        x="50"
        y="155">
    CPU        {cpu_bar}  {state["cpu"]}%
  </text>

  <text class="text"
        x="50"
        y="195">
    MEMORY     {mem_bar}  {state["memory"]}%
  </text>

  <text class="text"
        x="50"
        y="235">
    UPTIME     {state["uptime_hours"]}h
  </text>

  <text class="text"
        x="50"
        y="275">
    INCIDENTS  {state["incidents"]}
  </text>

  <text class="text"
        x="50"
        y="315">
    LAST MTTR  {last_mttr}
  </text>

  <text class="text"
        x="50"
        y="355">
    AVG MTTR   {avg_mttr}
  </text>

  <text class="face"
        x="430"
        y="170">
    {cfg["face"]}
  </text>

  <text class="text"
        x="430"
        y="215">
    {state["message"]}
  </text>

  <text class="small"
        x="50"
        y="405">
    Last check: {updated}
  </text>

</svg>
"""


# ---------------------------------------------------------
# WRITE SVG
# ---------------------------------------------------------

SVG_FILE.parent.mkdir(parents=True, exist_ok=True)

with open(SVG_FILE, "w") as f:
    f.write(svg)


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
    f"AVG MTTR {avg_mttr}"
)
