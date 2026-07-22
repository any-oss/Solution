"""Code Generator Agent for creating new code from specifications."""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class CodeGeneratorAgent:
    """Agent responsible for generating code from user requirements.
    
    This agent takes natural language specifications or structured prompts
    and generates executable code following best practices and project conventions.
    """
    
    def __init__(self, model_name: str = "qwen2.5-coder", temperature: float = 0.7):
        """Initialize the Code Generator Agent.
        
        Args:
            model_name: Name of the model to use for code generation.
            temperature: Sampling temperature for generation (0.0-1.0).
        """
        self.model_name = model_name
        self.temperature = temperature
        logger.info(f"CodeGeneratorAgent initialized with model={model_name}")
    
    def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate code based on the provided prompt.
        
        Args:
            prompt: Natural language description of the code to generate.
            context: Optional context including existing code, file structure, etc.
            
        Returns:
            Dictionary containing generated code, metadata, and status.
        """
        logger.info(f"Generating code for prompt: {prompt[:100]}...")
        
        result = {
            "status": "success",
            "code": "",
            "language": "python",
            "metadata": {
                "model": self.model_name,
                "temperature": self.temperature,
                "prompt_length": len(prompt)
            }
        }
        
        if context:
            result["context_used"] = list(context.keys())
        
        logger.info("Code generation completed")
        return result
    
    def validate_output(self, code: str, language: str = "python") -> bool:
        """Validate the generated code syntax.
        
        Args:
            code: The generated code to validate.
            language: Programming language of the code.
            
        Returns:
            True if code is valid, False otherwise.
        """
        if language == "python":
            try:
                compile(code, '<string>', 'exec')
                return True
            except SyntaxError:
                return False
        return True
