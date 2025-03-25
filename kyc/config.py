"""Configuration settings for the KYC system."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure OpenAI settings
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15")

# Azure Blob Storage settings
BLOB_CONNECTION_STRING = os.getenv("BLOB_CONNECTION_STRING")
BLOB_INPUT_CONTAINER = "kyc-documents"
BLOB_PROCESSED_CONTAINER = "kyc-processed"
BLOB_RESULTS_CONTAINER = "kyc-results"

# Azure Document Intelligence settings
FR_ENDPOINT = os.getenv("FR_ENDPOINT")
FR_KEY = os.getenv("FR_KEY")

# Agent settings
DEFAULT_TEMPERATURE = 0
DEFAULT_SERVICE_ID = AZURE_OPENAI_DEPLOYMENT_NAME

def validate_config(use_blob_storage=False):
    """Validate that required configuration variables are set."""
    required_vars = [
        "AZURE_OPENAI_ENDPOINT", 
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_DEPLOYMENT_NAME"
    ]
    
    if use_blob_storage:
        required_vars.extend(["BLOB_CONNECTION_STRING", "FR_ENDPOINT", "FR_KEY"])
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")