import requests
import re
import os
import json
import traceback
from datetime import datetime

url = "https://votemanager-da.ekom21cdn.de/2026-03-15/06433007/praesentation/ergebnis.html?wahl_id=769&stimmentyp=0&id=ebene_3_id_97"

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

STATE_FILE = "state.json"


def send(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": msg
            },
            timeout=10
        )
    except Exception as e:
        print("Telegram error:", e)


def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return {"last": None, "runs": 0}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


try:

    state = load_state()
    state["runs"] += 1

    r = requests.get(url, timeout=20)

    match = re.search(r"(\d+)\s*von\s*(\d+)", r.text)

    if not match:
        send("⚠️ Wahlmonitor: Ergebnis nicht gefunden")
        raise Exception("Regex match failed")

    current = int(match.group(1))
    total = int(match.group(2))

    last = state["last"]

    # Änderung melden
    if last is not None and current > last:

        send(
            f"🔔 Neues Wahllokal ausgezählt\n"
            f"{current} von {total}\n"
            f"Zeit: {datetime.utcnow()}"
        )

    # Periodischer Status
    if state["runs"] % 10 == 0:

        send(
            f"📊 Wahlmonitor Status\n"
            f"Aktuell: {current} von {total}\n"
            f"Letzter Stand: {last}\n"
            f"Runs: {state['runs']}"
        )

    state["last"] = current

    save_state(state)

except Exception:

    send(
        "❌ Fehler im Wahlmonitor\n\n"
        + traceback.format_exc()[:3500]
    )

    raise
