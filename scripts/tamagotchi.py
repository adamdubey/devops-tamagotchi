import json
import random
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = ROOT / "state.json"
SVG_FILE = ROOT / "assets" / "dashboard.svg"

with open(STATE_FILE) as f:
    state = json.load(f)

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

cfg = status_config[state["status"]]

cpu_bar = "█" * (state["cpu"] // 10) + "░" * (10 - state["cpu"] // 10)
mem_bar = "█" * (state["memory"] // 10) + "░" * (10 - state["memory"] // 10)

updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

svg = f"""
<svg width="720" height="390" viewBox="0 0 720 390"
     xmlns="http://www.w3.org/2000/svg">

  <style>
    .bg {{ fill: #0d1117; }}
    .card {{ fill: #161b22; stroke: #30363d; stroke-width: 2; }}
    .title {{ fill: #f0f6fc; font: bold 26px monospace; }}
    .text {{ fill: #c9d1d9; font: 18px monospace; }}
    .small {{ fill: #8b949e; font: 14px monospace; }}
    .face {{ fill: #58a6ff; font: bold 25px monospace; }}
  </style>

  <rect class="bg" width="720" height="390" rx="18"/>
  <rect class="card" x="20" y="20" width="680" height="350" rx="14"/>

  <text class="title" x="50" y="65">
    🖥️ DEVOPS TAMAGOTCHI
  </text>

  <text class="text" x="50" y="115">
    STATUS     {cfg["icon"]} {cfg["label"]}
  </text>

  <text class="text" x="50" y="155">
    CPU        {cpu_bar}  {state["cpu"]}%
  </text>

  <text class="text" x="50" y="195">
    MEMORY     {mem_bar}  {state["memory"]}%
  </text>

  <text class="text" x="50" y="235">
    UPTIME     {state["uptime_hours"]}h
  </text>

  <text class="text" x="50" y="275">
    INCIDENTS  {state["incidents"]}
  </text>

  <text class="face" x="435" y="170">
    {cfg["face"]}
  </text>

  <text class="text" x="430" y="215">
    {state["message"]}
  </text>

  <text class="small" x="50" y="335">
    Last check: {updated}
  </text>

</svg>
"""

SVG_FILE.parent.mkdir(exist_ok=True)

with open(SVG_FILE, "w") as f:
    f.write(svg)

print(
    f"{cfg['icon']} {cfg['label']} | "
    f"CPU {state['cpu']}% | "
    f"MEM {state['memory']}%"
)
