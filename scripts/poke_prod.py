import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

STATE_FILE = ROOT / "state.json"
INCIDENTS_FILE = ROOT / "incidents.json"


# ---------------------------------------------------------
# CLI
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# LOAD STATE
# ---------------------------------------------------------

with open(STATE_FILE, encoding="utf-8") as f:
    state = json.load(f)

with open(INCIDENTS_FILE, encoding="utf-8") as f:
    incidents = json.load(f)

now = datetime.now(timezone.utc)


# ---------------------------------------------------------
# INCIDENT HELPERS
# ---------------------------------------------------------

def start_incident(cause, message):
    if state["status"] != "incident":
        state["incidents"] += 1
        state["incident_started_at"] = now.isoformat()

        incidents.append(
            {
                "id": state["incidents"],
                "cause": cause,
                "started_at": now.isoformat(),
                "resolved_at": None,
                "mttr_seconds": None,
            }
        )

    state["status"] = "incident"
    state["message"] = message


def resolve_incident():
    started = state.get("incident_started_at")

    if not started:
        print("No active tracked incident to resolve.")
        return

    started_at = datetime.fromisoformat(started)

    mttr = max(
        0,
        int((now - started_at).total_seconds()),
    )

    state["last_mttr_seconds"] = mttr
    state["incident_started_at"] = None

    for incident in reversed(incidents):
        if incident["resolved_at"] is None:
            incident["resolved_at"] = now.isoformat()
            incident["mttr_seconds"] = mttr
            break

    resolved_times = [
        incident["mttr_seconds"]
        for incident in incidents
        if incident.get("mttr_seconds") is not None
    ]

    if resolved_times:
        state["average_mttr_seconds"] = int(
            sum(resolved_times) / len(resolved_times)
        )


# ---------------------------------------------------------
# ACTIONS
# ---------------------------------------------------------

if args.action == "incident":
    start_incident(
        cause="manual chaos",
        message="somebody poked prod",
    )

    state["cpu"] = 97
    state["memory"] = 96


elif args.action == "cpu":
    start_incident(
        cause="cpu saturation",
        message="CPU has entered another dimension",
    )

    state["cpu"] = 100
    state["memory"] = 62


elif args.action == "memory":
    start_incident(
        cause="memory leak",
        message="memory is disappearing suspiciously",
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


# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------

with open(STATE_FILE, "w", encoding="utf-8") as f:
    json.dump(state, f, indent=2)
    f.write("\n")

with open(INCIDENTS_FILE, "w", encoding="utf-8") as f:
    json.dump(incidents, f, indent=2)
    f.write("\n")


# ---------------------------------------------------------
# OUTPUT
# ---------------------------------------------------------

print(f"Action: {args.action}")
print(f"Status: {state['status']}")
print(f"Message: {state['message']}")
print(f"CPU: {state['cpu']}%")
print(f"Memory: {state['memory']}%")
print(f"Incidents: {state['incidents']}")
print(f"Incident started: {state.get('incident_started_at')}")
print(f"Last MTTR: {state.get('last_mttr_seconds')}")
print(f"Average MTTR: {state.get('average_mttr_seconds')}")