import os
import hashlib
from PyQt6.QtGui import QPixmap

CACHE_DIR = '.cache'

def get_cache_path(poster_path):
    """Generate a unique, safe filename for a given poster path."""
    if not poster_path:
        return None
    # Create a hash of the poster path to use as a filename
    hasher = hashlib.sha1(poster_path.encode('utf-8'))
    filename = f"{hasher.hexdigest()}.jpg"
    return os.path.join(CACHE_DIR, filename)

def get_image_from_cache(poster_path):
    """
    Tries to load a QPixmap from the cache.
    Returns the QPixmap if found, otherwise None.
    """
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    cache_path = get_cache_path(poster_path)
    if cache_path and os.path.exists(cache_path):
        pixmap = QPixmap()
        if pixmap.load(cache_path):
            return pixmap
    return None

def save_image_to_cache(poster_path, image_data):
    """Saves image data to the cache."""
    cache_path = get_cache_path(poster_path)
    if cache_path:
        try:
            with open(cache_path, 'wb') as f:
                f.write(image_data)
        except IOError as e:
            print(f"Error saving image to cache: {e}")

