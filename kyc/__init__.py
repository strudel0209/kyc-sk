"""KYC Agent System for processing financial documents using AI."""

# Load environment variables at the earliest possible point
import os
from dotenv import load_dotenv

# Try to load from both possible locations
load_dotenv()  # Load from root .env
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))  # Load from kyc/.env

# Now import the system
from kyc.system import KYCAgentSystem

__version__ = "0.1.0"