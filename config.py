import json
import os

import json
import os

CONFIG_FILE_NAME = 'config.json'
CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), CONFIG_FILE_NAME)

def save_media_path(path):
    """Saves the media path to the config file."""
    with open(CONFIG_FILE_PATH, 'w') as f:
        json.dump({'media_path': path}, f)

def load_media_path():
    """Loads the media path from the config file."""
    if not os.path.exists(CONFIG_FILE_PATH):
        return None
    try:
        with open(CONFIG_FILE_PATH, 'r') as f:
            config = json.load(f)
            return config.get('media_path')
    except (json.JSONDecodeError, IOError):
        return None
