"""Agent for extracting multiple financial data categories from mixed documents."""

from kyc.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class FinancialOverviewAgent(BaseAgent):
    """Agent to extract an overall financial overview from a document."""
    
    def __init__(self, kernel):
        super().__init__(kernel, "FinancialOverviewAgent")
        self.register_all_functions()
    
    def register_all_functions(self):
        self.register_extract_overview_function()
    
    def register_extract_overview_function(self):
        prompt = """
        You are a Financial Overview Agent. Your task is to extract a comprehensive financial overview
        from the document provided. A document may include assets, liabilities, and income information.
        
    TASK:
    - Identify and extract financial data (assets, liabilities, income) and assign the details to each client name found.
    - Return a JSON object where each key is a client name (for example, "Hans Muster" or "Maria Muster").
      Each client key should map to an object with keys "assets", "liabilities", and "income".
    - Under "assets" and "liabilities", include a "total_value" field and a "details" list.
    
    For example, your output should have the form:
    {
      "Hans Muster": {
         "assets": {
            "total_value": 123456,
            "details": [ { "description": "CSX Savings Account", "value": 12345 }, ... ]
         },
         "liabilities": {
            "total_value": 54321,
            "details": [ { "description": "Mortgage", "value": 54321 }, ... ]
         },
         "income": { "total_income": 0, "details": [] }
      },
      "Maria Muster": {
         "assets": { ... },
         "liabilities": { ... },
         "income": { ... }
      }
    }

     A more generic example could be:   
        Use the original document (provided as {{$document}}) and return a JSON with the following structure:
        {
           "assets": {
               "total_assets_value": number,
               "currency": "ISO currency code",
               "details": [ { "description": string, "value": number } ]
           },
           "liabilities": {
               "total_liabilities_value": number,
               "currency": "ISO currency code",
               "details": [ { "description": string, "value": number } ]
           },
           "income": {
               "total_income": number,
               "currency": "ISO currency code",
               "details": [ { "description": string, "value": number } ]
           }
        }
        
        Return ONLY valid JSON without any markdown formatting, comments, or additional text.
        """
        self.register_function(
            function_name="ExtractOverview",
            prompt=prompt,
            description="Extracts an overall financial overview (assets, liabilities, income) from a mixed document"
        )