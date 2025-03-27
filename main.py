import os
import logging
from utils.api_client import FootballAPIClient, OddsAPIClient
from utils.data_processor import DataProcessor
from utils.cloud_storage import CloudStorageManager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Initialize API Client
        api_key_fb = os.getenv('API_FOOTBALL_KEY')
        api_client_fb = FootballAPIClient(api_key_fb)

        api_key_odd = os.getenv('ODDS_API_KEY')
        api_client_odd = OddsAPIClient(api_key_odd)

        # Initialize Cloud Storage
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        cloud_storage = CloudStorageManager(project_id)
        
        # # Initialize Data Processor
        data_processor = DataProcessor(api_client_odd, cloud_storage)

        betting_list = data_processor.fetch_multi_league_corner_odds()
        data_processor.store_to_bigquery(betting_list, 'odd_laliga_epl')
    
    except Exception as e:
        logger.error(f"Critical error in main application: {e}")

if __name__ == '__main__':
    main()