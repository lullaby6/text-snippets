import json
import logging
from pathlib import Path
from collections import deque
import keyboard
import pyperclip

TITLE = "Text Snippets"
CONFIG_FILE = Path(__file__).parent / "config.json"
TRIGGER_PREFIX = "@"
BUFFER_MAX_LEN = 100

logging.basicConfig(
    format="%(asctime)s %(levelname)s: %(message)s",
    level=logging.INFO
)

def load_config(path: Path) -> dict:
    if not path.is_file():
        logging.warning(f"Config file not found: {path}")
        return {}
    try:
        return json.load(path.open("r", encoding="utf-8"))
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing JSON at {path}: {e}")
        return {}

def on_key_event(event, buffer: deque, snippets: dict):
    if event.event_type != keyboard.KEY_DOWN:
        return

    name = event.name

    buffer.append(name)
    if len(buffer) > BUFFER_MAX_LEN:
        buffer.popleft()

    recent = "".join(buffer)
    for key, value in snippets.items():
        trigger = f"{TRIGGER_PREFIX}{key}"
        if recent.endswith(trigger):
            for _ in trigger:
                keyboard.send("backspace")
            
            keyboard.write(value)

            logging.info(f"Replaced {trigger} → {value}")
            buffer.clear()
            break

def main():
    try:
        import os
        os.system(f"title {TITLE}")
    except Exception:
        pass

    snippets = load_config(CONFIG_FILE)
    if not snippets:
        logging.warning("No snippets loaded.")
        return

    logging.info(f"Snippets loaded: {snippets}")

    buffer = deque(maxlen=BUFFER_MAX_LEN)

    keyboard.hook(lambda e: on_key_event(e, buffer, snippets))
    logging.info("Text Snippets enabled. Use @key to insert snippets.")
    keyboard.wait()

if __name__ == "__main__":
    main()
