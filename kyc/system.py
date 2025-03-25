"""Main KYC Agent System implementation."""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion import AzureChatCompletion
from semantic_kernel.functions import KernelArguments
from semantic_kernel.memory import VolatileMemoryStore
from semantic_kernel.planners import SequentialPlanner

from kyc.config import (
    AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT_NAME,
    AZURE_OPENAI_API_VERSION, validate_config
)
from kyc.utils import safe_json_loads, normalize_client_name, logger
from kyc.agents.client_agent import ClientIdentificationAgent
from kyc.agents.classification_agent import DocumentClassificationAgent
from kyc.agents.asset_agent import AssetIdentificationAgent
from kyc.agents.liability_agent import LiabilityIdentificationAgent
from kyc.agents.currency_agent import CurrencyNormalizationAgent
from kyc.agents.multilingual_agent import MultilingualAgent
from kyc.agents.networth_agent import NetWorthCalculatorAgent
from kyc.agents.financial_overview_agent import FinancialOverviewAgent

class KYCAgentSystem:
    """
    KYC processing system using specialized agents to handle different aspects
    of document processing and financial data extraction.
    """
    
    def __init__(self, use_blob_storage: bool = False):
        """Initialize the KYC Agent System."""
        self.use_blob_storage = use_blob_storage
        
        # Validate configuration
        validate_config(use_blob_storage)
        
        # Initialize services
        self._init_azure_services()
        self._init_semantic_kernel()
        self._init_memory_store()
        self._register_agents()
        
        # Client data store (in-memory for this example)
        # In production, this would be a database
        self.client_data_store = {}
        
        logger.info("KYC Agent System initialized successfully")
    
    def _init_azure_services(self):
        """Initialize Azure services based on configuration."""
        if self.use_blob_storage:
            # Import services lazily to avoid dependencies if not needed
            from azure.storage.blob import BlobServiceClient
            from azure.ai.documentintelligence import DocumentIntelligenceClient
            from azure.core.credentials import AzureKeyCredential
            
            # Initialize Blob Storage
            self.blob_client = BlobServiceClient.from_connection_string(
                os.getenv("BLOB_CONNECTION_STRING")
            )
            
            # Initialize Document Intelligence
            self.doc_intelligence = DocumentIntelligenceClient(
                endpoint=os.getenv("FR_ENDPOINT"),
                credential=AzureKeyCredential(os.getenv("FR_KEY"))
            )
            
            # Define container names
            self.input_container = "kyc-documents"
            self.processed_container = "kyc-processed"
            self.results_container = "kyc-results"
        
        logger.info("Azure services initialized")
    
    def _init_semantic_kernel(self):
        """Initialize Semantic Kernel with Azure OpenAI."""
        self.kernel = Kernel()
        
        # Initialize Azure OpenAI service
        chat_service = AzureChatCompletion(
            service_id=AZURE_OPENAI_DEPLOYMENT_NAME,
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            endpoint=AZURE_OPENAI_ENDPOINT,
            deployment_name=AZURE_OPENAI_DEPLOYMENT_NAME
        )
        
        self.kernel.add_service(chat_service)
        logger.info(f"Semantic Kernel initialized with {AZURE_OPENAI_DEPLOYMENT_NAME}")
        
        # Initialize planners
        self.sequential_planner = SequentialPlanner(self.kernel, 
                                                  service_id=AZURE_OPENAI_DEPLOYMENT_NAME)
    
    def _init_memory_store(self):
        """Initialize memory for maintaining context between agents."""
        logger.info("Using simplified memory store approach")
        # Use a simple dictionary as memory since we don't need embeddings
        self.memory = {}
        self.memory_initialized = True
    
    def _register_agents(self):
        """Register all agent functions with the kernel."""
        # Create and initialize all agents
        self.client_agent = ClientIdentificationAgent(self.kernel)
        self.doc_classification_agent = DocumentClassificationAgent(self.kernel)
        self.asset_agent = AssetIdentificationAgent(self.kernel)
        self.liability_agent = LiabilityIdentificationAgent(self.kernel)
        self.currency_agent = CurrencyNormalizationAgent(self.kernel)
        self.multilingual_agent = MultilingualAgent(self.kernel)
        self.networth_agent = NetWorthCalculatorAgent(self.kernel)
        self.overview_agent = FinancialOverviewAgent(self.kernel)
        
        logger.info("All agents registered with the kernel")
    
    # The system methods that use these agents (analyze_document, extract_client_info, etc.)
    
    async def invoke_agent_function(self, plugin_name: str, function_name: str, **kwargs) -> Any:
        """Helper method to invoke agent functions with proper arguments."""
        # Create KernelArguments from kwargs
        args = KernelArguments()
        for key, value in kwargs.items():
            args[key] = value
        
        # Invoke the function
        result = await self.kernel.invoke(
            plugin_name=plugin_name,
            function_name=function_name,
            arguments=args
        )
        
        return result
    
    async def analyze_document(self, document_content: str, document_name: str) -> Dict[str, Any]:
        """
        Process a document to extract all relevant financial information.
        
        This is the main entry point for document processing. It orchestrates
        all the other functions to fully analyze a document.
        
        Args:
            document_content: The text content of the document
            document_name: A name/identifier for the document
            
        Returns:
            Dictionary with extracted information including client info,
            document type, and financial data
        """
        try:
            logger.info(f"Starting document analysis: {document_name}")
            
            # 1. Detect language
            language_info = await self.detect_document_language(document_content)
            language_code = language_info.get("language_code", "en")
            
            # 2. Translate if needed
            document_for_processing = document_content
            if (language_code != "en"):
                logger.info(f"Document in {language_info.get('primary_language', 'non-English')}, translating key information")
                translated_content = await self.translate_document(document_content, language_code)
                # For non-English documents, we'll use both the original and translated content
                document_for_processing = translated_content
            
            # 3. Extract client information
            client_info = await self.extract_client_info(document_content, language_code)
            client_id = client_info.get("client_id", "UNKNOWN")
            logger.info(f"Identified client: {client_id}")
            
            # 4. Classify document
            document_type = await self.classify_document(document_content, language_code)
            logger.info(f"Document classified as: {document_type}")
            
            # Invoke the overview agent
            overview_response = await self.invoke_agent_function(
                plugin_name="FinancialOverviewAgent",
                function_name="ExtractOverview",
                document=document_for_processing
            )
            
            try:
                overview_data = json.loads(str(overview_response))
            except json.JSONDecodeError:
                overview_data = {}
                logger.error("Failed to parse financial overview result.")
            
            # Update client data store based on the overview agent output:
            # The helper function expects a JSON keyed by client names.
            self.update_client_data_from_overview(overview_data)
            
            # Now calculate net worth for each client found in the overview:
            client_net_worths = {}
            for client_name in overview_data.keys():
                client_net_worths[client_name] = await self.calculate_net_worth(client_name)
            
            # For this example, you could either combine the net worths or return them as separate entries.
            # Here we add them to our final result under 'net_worths'
            net_worth_result = {
                "combined_net_worth": sum(nw.get("net_worth", 0) for nw in client_net_worths.values()),
                "individual_net_worth": client_net_worths
            }
            
            logger.info(f"Document analysis completed successfully: {document_name}")
            
            return {
                "document_name": document_name,
                "document_type": document_type,
                "language": language_info,
                "client_information": client_info,
                "financial_data": overview_data,
                "net_worth": net_worth_result
            }
            
        except Exception as e:
            logger.error(f"Error analyzing document {document_name}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Return error information
            return {
                "document_name": document_name,
                "error": str(e),
                "error_type": type(e).__name__,
                "status": "failed"
            }
    
    async def detect_document_language(self, document_content: str) -> Dict[str, Any]:
        """Detect the language of a document."""
        # Use only the first 1000 characters for language detection
        document_sample = document_content[:1000]
        
        result = await self.invoke_agent_function(
            plugin_name="MultilingualAgent",
            function_name="DetectLanguage",
            document_sample=document_sample
        )
        
        try:
            language_info = json.loads(str(result))
            return language_info
        except json.JSONDecodeError:
            # Return default if parsing fails
            return {
                "primary_language": "English",
                "language_code": "en",
                "confidence": "low"
            }
    
    async def translate_document(self, document_content: str, source_language: str) -> str:
        """Translate document to English for processing."""
        result = await self.invoke_agent_function(
            plugin_name="MultilingualAgent",
            function_name="TranslateFinancialDocument",
            document=document_content,
            source_language=source_language
        )
        
        return str(result)
    
    async def extract_client_info(self, document_content: str, language_code: str) -> Dict[str, Any]:
        """Extract client identification information."""
        if (language_code == "en"):
            result = await self.invoke_agent_function(
                plugin_name="ClientIdentificationAgent",
                function_name="ExtractClientIdentifier",
                document=document_content
            )
        else:
            result = await self.invoke_agent_function(
                plugin_name="ClientIdentificationAgent",
                function_name="ExtractMultilingualClientIdentifier",
                document=document_content,
                language=language_code
            )
        
        try:
            client_info = json.loads(str(result))
            
            # Add a normalized client name field for reconciliation
            if "client_name" in client_info and client_info["client_name"]:
                # Normalize name (lowercase, remove extra spaces, etc.)
                normalized_name = normalize_client_name(client_info["client_name"])
                client_info["normalized_name"] = normalized_name
                
                # Use normalized name as primary key if we don't have a better ID
                if client_info.get("client_id") == "UNKNOWN" or "PROP-" in client_info.get("client_id", ""):
                    client_info["client_id"] = f"NAME-{normalized_name}"
            
            return client_info
        except json.JSONDecodeError:
            # Return default if parsing fails
            return {
                "client_id": "UNKNOWN",
                "client_name": "UNKNOWN",
                "confidence": "low"
            }
    
    async def classify_document(self, document_content: str, language_code: str) -> str:
        """Classify the document into a financial category."""
        if language_code == "en":
            result = await self.invoke_agent_function(
                plugin_name="DocumentClassificationAgent",
                function_name="ClassifyFinancialDocument",
                document=document_content
            )
        else:
            result = await self.invoke_agent_function(
                plugin_name="DocumentClassificationAgent",
                function_name="ClassifyMultilingualDocument",
                document=document_content,
                language=language_code
            )
        
        # The classification returns just the category name as text
        return str(result).strip()
    
    async def extract_assets(self, document_content: str, document_type: str) -> Dict[str, Any]:
        """Extract asset information from a document."""
        # Extract table data if available
        tables = ""  # In a real implementation, this would extract tables
        
        result = await self.invoke_agent_function(
            plugin_name="AssetIdentificationAgent",
            function_name="ExtractAssets",
            document=document_content,
            document_type=document_type,
            tables=tables
        )
        
        try:
            assets_data = json.loads(str(result))
            return assets_data
        except json.JSONDecodeError:
            # Return minimal structure if parsing fails
            return {
                "total_assets_value": 0,
                "currency": "USD",
                "assets": []
            }
    
    async def extract_liabilities(self, document_content: str, document_type: str) -> Dict[str, Any]:
        """Extract liability information from a document."""
        # Extract table data if available
        tables = ""  # In a real implementation, this would extract tables
        
        result = await self.invoke_agent_function(
            plugin_name="LiabilityIdentificationAgent",
            function_name="ExtractLiabilities",
            document=document_content,
            document_type=document_type,
            tables=tables
        )
        
        try:
            liabilities_data = json.loads(str(result))
            return liabilities_data
        except json.JSONDecodeError:
            # Return minimal structure if parsing fails
            return {
                "total_liabilities_value": 0,
                "currency": "USD",
                "liabilities": []
            }
    
    async def normalize_currency(self, values: List[str], target_currency: str = "USD") -> Dict[str, Any]:
        """Normalize currency values to a standard format and currency."""
        input_values = json.dumps(values)
        
        result = await self.invoke_agent_function(
            plugin_name="CurrencyNormalizationAgent",
            function_name="NormalizeCurrencies",
            input_values=input_values,
            target_currency=target_currency
        )
        
        try:
            return json.loads(str(result))
        except json.JSONDecodeError:
            return {
                "normalized_values": [],
                "total_value_in_target_currency": 0
            }
    
    async def update_client_data(self, client_id: str, data_type: str, data: Dict[str, Any]) -> None:
        """Update the client data store with new information."""
        if client_id == "UNKNOWN":
            logger.warning("Cannot update data for unknown client")
            return
        
        # Initialize client record if it doesn't exist
        if client_id not in self.client_data_store:
            self.client_data_store[client_id] = {
                "assets": [],
                "liabilities": [],
                "documents_processed": []
            }
        
        # Update based on data type
        if data_type == "asset":
            # Check for key "assets" or fallback to "details"
            asset_items = data.get("assets")
            if not asset_items and "details" in data:
                asset_items = data["details"]
            if asset_items and isinstance(asset_items, list):
                self.client_data_store[client_id]["assets"].extend(asset_items)
        elif data_type == "liability":
            liability_items = data.get("liabilities")
            if not liability_items and "details" in data:
                liability_items = data["details"]
            if liability_items and isinstance(liability_items, list):
                # Ensure all liability values are stored as positive
                for item in liability_items:
                    if "value" in item:
                        item["value"] = abs(item["value"])
                self.client_data_store[client_id]["liabilities"].extend(liability_items)
        
        # Add document to processed list
        timestamp = datetime.now().isoformat()
        summary = f"{len(data.get('assets', [])) or len(data.get('details', []))} items" if data_type == "asset" else f"{len(data.get('liabilities', [])) or len(data.get('details', []))} items"
        self.client_data_store[client_id]["documents_processed"].append({
            "data_type": data_type,
            "timestamp": timestamp,
            "data_summary": summary
        })
        
        logger.info(f"Updated data store for client: {client_id}")
    
    async def calculate_net_worth(self, client_id: str) -> Dict[str, Any]:
        """Calculate the net worth for a client based on all known assets and liabilities."""
        if client_id not in self.client_data_store:
            return {
                "client_id": client_id,
                "error": "Client not found",
                "total_assets": 0,
                "total_liabilities": 0,
                "net_worth": 0
            }
        
        client_data = self.client_data_store[client_id]
        
        # Get client info for the calculation
        client_info = {"client_id": client_id}
        if client_data.get("client_info"):
            client_info = client_data.get("client_info")
        
        # Convert to JSON for the agent
        assets_json = json.dumps(client_data["assets"])
        liabilities_json = json.dumps(client_data["liabilities"])
        client_info_json = json.dumps(client_info)
        
        # Calculate net worth
        result = await self.invoke_agent_function(
            plugin_name="NetWorthCalculatorAgent",
            function_name="CalculateNetWorth",
            assets=assets_json,
            liabilities=liabilities_json,
            client_info=client_info_json
        )
        
        try:
            return json.loads(str(result))
        except json.JSONDecodeError:
            return {
                "client_id": client_id,
                "error": "Could not calculate net worth",
                "total_assets": sum(asset.get("value", 0) for asset in client_data["assets"]),
                "total_liabilities": sum(liability.get("value", 0) for liability in client_data["liabilities"]),
                "net_worth": sum(asset.get("value", 0) for asset in client_data["assets"]) - 
                           sum(liability.get("value", 0) for liability in client_data["liabilities"])
            }
    
    def reconcile_client_records(self) -> int:
        """
        Merge client records that appear to be the same person.
        
        Returns:
            Number of records merged
        """
        # Find clients with similar names
        client_groups = {}
        
        for client_id in self.client_data_store.keys():
            client_info = self.client_data_store[client_id].get("client_info", {})
            client_name = client_info.get("client_name", "").lower().strip()
            
            if client_name and client_name != "unknown":
                if client_name not in client_groups:
                    client_groups[client_name] = []
                client_groups[client_name].append(client_id)
        
        # Merge clients with the same name
        merged_count = 0
        for name, client_ids in client_groups.items():
            if len(client_ids) > 1:
                logger.info(f"Found multiple records for {name}: {client_ids}")
                primary_id = client_ids[0]
                
                # Merge all other records into the primary
                for other_id in client_ids[1:]:
                    self._merge_client_records(primary_id, other_id)
                    merged_count += 1
        
        logger.info(f"Reconciliation complete. Merged {merged_count} client records.")
        return merged_count
    
    def _merge_client_records(self, primary_id: str, secondary_id: str) -> None:
        """Merge two client records, preserving all data from both."""
        if primary_id not in self.client_data_store or secondary_id not in self.client_data_store:
            logger.warning(f"Cannot merge client records: one or both IDs not found")
            return
        
        # Get both records
        primary_record = self.client_data_store[primary_id]
        secondary_record = self.client_data_store[secondary_id]
        
        # Merge assets
        primary_record["assets"].extend(secondary_record.get("assets", []))
        
        # Merge liabilities
        primary_record["liabilities"].extend(secondary_record.get("liabilities", []))
        
        # Merge documents processed
        primary_record["documents_processed"].extend(secondary_record.get("documents_processed", []))
        
        # Add a note about the merge
        primary_record["merge_history"] = primary_record.get("merge_history", [])
        primary_record["merge_history"].append({
            "merged_from_id": secondary_id,
            "timestamp": datetime.now().isoformat(),
            "assets_count": len(secondary_record.get("assets", [])),
            "liabilities_count": len(secondary_record.get("liabilities", []))
        })
        
        # Remove the secondary record
        del self.client_data_store[secondary_id]
        
        logger.info(f"Merged client {secondary_id} into {primary_id}")
    
    def get_client_summary(self, client_id: str) -> Dict[str, Any]:
        """Get a summary of client data."""
        if client_id not in self.client_data_store:
            return {"client_id": client_id, "error": "Client not found"}
        
        client_data = self.client_data_store[client_id]
        
        # Calculate basic statistics
        asset_count = len(client_data.get("assets", []))
        liability_count = len(client_data.get("liabilities", []))
        document_count = len(client_data.get("documents_processed", []))
        
        # Calculate totals
        total_assets = sum(asset.get("value", 0) for asset in client_data.get("assets", []))
        total_liabilities = sum(liability.get("value", 0) for liability in client_data.get("liabilities", []))
        net_worth = total_assets - total_liabilities
        
        return {
            "client_id": client_id,
            "client_info": client_data.get("client_info", {"client_name": "UNKNOWN"}),
            "asset_count": asset_count,
            "liability_count": liability_count,
            "document_count": document_count,
            "total_assets": total_assets,
            "total_liabilities": total_liabilities,
            "net_worth": net_worth,
            "last_updated": max([doc.get("timestamp", "2000-01-01") for doc in client_data.get("documents_processed", [])], default="Never")
        }
    
    def export_client_data(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Export all client data to a file."""
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "client_count": len(self.client_data_store),
            "clients": self.client_data_store
        }
        
        if output_path:
            # Ensure directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # Write data to file
            with open(output_path, "w") as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Exported client data to {output_path}")
        
        return export_data
    
    def import_client_data(self, data: Dict[str, Any] or str) -> int:
        """Import client data from a file or dictionary."""
        if isinstance(data, str):
            # Assume it's a file path
            with open(data, "r") as f:
                data = json.load(f)
        
        client_data = data.get("clients", {})
        count = len(client_data)
        
        # Update our data store
        self.client_data_store.update(client_data)
        
        logger.info(f"Imported data for {count} clients")
        return count

    def update_client_data_from_overview(self, overview_data: dict) -> None:
        """
        Updates the client data store based on the financial overview returned
        by the FinancialOverviewAgent.
        """
        for client_name, data in overview_data.items():
            # Initialize client record if it doesn't exist.
            if client_name not in self.client_data_store:
                self.client_data_store[client_name] = {
                    "assets": [],
                    "liabilities": [],
                    "documents_processed": []
                }

            # Update assets.
            assets = data.get("assets", {})
            asset_details = assets.get("details", [])
            if isinstance(asset_details, list):
                self.client_data_store[client_name]["assets"].extend(asset_details)

            # Update liabilities.
            liabilities = data.get("liabilities", {})
            liability_details = liabilities.get("details", [])
            if isinstance(liability_details, list):
                # Ensure the liability values are positive.
                for item in liability_details:
                    if "value" in item:
                        item["value"] = abs(item["value"])
                self.client_data_store[client_name]["liabilities"].extend(liability_details)

            # Process income similarly if relevant.
            # income = data.get("income", {})
            # income_details = income.get("details", [])
            # self.client_data_store[client_name]["income"] = income_details

            # Optionally, update a "documents_processed" field.
            timestamp = datetime.now().isoformat()
            self.client_data_store[client_name]["documents_processed"].append({
                "timestamp": timestamp,
                "summary": f"Updated data from overview document"
            })

            logger.info(f"Client data updated for {client_name}")