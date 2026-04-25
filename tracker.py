import time
import csv
import os
from pynput import keyboard, mouse

# ── Storage ──────────────────────────────────────────────
events = []
session_start = time.time()

# Per-window stats
window_start     = time.time()
keystrokes       = 0
backspaces       = 0
pauses           = []
mouse_clicks     = 0
last_keypress    = None

WINDOW_SECONDS   = 30   # analyse every 30 seconds
OUTPUT_FILE      = "data/sessions.csv"

# ── Helpers ───────────────────────────────────────────────
def save_window():
    """Calculate features for the last 30s window and save."""
    global keystrokes, backspaces, pauses, mouse_clicks, window_start

    duration = time.time() - window_start
    if duration == 0:
        return

    typing_speed   = keystrokes / duration          # keys per second
    error_rate     = backspaces / max(keystrokes,1) # ratio
    avg_pause      = sum(pauses)/len(pauses) if pauses else 0
    click_rate     = mouse_clicks / duration

    # Write to CSV
    file_exists = os.path.exists(OUTPUT_FILE)
    with open(OUTPUT_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "timestamp","typing_speed","error_rate",
                "avg_pause","click_rate","label"
            ])
        writer.writerow([
            round(time.time(),2),
            round(typing_speed,4),
            round(error_rate,4),
            round(avg_pause,4),
            round(click_rate,4),
            ""   # label is empty — we'll fill later
        ])

    print(f"[{int(time.time()-session_start)}s] "
          f"speed={typing_speed:.2f}  errors={error_rate:.2f}  "
          f"pause={avg_pause:.2f}  clicks={click_rate:.2f}")

    # Reset window
    keystrokes    = 0
    backspaces    = 0
    pauses        = []
    mouse_clicks  = 0
    window_start  = time.time()


# ── Keyboard listener ─────────────────────────────────────
def on_press(key):
    global keystrokes, backspaces, last_keypress, pauses

    now = time.time()

    # Measure pause since last keypress
    if last_keypress is not None:
        gap = now - last_keypress
        if gap > 0.3:          # only count pauses > 300ms
            pauses.append(gap)

    last_keypress = now
    keystrokes   += 1

    if key == keyboard.Key.backspace:
        backspaces += 1

    # Every 30 seconds, save a window
    if time.time() - window_start >= WINDOW_SECONDS:
        save_window()


# ── Mouse listener ────────────────────────────────────────
def on_click(x, y, button, pressed):
    global mouse_clicks
    if pressed:
        mouse_clicks += 1


# ── Main ──────────────────────────────────────────────────
if __name__ == "__main__":
    print("🟢 CodeSense tracker started — just code normally!")
    print(f"   Saving data to: {OUTPUT_FILE}")
    print("   Press  Ctrl+C  to stop.\n")

    os.makedirs("data", exist_ok=True)

    kb_listener = keyboard.Listener(on_press=on_press)
    ms_listener = mouse.Listener(on_click=on_click)

    kb_listener.start()
    ms_listener.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        save_window()   # save the last incomplete window
        print("\n🔴 Tracker stopped. Data saved!")
