import subprocess
import json
from urllib.parse import urlencode
import os

class TMDbAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://api.themoviedb.org/3'

    def _get(self, endpoint, params=None):
        if params is None:
            params = {}

        params['api_key'] = self.api_key

        try:
            base_url = f"{self.base_url}/{endpoint.lstrip('/')}"
            
            if params:
                url = f"{base_url}?{urlencode(params)}"
            else:
                url = base_url

            curl_cmd = ['curl', '-X', 'GET', url]
            
            result = subprocess.run(curl_cmd, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"Error executing curl: {result.stderr}")
                return None
            
            return json.loads(result.stdout)

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def search_movie(self, title, year=None):
        """Search for a movie by title and optionally year."""
        params = {'query': title}
        if year:
            params['year'] = year
        return self._get('/search/movie', params)

    def get_movie_details(self, movie_id):
        """Get details for a specific movie."""
        return self._get(f'/movie/{movie_id}')

    def search_show(self, title):
        """Search for a show by title."""
        params = {'query': title}
        return self._get('/search/tv', params)

    def get_show_details(self, show_id):
        """Get details for a specific show."""
        return self._get(f'/tv/{show_id}')
    
    def get_show_season_details(self, show_id, season_number):
        """Get details for a specific season of a show."""
        return self._get(f'/tv/{show_id}/season/{season_number}')


if __name__ == '__main__':
    # This is for testing the TMDb API wrapper directly.
    # You need to have a TMDb API key set as an environment variable named TMDB_API_KEY
    # or replace it manually.
    api_key = os.environ.get('TMDB_API_KEY', '1d1f855c79a956515f6438990b93f65b')
    if not api_key:
        print("Please set the TMDB_API_KEY environment variable.")
    else:
        tmdb = TMDbAPI(api_key)

        # Test movie search
        print("Searching for movie 'Inception' (2010)...")
        movies_data = tmdb.search_movie('Inception', 2010)
        if movies_data and 'results' in movies_data and movies_data['results']:
            movie_id = movies_data['results'][0]['id']
            print(f"Found movie with ID: {movie_id}")
            movie_details = tmdb.get_movie_details(movie_id)
            if movie_details:
                print(f"Movie details: {movie_details['title']}, Poster path: {movie_details['poster_path']}")
        else:
            print("Movie not found.")
            if movies_data:
                print(f"Response from server: {movies_data}")


        print("\n" + "="*20 + "\n")

        # Test show search
        print("Searching for show 'Breaking Bad'...")
        shows_data = tmdb.search_show('Breaking Bad')
        if shows_data and 'results' in shows_data and shows_data['results']:
            show_id = shows_data['results'][0]['id']
            print(f"Found show with ID: {show_id}")
            show_details = tmdb.get_show_details(show_id)
            if show_details:
                print(f"Show details: {show_details['name']}, Poster path: {show_details['poster_path']}")
            
            # Test season details
            season_details = tmdb.get_show_season_details(show_id, 1)
            if season_details:
                print(f"Season 1 details: {len(season_details['episodes'])} episodes")

        else:
            print("Show not found.")
            if shows_data:
                print(f"Response from server: {shows_data}")