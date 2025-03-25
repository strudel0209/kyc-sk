"""Azure Function for processing KYC documents from blob storage."""

import json
import logging
import azure.functions as func
import os
import sys
import asyncio
from datetime import datetime

# Add the repo root (two directories up) to Python's sys.path so that module "kyc" can be imported.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient

from kyc.system import KYCAgentSystem
from kyc.config import FR_ENDPOINT, FR_KEY, BLOB_CONNECTION_STRING

async def process_document_with_intelligence(blob_content, filename):
    """Process document with Document Intelligence before KYC processing."""
    logging.info(f"Processing document with Document Intelligence: {filename}")
    
    # Initialize Document Intelligence client
    doc_intelligence_client = DocumentIntelligenceClient(
        endpoint=FR_ENDPOINT,
        credential=AzureKeyCredential(FR_KEY)
    )
    
    # Determine if it's a text file or needs OCR
    if filename.lower().endswith('.txt'):
        # For text files, use the content directly
        document_text = blob_content.decode('utf-8')
    else:
        # For non-text files, use Document Intelligence to extract text
        poller = doc_intelligence_client.begin_analyze_document("prebuilt-read", blob_content)
        result = poller.result()
        
        # Extract document content as markdown
        document_text = f"# Document Analysis\n\n"
        
        # Extract content from the result
        if hasattr(result, "content"):
            document_text += result.content
        else:
            # Extract from pages if content not directly available
            for page in result.pages:
                for line in page.lines:
                    document_text += line.content + "\n"
    
    return document_text

async def process_kyc_document(blob_content, filename):
    """Process document through Document Intelligence and KYC system."""
    # First process with Document Intelligence to get text
    document_text = await process_document_with_intelligence(blob_content, filename)
    
    # Initialize KYC system and process the document
    system = KYCAgentSystem(use_blob_storage=True)
    result = await system.analyze_document(document_text, filename)
    
    return result

async def save_result_to_blob(result, filename):
    """Save the analysis result to the results container."""
    try:
        # Initialize blob service client
        blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
        
        # Generate a unique result filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_filename = f"{os.path.splitext(filename)[0]}_{timestamp}_result.json"
        
        # Get a container client for kyc-results
        container_client = blob_service_client.get_container_client("kyc-results")
        
        # Create container if it doesn't exist
        if not container_client.exists():
            container_client.create_container()
            logging.info(f"Created container: kyc-results")
        
        # Get a blob client
        blob_client = container_client.get_blob_client(result_filename)
        
        # Upload the result as JSON
        blob_client.upload_blob(json.dumps(result, indent=2), overwrite=True)
        
        logging.info(f"Saved analysis result to kyc-results/{result_filename}")
        return True
    
    except Exception as e:
        logging.error(f"Error saving result to blob: {str(e)}")
        return False

def main(myblob: func.InputStream):
    """Azure Function entry point - triggered when a new blob is created."""
    logging.info(f"Python blob trigger function processed blob: {myblob.name}")
    
    try:
        # Get blob content
        blob_content = myblob.read()
        filename = myblob.name.split('/')[-1]
        
        # Process document asynchronously
        result = asyncio.run(process_kyc_document(blob_content, filename))
        
        # Log the result summary
        logging.info(f"Document analysis completed for {filename}")
        logging.info(f"Document type: {result.get('document_type', 'Unknown')}")
        logging.info(f"Client: {result.get('client_information', {}).get('client_name', 'Unknown')}")
        
        # Save result to kyc-results container
        asyncio.run(save_result_to_blob(result, filename))
        
        # Optionally move the processed document to a "processed" container
        # This would need additional code to copy the blob and then delete the original
        
    except Exception as e:
        logging.error(f"Error processing document: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())