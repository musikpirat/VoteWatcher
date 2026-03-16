import requests
import re
import os
import json

url = "https://votemanager-da.ekom21cdn.de/2026-03-15/06433007/praesentation/ergebnis.html?wahl_id=769&stimmentyp=0&id=ebene_3_id_97"

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

STATE_FILE = "state.json"

def load_last():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)["last"]
    except:
        return None

def save_last(value):
    with open(STATE_FILE,"w") as f:
        json.dump({"last":value},f)

def send(msg):

    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": msg
        }
    )

r = requests.get(url)

match = re.search(r"(\d+)\s*von\s*(\d+)", r.text)

if match:

    current = int(match.group(1))
    total = int(match.group(2))

    last = load_last()

    if last is not None and current > last:

        send(f"🔔 Neues Wahllokal ausgezählt\n{current} von {total}")

    save_last(current)
