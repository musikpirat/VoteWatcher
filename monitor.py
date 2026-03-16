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
    """Send a Telegram message and catch errors."""
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg},
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

state = load_state()
state["runs"] += 1

try:
    # Seite abrufen
    r = requests.get(url, timeout=20)
    html_text = r.text

    # Debug: Länge der Seite senden
    send(f"🌐 Seite geladen, Länge: {len(html_text)} Zeichen, Statuscode: {r.status_code}")

    # Robustere Regex: erkennt "ausgezählte Wahllokale: 42 von 87" oder "42 / 87"
    match = re.search(
        r"ausgezählte Wahllokale.*?(\d+)\s*(?:von|/)\s*(\d+)",
        html_text,
        re.IGNORECASE | re.DOTALL
    )

    if not match:
        send("⚠️ Wahlmonitor: Ergebnisse nicht gefunden. HTML möglicherweise geändert.")
        raise Exception("Regex konnte die Wahllokale nicht erkennen")

    current = int(match.group(1))
    total = int(match.group(2))
    last = state["last"]

    # Änderung melden
    if last is not None and current > last:
        send(f"🔔 Neues Wahllokal ausgezählt!\n{current} von {total}\nZeit: {datetime.utcnow()}")

    # Statusnachricht alle 10 Runs
    if state["runs"] % 10 == 0:
        send(f"📊 Status: {current} von {total}\nLetzter Stand: {last}\nRuns: {state['runs']}")

    state["last"] = current
    save_state(state)

except Exception:
    error_text = traceback.format_exc()[:3500]
    send(f"❌ Fehler im Wahlmonitor\n{error_text}")
    # Workflow nicht crashen lassen
    pass

