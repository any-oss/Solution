# Contributing to Intelligent Request Router

Thank you for considering contributing to the Intelligent Request Router! We welcome contributions from the community and are grateful for any help you can provide.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to keep our community open, inclusive, and respectful.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps to reproduce the problem**
* **Provide specific examples to demonstrate the steps**
* **Describe the behavior you observed and what behavior you expected**
* **Include any relevant logs or error messages**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a detailed description of the suggested enhancement**
* **Explain why this enhancement would be useful**
* **List some examples of how this enhancement would be used**

### Pull Requests

The process described here has several goals:

- Maintain code quality
- Fix problems that are important to users
- Engage the community in working toward the best possible solution
- Enable a sustainable system for maintainers to review contributions

Please follow these steps to have your contribution considered by the maintainers:

1. Fork the repository and create your branch from `main`
2. Add tests for your changes
3. Ensure all tests pass
4. Follow the style guidelines (see below)
5. Submit your pull request with a clear description

### Style Guidelines

* Use 4 spaces for indentation
* Keep lines under 100 characters
* Write docstrings for public functions and classes
* Use meaningful variable names
* Follow PEP 8 conventions for Python code

### Running Tests

Before submitting a pull request, make sure all tests pass:

```bash
# Install test dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v

# Run with coverage
pytest --cov=core --cov-report=html
```

### Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

## Questions?

Feel free to open an issue with the label "question" if you have any questions about contributing.

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.
