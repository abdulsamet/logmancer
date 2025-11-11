Contributing to Logmancer
==========================

We welcome contributions! This document provides guidelines for contributing to Logmancer.

Getting Started
---------------

1. **Fork the repository** on GitHub
2. **Clone your fork** locally::

    git clone https://github.com/YOUR-USERNAME/logmancer.git
    cd logmancer

3. **Install development dependencies**::

    uv sync --all-groups

4. **Create a branch** for your changes::

    git checkout -b feature/your-feature-name

Development Setup
-----------------

**Run tests**::

    uv run pytest

**Check code quality**::

    uv run black logmancer/ tests/
    uv run isort logmancer/ tests/
    uv run ruff check logmancer/ tests/

**Run tests with coverage**::

    uv run pytest --cov=logmancer --cov-report=html

**Build documentation**::

    cd docs
    uv run make html

Code Style
----------

* Follow PEP 8 style guide
* Use Black for code formatting
* Use isort for import sorting
* Maximum line length: 100 characters
* Add type hints where appropriate

Testing
-------

* Write tests for all new features
* Maintain test coverage above 95%
* Use pytest fixtures for common setup
* Mock external dependencies
* Test both sync and async code paths

Documentation
-------------

* Add docstrings to all public functions/classes
* Update API documentation if needed
* Add examples for new features
* Update changelog with your changes

Pull Request Process
--------------------

1. **Update tests** - Ensure all tests pass
2. **Update documentation** - Document your changes
3. **Update changelog** - Add entry to CHANGELOG.md
4. **Run quality checks** - Black, isort, ruff
5. **Create pull request** - Describe your changes clearly
6. **Address review comments** - Work with maintainers

Commit Messages
---------------

Use clear, descriptive commit messages::

    Add notification system for error alerts
    
    - Implement Email backend
    - Implement Slack backend
    - Implement Telegram backend
    - Add tests for all backends

Questions?
----------

* Open an issue on GitHub
* Contact the maintainers

License
-------

By contributing, you agree that your contributions will be licensed under the MIT License.
