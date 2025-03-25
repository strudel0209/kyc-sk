"""Main entry point for the KYC system."""
#test locally th KYC System
# Load environment variables first
import os
from dotenv import load_dotenv
load_dotenv()

print("Environment variables:")
for key in ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_DEPLOYMENT_NAME"]:
    print(f"{key}: {'SET' if os.environ.get(key) else 'MISSING'}")

import asyncio
import json
from kyc.system import KYCAgentSystem

async def main():
    """Run the KYC system."""
    print("Initializing KYC system...")
    system = KYCAgentSystem(use_blob_storage=False)
    
    # Example document to process
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
    
    print("Processing sample document...")
    result = await system.analyze_document(SAMPLE_DOCUMENT, "sample.txt")
    
    print("Result:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())