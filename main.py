import os
import sys
import json
import logging
from pathlib import Path
from collections import deque
import keyboard
import threading

TITLE = "Text Snippets"
SNIPPETS_FILE_PATH = Path(__file__).parent / "snippets.json"
TRIGGER_PREFIX = "@"
BUFFER_MAX_LEN = 100

snippets = {}
snippets_file = None

thread_hook = None
thread_input = None

logging.basicConfig(
    format="%(asctime)s %(levelname)s: %(message)s",
    level=logging.INFO
)

def panic(msg):
    logging.error(msg)
    sys.exit()

def load_snippets_file(path: Path):
    return open(path, "a+", encoding="utf-8")

def load_snippets(file) -> dict:
    file.seek(0)
    content = file.read().strip()
    if not content:
        return {}
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        panic("Error parsing snippets.json: invalid JSON")

def on_key_event(event, buffer: deque, snippets: dict):
    if event.event_type != keyboard.KEY_DOWN or len(event.name) != 1:
        return

    name = event.name
    # print(name)

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

def hook_thread():
    try:
        buffer = deque(maxlen=BUFFER_MAX_LEN)

        keyboard.hook(lambda e: on_key_event(e, buffer, snippets))
        logging.info(f"Use {TRIGGER_PREFIX}key to insert snippets.")
        keyboard.wait()
    except Exception as e:
        panic(f"Hook thread error: {e}")

def input_thread():
    global snippets_file, snippets
    try:
        while True:
            if not input("Press Enter to add a new snippet.") == None:
                key = input("Key: ")
                value = input("Value: ")
                snippets[key] = value

                snippets_file.seek(0)
                snippets_file.truncate()
                # snippets_file.write(json.dumps(snippets, indent=4))
                snippets_file.write("XD")

                logging.info(f"Snippet added: @{key} → {value}")
    except KeyboardInterrupt:
        panic("Input thread exiting.")
    except Exception as e:
        panic(f"Input thread error: {e}")

def thread_exception_handler(error):
    panic("Thread excetion handler")

def main():
    global snippets_file, snippets, thread_hook, thread_input

    os.system(f"title {TITLE}")

    snippets_file = load_snippets_file(SNIPPETS_FILE_PATH)

    snippets = load_snippets(snippets_file)
    if not snippets:
        logging.warning("No snippets loaded.")
    else:
        logging.info(f"Snippets loaded: {snippets}")

    # threading.excepthook = thread_exception_handler

    thread_hook = threading.Thread(target=hook_thread, daemon=True)
    thread_input = threading.Thread(target=input_thread, daemon=True)

    thread_hook.start()
    thread_input.start()

    try:
        thread_hook.join()
        thread_input.join()
    except KeyboardInterrupt:
        panic("Exiting on user interrupt.")
    except Exception as e:
        panic(f"Main thread error: {e}")

if __name__ == "__main__":
    main()
