"""Document Classification Agent for categorizing financial documents."""

from kyc.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class DocumentClassificationAgent(BaseAgent):
    """Agent for classifying financial documents into specific categories."""
    
    def __init__(self, kernel):
        """Initialize the Document Classification Agent."""
        super().__init__(kernel, "DocumentClassificationAgent")
        self.register_all_functions()
    
    def register_all_functions(self):
        """Register all functions for this agent."""
        self.register_classification_function()
        self.register_multilingual_classification_function()
    
    def register_classification_function(self):
        """Register the document classification function."""
        prompt = """
        You are a Document Classification Agent specialized in financial documents.
        
        TASK:
        Analyze this document and classify it into EXACTLY ONE of the following categories:
        
        CATEGORIES:
        - FinancialAssets (stocks, bonds, mutual funds, investment accounts)
        - BankableAssets (cash, checking accounts, savings accounts, CDs)
        - RealEstate (properties, land, real estate valuations)
        - PrivateEquity (business ownership, venture investments, private equity)
        - OtherAssets (vehicles, art, collectibles, personal property)
        - Loans (personal loans, non-mortgage debt)
        - Mortgages (property mortgages, home equity loans)
        - CreditCards (credit card statements, credit debt)
        - OtherLiabilities (other forms of debt)
        - Salary (employment income, wages, bonuses)
        - Dividends (dividend income from investments)
        - Interest (interest income)
        - RentalIncome (income from property leasing)
        - OtherIncome (other sources of income)
        
        DOCUMENT:
        {{$document}}
        
        INSTRUCTIONS:
        1. Analyze the content, format, and financial data in the document.
        2. Determine the primary financial purpose of this document.
        3. Select EXACTLY ONE category that best matches the document.
        4. For mixed documents, choose the category that represents the main purpose.
        
        RESPONSE FORMAT:
        Return ONLY the category name without quotes, explanations, or additional text.
        """
        
        self.register_function(
            function_name="ClassifyFinancialDocument",
            prompt=prompt,
            description="Classifies financial documents into specific categories"
        )
    
    def register_multilingual_classification_function(self):
        """Register the multilingual document classification function."""
        prompt = """
        You are a Document Classification Agent specialized in multilingual financial documents.
        
        TASK:
        Analyze this document in {{$language}} and classify it into one of the following categories:
        
        CATEGORIES:
        - FinancialAssets
        - BankableAssets
        - RealEstate
        - PrivateEquity
        - OtherAssets
        - Loans
        - Mortgages
        - CreditCards
        - OtherLiabilities
        - Salary
        - Dividends
        - Interest
        - RentalIncome
        - OtherIncome
        
        DOCUMENT:
        {{$document}}
        
        Return ONLY the category name without any additional text.
        """
        
        self.register_function(
            function_name="ClassifyMultilingualDocument",
            prompt=prompt,
            description="Classifies financial documents in multiple languages"
        )