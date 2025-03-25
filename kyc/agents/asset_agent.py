"""Asset Identification Agent for extracting financial assets from documents."""

from kyc.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class AssetIdentificationAgent(BaseAgent):
    """Agent for identifying and extracting asset information from financial documents."""
    
    def __init__(self, kernel):
        """Initialize the Asset Identification Agent."""
        super().__init__(kernel, "AssetIdentificationAgent")
        self.register_all_functions()
    
    def register_all_functions(self):
        """Register all functions for this agent."""
        self.register_asset_extraction_function()
    
    def register_asset_extraction_function(self):
        """Register the asset extraction function."""
        prompt = """
        You are an Asset Identification Agent specialized in extracting financial asset information.
        
        TASK:
        Extract all assets and their monetary values from the document.
        
        DOCUMENT:
        {{$document}}
        
        DOCUMENT TYPE: {{$document_type}}
        
        TABLES (if available):
        {{$tables}}
        
        INSTRUCTIONS:
        1. Identify all assets belonging to the client mentioned in the document.
        2. Extract both the asset description and its monetary value.
        3. Convert all values to numbers (remove currency symbols, commas).
        4. For recurring assets (like income), note the frequency.
        5. Extract any relevant dates (valuation date, statement date).
        6. Pay special attention to tables, lists, and totals sections.
        
        RESPONSE FORMAT (JSON):
        {
            "total_assets_value": number,
            "currency": "detected currency code (USD, EUR, etc.)",
            "valuation_date": "YYYY-MM-DD",
            "assets": [
                {
                    "description": "asset description",
                    "value": number,
                    "type": "asset category (cash, stock, property, etc.)",
                    "details": "additional information if available"
                }
            ],
            "subtotals": {
                "category1": number,
                "category2": number
            }
        }
        
        Return ONLY valid JSON without markdown formatting, comments, or explanations.
        """
        
        self.register_function(
            function_name="ExtractAssets",
            prompt=prompt,
            description="Extracts asset information and values from financial documents"
        )