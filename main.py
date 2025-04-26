import keyboard
from os import path, system
from json import loads

title = "Text Snippets"

config = {}
try:
    with open(path.join(path.dirname(__file__), "config.json"), "r") as config_file:
        config = loads(config_file.read())
except: pass

def main():
    system(f"title {title}")

    inputs = ""

    while True:
        event = keyboard.read_event()
        if event.event_type == 'down':
            inputs += event.name
            print(event.name)

            for key, value in config.items():
                if inputs.endswith(f"@{key}"):
                    for _ in range(len(key) + 1):
                        keyboard.send('backspace')

                    keyboard.write(value)

                    inputs = ""

                    print(f"Replaced @{key} with {value}")

if __name__ == "__main__":
    main()
