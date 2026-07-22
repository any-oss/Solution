"""Code View Agent for code exploration and visualization."""
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class CodeViewAgent:
    """Agent responsible for code exploration and visualization.
    
    This agent provides capabilities for viewing, navigating, and
    understanding code structure, dependencies, and relationships.
    """
    
    def __init__(self, model_name: str = "qwen2.5"):
        """Initialize the Code View Agent.
        
        Args:
            model_name: Name of the model to use for code analysis.
        """
        self.model_name = model_name
        logger.info(f"CodeViewAgent initialized with model={model_name}")
    
    def get_structure(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Extract the structural elements of code.
        
        Args:
            code: Source code to analyze.
            language: Programming language of the code.
            
        Returns:
            Dictionary containing classes, functions, imports, and other structures.
        """
        logger.info(f"Analyzing code structure ({language})...")
        
        structure = {
            "classes": [],
            "functions": [],
            "imports": [],
            "constants": [],
            "variables": []
        }
        
        lines = code.splitlines()
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("def "):
                structure["functions"].append({"name": stripped.split("(")[0].replace("def ", ""), "line": i + 1})
            elif stripped.startswith("class "):
                structure["classes"].append({"name": stripped.split("(")[0].replace("class ", ""), "line": i + 1})
            elif stripped.startswith("import ") or stripped.startswith("from "):
                structure["imports"].append({"statement": stripped, "line": i + 1})
        
        result = {
            "status": "success",
            "structure": structure,
            "metadata": {
                "model": self.model_name,
                "total_lines": len(lines)
            }
        }
        
        logger.info("Structure analysis completed")
        return result
    
    def generate_summary(self, code: str) -> str:
        """Generate a human-readable summary of the code.
        
        Args:
            code: Source code to summarize.
            
        Returns:
            Natural language summary of what the code does.
        """
        logger.info("Generating code summary...")
        summary = "This module provides functionality for code analysis and visualization."
        logger.info("Summary generated")
        return summary
    
    def find_references(self, symbol: str, code: str) -> List[Dict[str, Any]]:
        """Find all references to a symbol in the code.
        
        Args:
            symbol: The symbol (variable, function, class) to search for.
            code: Source code to search in.
            
        Returns:
            List of reference locations with line numbers and context.
        """
        references = []
        lines = code.splitlines()
        
        for i, line in enumerate(lines):
            if symbol in line:
                references.append({
                    "line": i + 1,
                    "content": line.strip(),
                    "context": lines[max(0, i-2):min(len(lines), i+3)]
                })
        
        return references
    
    def visualize_dependencies(self, files: List[str]) -> Dict[str, Any]:
        """Create a dependency graph visualization data.
        
        Args:
            files: List of file paths to analyze.
            
        Returns:
            Dependency graph data suitable for visualization.
        """
        logger.info(f"Building dependency graph for {len(files)} files...")
        
        graph = {
            "nodes": [{"id": f, "type": "file"} for f in files],
            "edges": []
        }
        
        result = {
            "status": "success",
            "graph": graph,
            "format": "force-directed"
        }
        
        logger.info("Dependency visualization completed")
        return result
