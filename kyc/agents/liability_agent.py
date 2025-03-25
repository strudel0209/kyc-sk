"""Liability Identification Agent for extracting financial liabilities from documents."""

from kyc.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class LiabilityIdentificationAgent(BaseAgent):
    """Agent for identifying and extracting liability information from financial documents."""
    
    def __init__(self, kernel):
        """Initialize the Liability Identification Agent."""
        super().__init__(kernel, "LiabilityIdentificationAgent")
        self.register_all_functions()
    
    def register_all_functions(self):
        """Register all functions for this agent."""
        self.register_liability_extraction_function()
    
    def register_liability_extraction_function(self):
        """Register the liability extraction function."""
        prompt = """
        You are a Liability Identification Agent specialized in extracting financial liabilities.
        
        TASK:
        Extract all liabilities and their monetary values from the document.
        
        DOCUMENT:
        {{$document}}
        
        DOCUMENT TYPE: {{$document_type}}
        
        TABLES (if available):
        {{$tables}}
        
        INSTRUCTIONS:
        1. Identify all debts, loans, mortgages, and other liabilities in the document.
        2. Extract both the liability description and its monetary value.
        3. Convert all values to numbers (remove currency symbols, commas).
        4. Note interest rates and payment terms if available.
        5. Extract any relevant dates (statement date, due dates).
        6. Pay special attention to tables, summaries, and balance sections.
        7. Pay attention to the sign in front of the amount that you identify as liability. Typically this can be repreented as a "-". Convert it to a positive amount as the value will be needed for the total net worth calculation of the client which uses the formula -> assets - liabilities
        
        RESPONSE FORMAT (JSON):
        {
            "total_liabilities_value": number,
            "currency": "detected currency code (USD, EUR, etc.)",
            "statement_date": "YYYY-MM-DD",
            "liabilities": [
                {
                    "description": "liability description",
                    "value": number,
                    "type": "liability type (mortgage, loan, credit card, etc.)",
                    "interest_rate": number or null,
                    "term": "payment term if available",
                    "details": "additional information"
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
            function_name="ExtractLiabilities",
            prompt=prompt,
            description="Extracts liability information and values from financial documents"
        )