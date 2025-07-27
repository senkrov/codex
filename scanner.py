import os
import re

def scan_media(media_path):
    """
    Scans the given media path for movies and shows based on the expected directory structure.
    """
    movies_path = os.path.join(media_path, 'movies')
    shows_path = os.path.join(media_path, 'shows')

    movies = []
    if os.path.exists(movies_path):
        for item in os.listdir(movies_path):
            item_path = os.path.join(movies_path, item)
            if os.path.isfile(item_path) and item.lower().endswith(('.mp4', '.mkv', '.avi')):
                filename = os.path.splitext(item)[0]
                
                match = re.match(r'^(.*) \((\d{4})\)$', filename)
                if match:
                    title = match.group(1).replace('.', ' ').strip()
                    year = int(match.group(2))
                else:
                    title = filename.replace('.', ' ').strip()
                    year = None

                movie_data = {
                    'title': title,
                    'year': year,
                    'path': item_path
                }
                movies.append(movie_data)

    shows = []
    if os.path.exists(shows_path):
        for show_dir in os.listdir(shows_path):
            show_path = os.path.join(shows_path, show_dir)
            if os.path.isdir(show_path):
                seasons = []
                for season_dir in os.listdir(show_path):
                    if os.path.isdir(os.path.join(show_path, season_dir)) and season_dir.lower().startswith('season'):
                        episodes = []
                        season_path = os.path.join(show_path, season_dir)
                        for episode_file in os.listdir(season_path):
                            if episode_file.lower().endswith(('.mkv', '.mp4', '.avi')):
                                episode_path = os.path.join(season_path, episode_file)
                                episode_name = os.path.splitext(episode_file)[0]
                                
                                # Attempt to parse episode number and name from filename
                                match = re.match(r'.*s(\d+)e(\d+).*', episode_name, re.I)
                                if match:
                                    episode_number = int(match.group(2))
                                    # Try to extract a clean name, otherwise fall back
                                    name_match = re.search(r'-\s*(.*)', episode_name)
                                    if name_match:
                                        name = name_match.group(1)
                                    else:
                                        name = episode_name
                                else:
                                    episode_number = None
                                    name = episode_name

                                episodes.append({
                                    'episode_number': episode_number,
                                    'name': name,
                                    'path': episode_path
                                })
                        seasons.append({'name': season_dir, 'episodes': episodes})
                if seasons:
                    show_data = {'title': show_dir, 'path': show_path, 'seasons': seasons}
                    shows.append(show_data)

    return movies, shows