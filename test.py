import os
import json
import logging
from pathlib import Path
from collections import deque
import keyboard

TITLE = "Text Snippets"
SNIPPETS_FILE_PATH = Path(__file__).parent / "snippets.json"
TRIGGER_PREFIX = "@"
BUFFER_MAX_LEN = 100

logging.basicConfig(
    format="%(asctime)s %(levelname)s: %(message)s",
    level=logging.INFO
)

def load_snippets_file(path: Path):
    file = open(path, "a+", encoding="utf-8")
    return file

def load_snippets(file) -> dict:
    try:
        return json.load(file.read())
    except json.JSONDecodeError:
        # file.truncate(0)
        # file.seek(0)
        # file.write("{}")
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
    os.system(f"title {TITLE}")

    snippets_file = load_snippets_file(SNIPPETS_FILE_PATH)

    snippets = load_snippets(snippets_file)
    print(snippets)
    if not snippets:
        logging.warning("No snippets loaded.")
    else:
        logging.info(f"Snippets loaded: {snippets}")

    buffer = deque(maxlen=BUFFER_MAX_LEN)

    keyboard.hook(lambda e: on_key_event(e, buffer, snippets))
    logging.info("Text Snippets enabled. Use @key to insert snippets.")
    keyboard.wait()

if __name__ == "__main__":
    main()
