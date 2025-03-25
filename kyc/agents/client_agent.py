"""Client Identification Agent for extracting client information from documents."""

from kyc.agents.base_agent import BaseAgent

class ClientIdentificationAgent(BaseAgent):
    """Agent for extracting client identity information from financial documents."""
    
    def __init__(self, kernel):
        """Initialize the Client Identification Agent."""
        super().__init__(kernel, "ClientIdentificationAgent")
        self.register_all_functions()
    
    def register_all_functions(self):
        """Register all functions for this agent."""
        self.register_client_identifier()
        self.register_multilingual_client_identifier()
    
    def register_client_identifier(self):
        """Register the client identifier function."""
        prompt = """
        You are a Client Identification Agent specialized in financial documents.
        
        TASK:
        Extract the client identifier information from the provided document.
        
        DOCUMENT:
        {{$document}}
        
        INSTRUCTIONS:
        1. Look for the client name, account numbers, client IDs, or tax IDs.
        2. Determine the primary owner or account holder of the document.
        3. Extract identifiers in their original format without modifications.
        4. For multiple clients, focus on the primary account holder.
        5. Handle diverse document formats: statements, assessments, invoices, etc.
        
        RESPONSE FORMAT (JSON):
        {
            "client_id": "most unique identifier found (preferably account/customer number)",
            "client_name": "full name of client",
            "account_number": "account number if found, otherwise null",
            "tax_id": "tax ID/SSN if found, otherwise null", 
            "confidence": "high/medium/low",
            "source": "specific section or line where this information was found"
        }
        
        Return ONLY valid JSON without markdown formatting, comments, or explanations.
        """
        
        self.register_function(
            function_name="ExtractClientIdentifier",
            prompt=prompt,
            description="Extracts client identity information from financial documents"
        )
    
    def register_multilingual_client_identifier(self):
        """Register the multilingual client identifier function."""
        prompt = """
        You are a Multilingual Client Identification Agent specialized in financial documents.
        
        TASK:
        Extract client identifier information from this document in {{$language}}.
        
        DOCUMENT:
        {{$document}}
        
        INSTRUCTIONS:
        1. Identify key terms in {{$language}} that indicate client names, account numbers or IDs.
        2. Focus on extracting the primary client/account holder.
        3. Return the information in its original language and script.
        
        RESPONSE FORMAT (JSON):
        {
            "client_id": "most unique identifier found",
            "client_name": "full name as it appears in document",
            "account_number": "account number if available, otherwise null",
            "language_detected": "actual language detected",
            "confidence": "high/medium/low"
        }
        
        Return ONLY valid JSON without markdown formatting or explanations.
        """
        
        self.register_function(
            function_name="ExtractMultilingualClientIdentifier",
            prompt=prompt,
            description="Extracts client identity information from financial documents in multiple languages"
        )