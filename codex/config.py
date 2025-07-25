import json
import os

CONFIG_FILE = 'config.json'

def save_media_path(path):
    """Saves the media path to the config file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump({'media_path': path}, f)

def load_media_path():
    """Loads the media path from the config file."""
    if not os.path.exists(CONFIG_FILE):
        return None
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return config.get('media_path')
    except (json.JSONDecodeError, IOError):
        return None
