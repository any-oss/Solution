"""Agent system initialization."""
from .code_generator_agent import CodeGeneratorAgent
from .refactoring_agent import RefactoringAgent
from .code_view_agent import CodeViewAgent
from .testing_agent import TestingAgent
from .bug_detection_agent import BugDetectionAgent
from .documentation_agent import DocumentationAgent
from .migration_agent import MigrationAgent
from .devops_agent import DevOpsAgent
from .release_agent import ReleaseAgent

__all__ = [
    'CodeGeneratorAgent',
    'RefactoringAgent',
    'CodeViewAgent',
    'TestingAgent',
    'BugDetectionAgent',
    'DocumentationAgent',
    'MigrationAgent',
    'DevOpsAgent',
    'ReleaseAgent',
]
