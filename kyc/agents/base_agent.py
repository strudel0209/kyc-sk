"""Base agent definition and common functionality for KYC agents."""

import logging
from typing import Dict, Any
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings

from kyc.config import DEFAULT_SERVICE_ID, DEFAULT_TEMPERATURE

logger = logging.getLogger(__name__)

class BaseAgent:
    """Base class for all KYC agents."""
    
    def __init__(self, kernel: Kernel, plugin_name: str):
        """Initialize the base agent.
        
        Args:
            kernel: The Semantic Kernel instance
            plugin_name: The name of this agent's plugin
        """
        self.kernel = kernel
        self.plugin_name = plugin_name
    
    def get_prompt_settings(self, temperature: float = DEFAULT_TEMPERATURE):
        """Get standard prompt execution settings."""
        return AzureChatPromptExecutionSettings(
            service_id=DEFAULT_SERVICE_ID,
            temperature=temperature
        )
    
    def register_function(self, function_name: str, prompt: str, description: str):
        """Register a function with the kernel.
        
        Args:
            function_name: Name of the function
            prompt: The prompt template
            description: Description of what the function does
        """
        try:
            settings = self.get_prompt_settings()
            
            self.kernel.add_function(
                function_name=function_name,
                plugin_name=self.plugin_name,
                description=description,
                prompt=prompt,
                prompt_execution_settings=settings
            )
            
            logger.info(f"Registered function {self.plugin_name}.{function_name}")
        except Exception as e:
            logger.error(f"Error registering function {function_name}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())