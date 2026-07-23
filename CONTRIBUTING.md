# Contributing to Intelligent Request Router

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Accept constructive criticism
- Focus on what's best for the community

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs actual behavior
- Environment details (OS, Python version, Docker version)
- Any relevant logs or screenshots

**Example:**
```markdown
**Bug Summary**
Proxy server crashes when receiving malformed JSON

**Steps to Reproduce**
1. Start the proxy server
2. Send POST request with invalid JSON to /v1/chat/completions
3. Observe server crash

**Expected Behavior**
Server should return 400 error and continue running

**Actual Behavior**
Server crashes with JSONDecodeError

**Environment**
- OS: Ubuntu 22.04
- Python: 3.11
- Docker: 24.0.5
```

### Suggesting Features

Feature suggestions are welcome! Please provide:

- A clear description of the feature
- Use cases and benefits
- Possible implementation approaches
- Any potential drawbacks

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest` and `bash scripts/verify.sh`)
5. Commit with clear messages following [Conventional Commits](https://www.conventionalcommits.org/)
6. Push to your branch
7. Open a Pull Request

**PR Guidelines:**
- Keep PRs focused and reasonably sized
- Include tests for new functionality
- Update documentation as needed
- Ensure all tests pass
- Follow existing code style

## Development Setup

### Prerequisites

- Python 3.9+
- Docker & Docker Compose v2.0+
- Git

### Local Development

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/summy.git
cd summy

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run services locally
uvicorn core.proxy:app --port 8000
```

### Docker Development

```bash
# Build and run with Docker Compose
docker compose up -d

# View logs
docker compose logs -f

# Run tests in container
docker compose exec proxy pytest
```

## Code Style

- Follow [PEP 8](https://pep8.org/) for Python code
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions small and focused
- Use meaningful variable and function names

### Example

```python
def select_backend(prompt: str, threshold: int = 100) -> str:
    """Select backend based on prompt length.
    
    Args:
        prompt: Input prompt text.
        threshold: Length threshold for backend selection.
        
    Returns:
        Backend URL (CPU for short prompts, GPU for long prompts).
    """
    return GPU_BACKEND_URL if len(prompt) > threshold else CPU_BACKEND_URL
```

## Testing

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=core --cov=ui --cov=sdk --cov=cli

# Specific test file
pytest tests/test_proxy.py

# Specific test function
pytest tests/test_proxy.py::test_health_endpoint
```

### Writing Tests

- Test both success and failure cases
- Mock external dependencies
- Use descriptive test names
- Keep tests independent and idempotent

**Example:**

```python
def test_post_invalid_json():
    """Test that invalid JSON returns 400 error."""
    response = requests.post(
        f"{PROXY_URL}/v1/chat/completions",
        data="not valid json",
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 400
    assert "error" in response.json()
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings to all public APIs
- Include usage examples
- Document configuration options
- Update CHANGELOG.md

## Release Process

1. Update VERSION file with new version number
2. Update CHANGELOG.md with release notes
3. Create a release tag: `git tag -a v1.2.0 -m "Release v1.2.0"`
4. Push tag: `git push origin v1.2.0`
5. GitHub Actions will automatically build and publish

## Questions?

Feel free to open an issue for any questions or discussions.

---

Thank you for contributing to making Intelligent Request Router better!
