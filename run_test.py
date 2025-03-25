"""Test script to run the KYC system with a sample document."""

import os
from dotenv import load_dotenv
load_dotenv()
print("Environment variables:")
for key in ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_DEPLOYMENT_NAME"]:
    print(f"{key}: {'SET' if os.environ.get(key) else 'MISSING'}")
import asyncio
import json
from kyc.system import KYCAgentSystem

# Sample document for testing
SAMPLE_DOCUMENT = """
Bank Statement
Account Holder: John Smith
Account Number: 12345678
Date: 2023-01-15

Opening Balance: $10,000.00
Deposits: $5,000.00
Withdrawals: $2,500.00
Closing Balance: $12,500.00
"""

async def test_kyc_system():
    """Run a test against the KYC system."""
    # Load environment variables from .env file 
    # (already done by the system, but explicit here for clarity)
    
    print("Initializing KYC system...")
    system = KYCAgentSystem(use_blob_storage=False)
    
    print("Analyzing sample document...")
    result = await system.analyze_document(SAMPLE_DOCUMENT, "sample_bank_statement.txt")
    
    # Print results
    print("\nDocument Analysis Results:")
    print(json.dumps(result, indent=2))
    
    return result

if __name__ == "__main__":
    # Run the test with error handling
    try:
        print("Starting test...")
        asyncio.run(test_kyc_system())
        print("Test completed successfully")
    except Exception as e:
        import traceback
        print(f"Error occurred: {e}")
        traceback.print_exc()
