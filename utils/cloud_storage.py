from google.cloud import storage, bigquery
import logging

class CloudStorageManager:
    """
    Manages interactions with Google Cloud Storage and BigQuery
    """
    def __init__(self, project_id):
        """
        Initialize cloud storage manager
        
        Args:
            project_id (str): Google Cloud Project ID
        """
        self.project_id = project_id
        self.storage_client = storage.Client(project=project_id)
        self.logger = logging.getLogger(__name__)

    def create_bucket(self, bucket_name):
        """
        Create a new Google Cloud Storage bucket
        
        Args:
            bucket_name (str): Name of the bucket to create
        
        Returns:
            google.cloud.storage.Bucket: Created bucket
        """
        try:
            bucket = self.storage_client.create_bucket(
                bucket_name, 
                project=self.project_id
            )
            self.logger.info(f"Bucket {bucket_name} created")
            return bucket
        
        except Exception as e:
            self.logger.error(f"Bucket creation error: {e}")
            raise

    def upload_file(self, bucket_name, source_file, destination_blob_name):
        """
        Upload a file to a Google Cloud Storage bucket
        
        Args:
            bucket_name (str): Name of the bucket
            source_file (str): Path to the local file
            destination_blob_name (str): Destination path in the bucket
        """
        try:
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(destination_blob_name)
            
            blob.upload_from_filename(source_file)
            
            self.logger.info(
                f"File {source_file} uploaded to {destination_blob_name}"
            )
        
        except Exception as e:
            self.logger.error(f"File upload error: {e}")
            raise