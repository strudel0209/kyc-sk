"""Multilingual Agent for language detection and translation."""

from kyc.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class MultilingualAgent(BaseAgent):
    """Agent for handling multilingual documents including detection and translation."""
    
    def __init__(self, kernel):
        """Initialize the Multilingual Agent."""
        super().__init__(kernel, "MultilingualAgent")
        self.register_all_functions()
    
    def register_all_functions(self):
        """Register all functions for this agent."""
        self.register_language_detection_function()
        self.register_translation_function()
    
    def register_language_detection_function(self):
        """Register the language detection function."""
        prompt = """
        You are a Language Detection Agent specialized in financial documents.
        
        TASK:
        Detect the primary language used in the document.
        
        DOCUMENT (First 1000 characters):
        {{$document_sample}}
        
        INSTRUCTIONS:
        1. Analyze the text patterns, characters, and linguistic features.
        2. Identify the primary language used in the document.
        3. Determine the confidence level of your detection.
        4. Note if multiple languages are present.
        
        RESPONSE FORMAT (JSON):
        {
            "primary_language": "language name in English",
            "language_code": "ISO 639-1 language code (en, es, fr, de, zh, etc.)",
            "confidence": "high/medium/low",
            "other_languages": ["other detected languages"] or [],
            "writing_system": "latin/cyrillic/arabic/cjk/other"
        }
        
        Return ONLY valid JSON without markdown formatting, comments, or explanations.
        """
        
        self.register_function(
            function_name="DetectLanguage",
            prompt=prompt,
            description="Detects the language used in a financial document"
        )
    
    def register_translation_function(self):
        """Register the translation function."""
        prompt = """
        You are a Financial Document Translation Agent.
        
        TASK:
        Translate the key financial information from the document to English.
        
        DOCUMENT:
        {{$document}}
        
        SOURCE LANGUAGE: {{$source_language}}
        
        INSTRUCTIONS:
        1. Focus only on translating the financial figures, client information, and key dates.
        2. Maintain the original numerical values and formats.
        3. Preserve the structure of the document when possible.
        4. Translate headers, labels, and important sections.
        5. Do not translate proper names, account numbers, or identifiers.
        
        RESPONSE FORMAT:
        Return the translated financial information in a clear, structured format.
        Include a glossary of key financial terms that were translated.
        """
        
        self.register_function(
            function_name="TranslateFinancialDocument",
            prompt=prompt,
            description="Translates key financial information to English"
        )