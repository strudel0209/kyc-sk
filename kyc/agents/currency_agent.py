"""Currency Normalization Agent for standardizing financial values."""

from kyc.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class CurrencyNormalizationAgent(BaseAgent):
    """Agent for normalizing currency values across different formats and currencies."""
    
    def __init__(self, kernel):
        """Initialize the Currency Normalization Agent."""
        super().__init__(kernel, "CurrencyNormalizationAgent")
        self.register_all_functions()
    
    def register_all_functions(self):
        """Register all functions for this agent."""
        self.register_currency_normalization_function()
    
    def register_currency_normalization_function(self):
        """Register the currency normalization function."""
        prompt = """
        You are a Currency Normalization Agent specialized in financial data.
        
        TASK:
        Normalize the provided financial values to a standard format and currency.
        
        INPUT:
        {{$input_values}}
        
        TARGET CURRENCY: {{$target_currency}}
        
        INSTRUCTIONS:
        1. Identify the source currency for each value.
        2. Convert numerical values to proper decimal format.
        3. Convert all values to the target currency using sensible exchange rates.
        4. Handle different number formats (e.g., European vs US notation).
        5. Remove any non-numeric characters except decimal separators.
        
        RESPONSE FORMAT (JSON):
        {
            "normalized_values": [
                {
                    "original_value": "original string representation",
                    "original_currency": "identified source currency",
                    "normalized_value": number (decimal),
                    "target_currency": "{{$target_currency}}",
                    "exchange_rate_applied": number or null,
                    "confidence": "high/medium/low"
                }
            ],
            "total_value_in_target_currency": number (decimal)
        }
        
        Return ONLY valid JSON without markdown formatting, comments, or explanations.
        """
        
        self.register_function(
            function_name="NormalizeCurrencies",
            prompt=prompt,
            description="Normalizes financial values to a standard currency and format"
        )