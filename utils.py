import json

# Save alarms to a JSON file
def save_alarms(alarms):
    with open('data/alarms.json', 'w') as f:
        json.dump(alarms, f)

# Load alarms from a JSON file
def load_alarms():
    try:
        with open('data/alarms.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'CPU': [], 'Memory': [], 'Disk': []}