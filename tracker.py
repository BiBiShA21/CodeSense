import time
import csv
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from pynput import keyboard, mouse
from datetime import datetime

# ── Firebase Setup ────────────────────────────────────────
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# ── Storage ───────────────────────────────────────────────
session_id    = datetime.now().strftime("%Y%m%d_%H%M%S")
session_start = time.time()

window_start  = time.time()
keystrokes    = 0
backspaces    = 0
pauses        = []
mouse_clicks  = 0
last_keypress = None

WINDOW_SECONDS = 30

# ── Helpers ───────────────────────────────────────────────
def save_window():
    global keystrokes, backspaces, pauses, mouse_clicks, window_start

    duration = time.time() - window_start
    if duration == 0:
        return

    typing_speed = keystrokes / duration
    error_rate   = backspaces / max(keystrokes, 1)
    avg_pause    = sum(pauses) / len(pauses) if pauses else 0
    click_rate   = mouse_clicks / duration

    # Save to Firebase
    data = {
        "session_id"   : session_id,
        "timestamp"    : datetime.now().isoformat(),
        "typing_speed" : round(typing_speed, 4),
        "error_rate"   : round(error_rate, 4),
        "avg_pause"    : round(avg_pause, 4),
        "click_rate"   : round(click_rate, 4),
    }

    db.collection("sessions").add(data)

    print(f"[{int(time.time()-session_start)}s] "
          f"speed={typing_speed:.2f}  errors={error_rate:.2f}  "
          f"pause={avg_pause:.2f}  clicks={click_rate:.2f}  "
          f"✅ saved to Firebase!")

    # Also save locally as backup
    os.makedirs("data", exist_ok=True)
    file_exists = os.path.exists("data/sessions.csv")
    with open("data/sessions.csv", "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "timestamp", "typing_speed", "error_rate",
                "avg_pause", "click_rate", "label"
            ])
        writer.writerow([
            data["timestamp"],
            data["typing_speed"],
            data["error_rate"],
            data["avg_pause"],
            data["click_rate"],
            ""
        ])

    # Reset window
    keystrokes   = 0
    backspaces   = 0
    pauses       = []
    mouse_clicks = 0
    window_start = time.time()


# ── Keyboard listener ─────────────────────────────────────
def on_press(key):
    global keystrokes, backspaces, last_keypress, pauses

    now = time.time()

    if last_keypress is not None:
        gap = now - last_keypress
        if gap > 0.3:
            pauses.append(gap)

    last_keypress = now
    keystrokes   += 1

    if key == keyboard.Key.backspace:
        backspaces += 1

    if time.time() - window_start >= WINDOW_SECONDS:
        save_window()


# ── Mouse listener ────────────────────────────────────────
def on_click(x, y, button, pressed):
    global mouse_clicks
    if pressed:
        mouse_clicks += 1


# ── Main ──────────────────────────────────────────────────
if __name__ == "__main__":
    print("🟢 CodeSense tracker started!")
    print(f"   Session ID: {session_id}")
    print(f"   Saving to Firebase + local backup")
    print("   Press Ctrl+C to stop.\n")

    os.makedirs("data", exist_ok=True)

    kb_listener = keyboard.Listener(on_press=on_press)
    ms_listener = mouse.Listener(on_click=on_click)

    kb_listener.start()
    ms_listener.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        save_window()
        print("\n🔴 Tracker stopped!")