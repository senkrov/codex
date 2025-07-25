import os
import re

def scan_media(media_path):
    """
    Scans the given media path for movies and shows based on the expected directory structure.
    """
    movies_path = os.path.join(media_path, 'movies')
    shows_path = os.path.join(media_path, 'shows')
    print(f"Scanning for shows in: {shows_path}")

    movies = []
    if os.path.exists(movies_path):
        for movie_dir in os.listdir(movies_path):
            match = re.match(r'(.+) \((\d{4})\)', movie_dir)
            if match:
                movies.append({
                    'title': match.group(1).strip(),
                    'year': int(match.group(2)),
                    'path': os.path.join(movies_path, movie_dir)
                })

    shows = []
    if os.path.exists(shows_path):
        for show_dir in os.listdir(shows_path):
            print(f"Found potential show directory: {show_dir}")
            show_path = os.path.join(shows_path, show_dir)
            if os.path.isdir(show_path):
                print(f"Confirmed directory: {show_path}")
                seasons = []
                for season_dir in os.listdir(show_path):
                    print(f"  Found potential season directory: {season_dir}")
                    if os.path.isdir(os.path.join(show_path, season_dir)) and season_dir.lower().startswith('season'):
                        print(f"  Confirmed season directory: {season_dir}")
                        episodes = []
                        season_path = os.path.join(show_path, season_dir)
                        for episode_file in os.listdir(season_path):
                            if episode_file.lower().endswith(('.mkv', '.mp4', '.avi')):
                                episodes.append(episode_file)
                        seasons.append({'name': season_dir, 'episodes': episodes})
                if seasons:
                    shows.append({'title': show_dir, 'path': show_path, 'seasons': seasons})
                    print(f"Added show '{show_dir}' with {len(seasons)} seasons.")

    return movies, shows

if __name__ == '__main__':
    media_directory = '.' 
    
    if not os.path.exists('movies/Inception (2010)'):
        os.makedirs('movies/Inception (2010)')
    if not os.path.exists('shows/Breaking Bad/Season 01'):
        os.makedirs('shows/Breaking Bad/Season 01')

    movies, shows = scan_media(media_directory)
    print("\n--- Scan Results ---")
    print("Movies found:")
    for movie in movies:
        print(f"  - {movie['title']} ({movie['year']})")

    print("\nShows found:")
    for show in shows:
        print(f"  - {show['title']}")
        for season in show['seasons']:
            print(f"    - {season['name']} ({len(season['episodes'])} episodes)")
