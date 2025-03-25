"""Net Worth Calculator Agent for financial analysis."""

from kyc.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class NetWorthCalculatorAgent(BaseAgent):
    """Agent for calculating net worth based on assets and liabilities."""
    
    def __init__(self, kernel):
        """Initialize the Net Worth Calculator Agent."""
        super().__init__(kernel, "NetWorthCalculatorAgent")
        self.register_all_functions()
    
    def register_all_functions(self):
        """Register all functions for this agent."""
        self.register_net_worth_calculation_function()
    
    def register_net_worth_calculation_function(self):
        """Register the net worth calculation function."""
        prompt = """
        You are a Net Worth Calculator Agent specialized in financial analysis.
        
        TASK:
        Calculate the client's net worth based on the provided assets and liabilities.
        
        ASSETS:
        {{$assets}}
        
        LIABILITIES:
        {{$liabilities}}
        
        CLIENT INFO:
        {{$client_info}}
        
        INSTRUCTIONS:
        1. Sum up all asset values from the assets data.
        2. Sum up all liability values from the liabilities data.
        3. Calculate net worth as (total assets - total liabilities).
        4. Group assets and liabilities by categories.
        5. Provide a detailed breakdown of the calculation.
        6. Use the same currency for the final calculation.
        
        RESPONSE FORMAT (JSON):
        {
            "client_id": "from client info",
            "client_name": "from client info",
            "calculation_date": "current date (YYYY-MM-DD)",
            "total_assets": number,
            "total_liabilities": number,
            "net_worth": number,
            "currency": "currency code used for calculation",
            "asset_breakdown": {
                "category1": number,
                "category2": number
            },
            "liability_breakdown": {
                "category1": number,
                "category2": number
            },
            "data_completeness": "assessment of data completeness",
            "recommendations": ["any obvious financial recommendations"] or []
        }
        
        Return ONLY valid JSON without markdown formatting, comments, or explanations.
        """
        
        self.register_function(
            function_name="CalculateNetWorth",
            prompt=prompt,
            description="Calculates total net worth based on assets and liabilities"
        )