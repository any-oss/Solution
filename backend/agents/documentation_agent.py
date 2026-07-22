"""Documentation Agent for generating and maintaining project documentation."""
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class DocumentationAgent:
    """Agent responsible for creating and maintaining documentation.
    
    This agent generates API documentation, README files, code comments,
    and other technical documentation from source code.
    """
    
    def __init__(self, model_name: str = "qwen2.5", style: str = "google"):
        """Initialize the Documentation Agent.
        
        Args:
            model_name: Name of the model to use for documentation generation.
            style: Documentation style (google, numpy, sphinx, markdown).
        """
        self.model_name = model_name
        self.style = style
        logger.info(f"DocumentationAgent initialized with model={model_name}, style={style}")
    
    def generate_docstring(self, code: str, element_type: str = "function") -> str:
        """Generate a docstring for a code element.
        
        Args:
            code: The code element (function, class, method).
            element_type: Type of element (function, class, method, module).
            
        Returns:
            Generated docstring in the configured style.
        """
        logger.info(f"Generating {self.style} docstring for {element_type}...")
        
        if self.style == "google":
            docstring = '''"""Brief description of the function.

Args:
    arg1: Description of argument 1.
    arg2: Description of argument 2.

Returns:
    Description of return value.

Raises:
    ValueError: When invalid input is provided.
"""'''
        elif self.style == "sphinx":
            docstring = '''"""Brief description of the function.

:param arg1: Description of argument 1.
:param arg2: Description of argument 2.
:return: Description of return value.
:raises ValueError: When invalid input is provided.
"""'''
        else:
            docstring = '''"""Brief description of the function."""'''
        
        logger.info("Docstring generated")
        return docstring
    
    def create_readme(self, project_info: Dict[str, Any]) -> str:
        """Generate a README.md file for the project.
        
        Args:
            project_info: Dictionary containing project metadata and details.
            
        Returns:
            Complete README content in Markdown format.
        """
        logger.info("Generating README.md...")
        
        readme = f"""# {project_info.get('name', 'Project')}

{project_info.get('description', 'A new project.')}

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
# Example usage here
```

## Features

{self._format_features(project_info.get('features', []))}

## Contributing

See CONTRIBUTING.md for guidelines.

## License

{project_info.get('license', 'MIT')}
"""
        
        logger.info("README generated")
        return readme
    
    def _format_features(self, features: List[str]) -> str:
        """Format features list for README."""
        if not features:
            return "- Feature-driven development"
        return "\n".join([f"- {f}" for f in features])
    
    def generate_api_docs(self, modules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate API documentation for multiple modules.
        
        Args:
            modules: List of module information dictionaries.
            
        Returns:
            Dictionary containing API documentation structure.
        """
        logger.info(f"Generating API docs for {len(modules)} modules...")
        
        api_docs = {
            "title": "API Documentation",
            "version": "1.0.0",
            "modules": []
        }
        
        for module in modules:
            api_docs["modules"].append({
                "name": module.get("name", "unknown"),
                "description": module.get("description", ""),
                "classes": module.get("classes", []),
                "functions": module.get("functions", [])
            })
        
        result = {
            "status": "success",
            "documentation": api_docs,
            "format": self.style,
            "modules_documented": len(modules)
        }
        
        logger.info("API documentation generated")
        return result
    
    def update_changelog(self, changes: List[Dict[str, Any]], version: str) -> str:
        """Generate changelog entries for a release.
        
        Args:
            changes: List of change descriptions with types (added, changed, fixed).
            version: Version number for this release.
            
        Returns:
            Formatted changelog section in Keep a Changelog format.
        """
        logger.info(f"Updating changelog for version {version}...")
        
        changelog = f"## [{version}] - {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        categories = {"added": "### Added", "changed": "### Changed", "fixed": "### Fixed", "removed": "### Removed"}
        
        for category, header in categories.items():
            items = [c for c in changes if c.get("type") == category]
            if items:
                changelog += f"{header}\n\n"
                for item in items:
                    changelog += f"- {item.get('description', '')}\n"
                changelog += "\n"
        
        logger.info("Changelog updated")
        return changelog
    
    def extract_comments(self, code: str) -> List[Dict[str, Any]]:
        """Extract all comments from source code.
        
        Args:
            code: Source code to analyze.
            
        Returns:
            List of comments with line numbers and content.
        """
        comments = []
        lines = code.splitlines()
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("#"):
                comments.append({
                    "line": i + 1,
                    "content": stripped[1:].strip(),
                    "type": "single_line"
                })
            elif '"""' in line or "'''" in line:
                comments.append({
                    "line": i + 1,
                    "content": "",
                    "type": "docstring"
                })
        
        return comments
