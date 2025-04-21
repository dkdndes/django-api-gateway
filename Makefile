.PHONY: setup install dev migrate test run clean format lint

# Default Python interpreter
PYTHON = python
# Default port
PORT = 8000
# Default host
HOST = 0.0.0.0

setup:
	uv venv
	@echo "Virtual environment created. Activate with: source .venv/bin/activate"

install:
	uv pip install -e .

dev:
	uv pip install -e ".[dev]"

migrate:
	$(PYTHON) manage.py migrate

test:
	$(PYTHON) manage.py test

run:
	$(PYTHON) manage.py runserver $(HOST):$(PORT)

clean:
	rm -rf __pycache__
	rm -rf */__pycache__
	rm -rf */*/__pycache__
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info

format:
	black .
	isort .

lint:
	flake8 .
	black --check .
	isort --check .

testdata:
	$(PYTHON) manage.py create_test_data

superuser:
	$(PYTHON) manage.py createsuperuser

requirements:
	uv pip compile pyproject.toml -o requirements.txt
	uv pip compile pyproject.toml --extra=dev -o requirements-dev.txt

help:
	@echo "Available commands:"
	@echo "  setup        - Create a virtual environment using uv"
	@echo "  install      - Install the package and its dependencies"
	@echo "  dev          - Install development dependencies"
	@echo "  migrate      - Run database migrations"
	@echo "  test         - Run tests"
	@echo "  run          - Run the development server"
	@echo "  clean        - Remove build artifacts"
	@echo "  format       - Format code with black and isort"
	@echo "  lint         - Check code style with flake8, black, and isort"
	@echo "  testdata     - Create test data"
	@echo "  superuser    - Create a superuser"
	@echo "  requirements - Generate requirements.txt and requirements-dev.txt"
	@echo "  help         - Show this help message"