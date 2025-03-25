"""Azure Blob Storage implementation for KYC data."""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from azure.storage.blob import BlobServiceClient, ContentSettings

from kyc.storage.memory_store import MemoryStore

logger = logging.getLogger(__name__)

class BlobStore(MemoryStore):
    """Azure Blob Storage for client data with in-memory caching."""
    
    def __init__(self, connection_string: Optional[str] = None):
        """Initialize the blob storage."""
        super().__init__()  # Initialize in-memory cache
        
        # Use connection string from environment if not provided
        self.connection_string = connection_string or os.getenv("BLOB_CONNECTION_STRING")
        if not self.connection_string:
            raise ValueError("Blob connection string is required")
        
        # Initialize blob service client
        self.blob_client = BlobServiceClient.from_connection_string(self.connection_string)
        
        # Define container names
        self.client_data_container = "kyc-client-data"
        self.documents_container = "kyc-documents"
        self.results_container = "kyc-results"
        
        # Ensure containers exist
        self._ensure_containers_exist()
        
        logger.info("Initialized blob storage")
    
    def _ensure_containers_exist(self) -> None:
        """Create required containers if they don't exist."""
        containers = [self.client_data_container, self.documents_container, self.results_container]
        
        for container_name in containers:
            container_client = self.blob_client.get_container_client(container_name)
            if not container_client.exists():
                logger.info(f"Creating container: {container_name}")
                container_client.create_container()
    
    def get_client(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get client data by ID, fetching from blob if not in memory."""
        # Try memory first
        client_data = super().get_client(client_id)
        if client_data:
            return client_data
        
        # If not in memory, try to fetch from blob
        try:
            blob_client = self.blob_client.get_blob_client(
                container=self.client_data_container,
                blob=f"{client_id}.json"
            )
            
            if blob_client.exists():
                data = blob_client.download_blob().readall()
                client_data = json.loads(data)
                
                # Update in-memory cache
                self.client_data[client_id] = client_data
                return client_data
            
            return None
        except Exception as e:
            logger.error(f"Error fetching client {client_id} from blob: {str(e)}")
            return None
    
    def update_client(self, client_id: str, data_type: str, data: Dict[str, Any]) -> None:
        """Update client data and persist to blob storage."""
        # Update in-memory first
        super().update_client(client_id, data_type, data)
        
        # Then persist to blob
        try:
            client_data = self.client_data[client_id]
            
            blob_client = self.blob_client.get_blob_client(
                container=self.client_data_container,
                blob=f"{client_id}.json"
            )
            
            # Upload to blob
            blob_client.upload_blob(
                json.dumps(client_data),
                overwrite=True,
                content_settings=ContentSettings(content_type="application/json")
            )
            
            logger.info(f"Persisted {client_id} data to blob storage")
        except Exception as e:
            logger.error(f"Error persisting client {client_id} to blob: {str(e)}")
    
    def list_clients(self) -> List[str]:
        """List all clients from blob storage."""
        try:
            # Get list from blob storage
            container_client = self.blob_client.get_container_client(self.client_data_container)
            blob_list = container_client.list_blobs()
            
            # Extract client IDs from blob names
            client_ids = [blob.name.replace(".json", "") for blob in blob_list]
            
            # Update memory cache with any missing clients
            for client_id in client_ids:
                if client_id not in self.client_data:
                    self.get_client(client_id)  # This will fetch and cache
            
            return client_ids
        except Exception as e:
            logger.error(f"Error listing clients from blob: {str(e)}")
            # Fall back to in-memory list
            return super().list_clients()
    
    def export_data(self) -> Dict[str, Any]:
        """Export all client data, ensuring memory cache is up to date."""
        # Ensure memory cache is current by listing all clients
        self.list_clients()
        return super().export_data()
    
    def import_data(self, data: Dict[str, Any]) -> None:
        """Import client data and persist to blob storage."""
        # Update memory
        super().import_data(data)
        
        # Persist each client to blob
        for client_id, client_data in data.items():
            try:
                blob_client = self.blob_client.get_blob_client(
                    container=self.client_data_container,
                    blob=f"{client_id}.json"
                )
                
                # Upload to blob
                blob_client.upload_blob(
                    json.dumps(client_data),
                    overwrite=True,
                    content_settings=ContentSettings(content_type="application/json")
                )
            except Exception as e:
                logger.error(f"Error importing client {client_id} to blob: {str(e)}")
        
        logger.info(f"Imported and persisted {len(data)} clients to blob storage")