import pandas as pd
from google.cloud import bigquery
import logging

class DataProcessor:
    """
    Handles data processing and storage operations
    """
    def __init__(self, api_client, cloud_storage):
        """
        Initialize data processor
        
        Args:
            api_client (FootballAPIClient): API client for data retrieval
            cloud_storage (CloudStorageManager): Cloud storage manager
        """
        self.api_client = api_client
        self.cloud_storage = cloud_storage
        self.bq_client = bigquery.Client(
            project=cloud_storage.project_id
        )
        self.logger = logging.getLogger(__name__)

    def fetch_league_standings(self, league_id, season):
        """
        Fetch and process league standings
        
        Args:
            league_id (int): League identifier
            season (int): Football season year
        
        Returns:
            pd.DataFrame: Processed standings data
        """
        try:
            # Fetch raw data
            raw_data = self.api_client.get_league_standings(
                league_id, season
            )
            # Extract standings
            standings = raw_data['response'][0]['league']['standings'][0]

            # Convert to DataFrame
            df = pd.DataFrame([
                {
                    'league_id': league_id,
                    'season': season,
                    'rank': team['rank'],
                    'team_name': team['team']['name'],
                    'team_id': team['team']['id'],
                    'points': team['points'],
                    'played': team['all']['played'],
                    'wins': team['all']['win'],
                    'draws': team['all']['draw'],
                    'losses': team['all']['lose'],
                    'goals_for': team['all']['goals']['for'],
                    'goals_against': team['all']['goals']['against']
                } for team in standings
            ])
            
            return df
        
        except Exception as e:
            self.logger.error(f"Error processing standings: {e}")
            raise

    def store_to_bigquery(self, df, table_name):
        """
        Store DataFrame to BigQuery table
        
        Args:
            df (pd.DataFrame): Data to store
            table_name (str): BigQuery table name
        """
        try:
            dataset_id = 'football_analytics'
            table_id = f'{self.cloud_storage.project_id}.{dataset_id}.{table_name}'
            
            # Create dataset if not exists
            dataset = bigquery.Dataset(f"{self.cloud_storage.project_id}.{dataset_id}")
            self.bq_client.create_dataset(dataset, exists_ok=True)
            
            # Load data to BigQuery
            job_config = bigquery.LoadJobConfig(
                write_disposition='WRITE_APPEND',
            )
            
            job = self.bq_client.load_table_from_dataframe(
                df, table_id, job_config=job_config
            )
            job.result()
            
            self.logger.info(f"Successfully stored data to {table_name}")
        
        except Exception as e:
            self.logger.error(f"BigQuery storage error: {e}")
            raise