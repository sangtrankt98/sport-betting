import requests
import logging

class FootballAPIClient:
    """
    Handles API interactions with Football API
    """
    def __init__(self, api_key):
        """
        Initialize API client with authentication
        
        Args:
            api_key (str): API key for authentication
        """
        self.API_KEY = api_key
        self.BASE_URL = 'https://v3.football.api-sports.io'
        self.headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': self.API_KEY
        }
        self.logger = logging.getLogger(__name__)

    def get_league_standings(self, league_id, season):
        """
        Fetch league standings for a specific season
        
        Args:
            league_id (int): Unique identifier for the league
            season (int): Year of the season
        
        Returns:
            dict: API response with league standings
        """
        try:
            endpoint = f'{self.BASE_URL}/standings'
            params = {
                'league': league_id,
                'season': season
            }
            
            response = requests.get(
                endpoint, 
                headers=self.headers, 
                params=params
            )
            response.raise_for_status()  # Raise exception for bad responses
            return response.json()
        
        except requests.RequestException as e:
            self.logger.error(f"API Request Error: {e}")
            raise