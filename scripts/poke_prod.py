import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = ROOT / "state.json"
INCIDENTS_FILE = ROOT / "incidents.json"

parser = argparse.ArgumentParser()
parser.add_argument(
    "action",
    choices=[
        "incident",
        "cpu",
        "memory",
        "heal",
        "feed",
    ],
)

args = parser.parse_args()

with open(STATE_FILE) as f:
    state = json.load(f)

with open(INCIDENTS_FILE) as f:
    incidents = json.load(f)

now = datetime.now(timezone.utc)


def start_incident(cause: str, message: str):
    if state["status"] != "incident":
        state["incidents"] += 1
        state["incident_started_at"] = now.isoformat()

        incidents.append({
            "id": state["incidents"],
            "cause": cause,
            "started_at": now.isoformat(),
            "resolved_at": None,
            "mttr_seconds": None
        })

    state["status"] = "incident"
    state["message"] = message


def resolve_incident():
    started = state.get("incident_started_at")

    if not started:
        return

    started_at = datetime.fromisoformat(started)
    mttr = int((now - started_at).total_seconds())

    state["last_mttr_seconds"] = mttr
    state["incident_started_at"] = None

    for incident in reversed(incidents):
        if incident["resolved_at"] is None:
            incident["resolved_at"] = now.isoformat()
            incident["mttr_seconds"] = mttr
            break

    resolved_times = [
        item["mttr_seconds"]
        for item in incidents
        if item["mttr_seconds"] is not None
    ]

    if resolved_times:
        state["average_mttr_seconds"] = int(
            sum(resolved_times) / len(resolved_times)
        )


if args.action == "incident":
    start_incident(
        "manual chaos",
        "somebody poked prod"
    )
    state["cpu"] = 97
    state["memory"] = 96

elif args.action == "cpu":
    start_incident(
        "cpu saturation",
        "CPU has entered another dimension"
    )
    state["cpu"] = 100
    state["memory"] = 62

elif args.action == "memory":
    start_incident(
        "memory leak",
        "memory is disappearing suspiciously"
    )
    state["cpu"] = 54
    state["memory"] = 99

elif args.action == "heal":
    resolve_incident()

    state["status"] = "healthy"
    state["cpu"] = 21
    state["memory"] = 37
    state["message"] = "server has recovered"

elif args.action == "feed":
    if state["status"] == "incident":
        state["message"] = "snacks cannot fix production"
    else:
        state["status"] = "healthy"
        state["cpu"] = max(5, state["cpu"] - 10)
        state["memory"] = max(10, state["memory"] - 10)
        state["message"] = "server has been fed 🍪"

with open(STATE_FILE, "w") as f:
    json.dump(state, f, indent=2)

with open(INCIDENTS_FILE, "w") as f:
    json.dump(incidents, f, indent=2)

print(f"Action: {args.action}")
print(f"Status: {state['status']}")
print(f"Message: {state['message']}")
