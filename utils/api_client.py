import requests
import logging
import os
import requests
import pandas as pd
import logging
from typing import List, Dict, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
class OddsAPIClient:
    def __init__(self, api_key: str):
        """
        Initialize Odds API Client
        
        Args:
            api_key (str): API key for The Odds API
        """
        self.API_KEY = api_key
        self.BASE_URL = 'https://api.the-odds-api.com/v4'
        self.logger = logging.getLogger(__name__)

    def get_available_sports(self) -> List[Dict]:
        """
        Retrieve list of available sports from the API
        
        Returns:
            List of available sports with their keys
        """
        try:
            endpoint = f'{self.BASE_URL}/sports'
            params = {'apiKey': self.API_KEY}
            
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            
            sports = response.json()
            soccer_sports = [sport for sport in sports if 'soccer' in sport['key']]
            
            self.logger.info("Available Soccer Sports:")
            for sport in soccer_sports:
                self.logger.info(f"Key: {sport['key']}, Title: {sport['title']}")
            
            return sports
        
        except requests.RequestException as e:
            self.logger.error(f"Error fetching available sports: {e}")
            return []

    def get_soccer_events(
        self, 
        sport: str = 'soccer_epl',
        region: str = 'us'
    ) -> List[Dict]:
        """
        Fetch current soccer events
        
        Args:
            sport (str): Sport/league identifier
            region (str): Betting region (us, uk, eu)
        
        Returns:
            List of soccer events
        """
        try:
            endpoint = f'{self.BASE_URL}/sports/{sport}/events'
            params = {
                'apiKey': self.API_KEY,
                'regions': region
            }
            
            self.logger.info(f"Fetching events for sport: {sport}")
            
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            
            return response.json()
        
        except requests.RequestException as e:
            self.logger.error(f"Error fetching events for {sport}: {e}")
            raise

    def get_event_odds(
        self, 
        sport: str,
        event_id: str, 
        regions: str = 'us',
        markets: Optional[List[str]] = None,
        date_format: str = 'iso',
        odds_format: str = 'decimal'
    ) -> Dict:
        """
        Fetch odds for a specific event with comprehensive parameter support
        
        Args:
            sport (str): Sport/league identifier (e.g., 'soccer_epl')
            event_id (str): Unique identifier for the event
            regions (str, optional): Betting regions. Defaults to 'us'.
            markets (List[str], optional): List of markets to fetch. Defaults to None.
            date_format (str, optional): Format for dates. Defaults to 'iso'.
            odds_format (str, optional): Format for odds. Defaults to 'decimal'.
        
        Returns:
            Dict: Event odds data
        """
        try:
            # Construct the full endpoint URL
            endpoint = f'{self.BASE_URL}/sports/{sport}/events/{event_id}/odds'
            
            # Prepare query parameters
            params = {
                'apiKey': self.API_KEY,
                'regions': regions,
                'dateFormat': date_format,
                'oddsFormat': odds_format
            }
            
            # Add markets if specified
            if markets:
                params['markets'] = ','.join(markets)
            
            # self.logger.info(f"Fetching odds for event: {event_id} in sport: {sport}")
            # self.logger.info(f"Endpoint: {endpoint}")
            # self.logger.info(f"Parameters: {params}")
            
            # Make the API request
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            
            return response.json()
        
        except requests.RequestException as e:
            self.logger.error(f"Error fetching odds for event {event_id}: {e}")
            
            # Enhanced error logging
            if hasattr(e, 'response'):
                self.logger.error(f"Response Content: {e.response.text}")
            
            raise

    def process_corner_odds_data(self, event_data: Dict) -> pd.DataFrame:
        """
        Process raw corner kick odds data into a structured DataFrame
        
        Args:
            event_data (Dict): Raw event odds data from API
        
        Returns:
            pd.DataFrame: Processed corner kick odds data
        """
        try:
            # Base match information
            processed_data = {
                'match_id': event_data.get('id'),
                'sport_key': event_data.get('sport_key'),
                'sport_title': event_data.get('sport_title'),
                'home_team': event_data.get('home_team', 'Unknown'),
                'away_team': event_data.get('away_team', 'Unknown'),
                'commence_time': event_data.get('commence_time')
            }
            
            # Process bookmaker corner odds
            corner_odds_data = []
            
            for bookmaker in event_data.get('bookmakers', []):
                bookmaker_name = bookmaker.get('title', 'Unknown')
                
                # Find alternate totals corners market
                corner_markets = [
                    market for market in bookmaker.get('markets', []) 
                    if market.get('key') == 'alternate_totals_corners'
                ]
                
                for market in corner_markets:
                    # Process each outcome in the market
                    for outcome in market.get('outcomes', []):
                        corner_odds_entry = processed_data.copy()
                        corner_odds_entry.update({
                            'bookmaker': bookmaker_name,
                            'outcome_name': outcome.get('name'),
                            'corner_point': outcome.get('point'),
                            'odds_price': outcome.get('price'),
                            'market_last_update': market.get('last_update')
                        })
                        corner_odds_data.append(corner_odds_entry)
            
            # Convert to DataFrame
            if corner_odds_data:
                df = pd.DataFrame(corner_odds_data)
                
                # Optional: Pivot or reshape the data as needed
                return df
            else:
                self.logger.warning("No corner odds data found for the event")
                return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"Error processing corner kick odds: {e}")
            return pd.DataFrame()