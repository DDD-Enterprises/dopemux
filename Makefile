# Dopemux Development Makefile

.PHONY: help install install-dev test test-unit test-integration test-coverage clean lint format type-check build docs serve-docs

# Default target
help:
	@echo "Dopemux Development Commands:"
	@echo ""
	@echo "Installation:"
	@echo "  install        Install package in production mode"
	@echo "  install-dev    Install package in development mode with dev dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  test           Run all tests"
	@echo "  test-unit      Run unit tests only"
	@echo "  test-integration  Run integration tests only"
	@echo "  test-coverage  Run tests with coverage report"
	@echo "  test-fast      Run tests without slow tests"
	@echo ""
	@echo "Quality:"
	@echo "  lint           Run linting checks (flake8)"
	@echo "  format         Format code with black and isort"
	@echo "  type-check     Run type checking with mypy"
	@echo "  quality        Run all quality checks"
	@echo ""
	@echo "Development:"
	@echo "  clean          Clean build artifacts and cache"
	@echo "  build          Build distribution packages"
	@echo "  docs           Build documentation"
	@echo "  serve-docs     Serve documentation locally"

# Installation targets
install:
	pip install -e .

install-dev:
	pip install -e .[dev]

# Testing targets
test:
	pytest

test-unit:
	pytest -m "not integration"

test-integration:
	pytest -m integration

test-coverage:
	pytest --cov-report=term-missing --cov-report=html

test-fast:
	pytest -m "not slow"

test-verbose:
	pytest -v

# Quality targets
lint:
	flake8 src/ tests/

format:
	black src/ tests/
	isort src/ tests/

type-check:
	mypy src/

quality: lint type-check
	@echo "✓ All quality checks passed"

# Development targets
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf coverage.xml
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

# Development server
dev-server:
	@echo "Starting development environment..."
	@echo "Run 'make test-coverage' to see test coverage"
	@echo "Run 'make quality' to check code quality"

# Pre-commit hook simulation
pre-commit: format lint type-check test-fast
	@echo "✓ Pre-commit checks passed"

# CI simulation
ci: quality test-coverage
	@echo "✓ CI checks passed"

# Documentation (placeholder for future)
docs:
	@echo "Documentation build not yet implemented"

serve-docs:
	@echo "Documentation server not yet implemented"