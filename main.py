import os
import logging
from utils.api_client import FootballAPIClient
from utils.data_processor import DataProcessor
from utils.cloud_storage import CloudStorageManager
from utils.visualization import generate_league_visualizations
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
        api_key = os.getenv('API_FOOTBALL_KEY')
        api_client = FootballAPIClient(api_key)

        # Initialize Cloud Storage
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        cloud_storage = CloudStorageManager(project_id)

        # Initialize Data Processor
        data_processor = DataProcessor(api_client, cloud_storage)

        # Define leagues to analyze
        leagues = [
            {'id': 39, 'name': 'Premier League', 'season': 2023},
            {'id': 140, 'name': 'La Liga', 'season': 2023},
            # {'id': 61, 'name': 'Ligue 1', 'season': 2023}
        ]

        # Analyze each league
        for league in leagues:
            try:
                # Fetch standings
                standings_df = data_processor.fetch_league_standings(
                    league['id'], 
                    league['season']
                )

                # Store to BigQuery
                data_processor.store_to_bigquery(
                    standings_df, 
                    f'standings_{league["name"].lower().replace(" ", "_")}'
                )

                # Generate Visualizations
                generate_league_visualizations(
                    standings_df, 
                    league['name']
                )

                logger.info(f"Successfully processed {league['name']} data")

            except Exception as league_error:
                logger.error(f"Error processing {league['name']}: {league_error}")

    except Exception as e:
        logger.error(f"Critical error in main application: {e}")

if __name__ == '__main__':
    main()