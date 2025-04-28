# API Gateway with Django

This project implements an API Gateway using Django and Django REST Framework. It allows you to define mapping rules between domains, API endpoints, and API payloads.

[![Version](https://img.shields.io/badge/version-0.1.2-blue.svg)](https://github.com/dkdndes/django-api-gateway)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/dkdndes/django-api-gateway/actions/workflows/django-tests.yml/badge.svg)](https://github.com/dkdndes/django-api-gateway/actions/workflows/django-tests.yml)
[![Coverage](https://img.shields.io/codecov/c/github/dkdndes/django-api-gateway/develop.svg)](https://codecov.io/gh/dkdndes/django-api-gateway)

## Features

- Map domains to target APIs
- Define API endpoints with transformations
- Transform request and response payloads
- Log API requests and responses
- Admin interface for managing mappings
- REST API for programmatic management
- IFTTT-like web interface for easy rule management

## Models

- **Domain**: Represents a domain that the gateway will handle
- **ApiEndpoint**: Represents an API endpoint with its HTTP method and target URL
- **RequestTransformation**: Defines transformations for request payloads
- **ResponseTransformation**: Defines transformations for response payloads
- **ApiLog**: Logs API requests and responses

## Installation

### Using pip

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Apply migrations:
   ```
   python manage.py migrate
   ```
4. Create a superuser:
   ```
   python manage.py createsuperuser
   ```
5. (Optional) Create test data:
   ```
   python manage.py create_test_data
   ```
6. Run the server:
   ```
   python manage.py runserver
   ```

### Using uv (recommended)

1. Clone the repository
2. Create a virtual environment:
   ```
   uv venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```
   uv pip install -e .
   ```
4. Apply migrations:
   ```
   python manage.py migrate
   ```
5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```
6. (Optional) Create test data:
   ```
   python manage.py create_test_data
   ```
7. Run the server:
   ```
   python manage.py runserver
   ```

## Development

For development, install the development dependencies:

```
uv pip install -e ".[dev]"
```

Or using the requirements file:

```
uv pip install -r requirements-dev.txt
```

### Running Tests

To run the tests, use pytest:

```
python -m pytest
```

To run tests with coverage:

```
python -m pytest --cov=gateway
```

To generate a coverage report:

```
python -m pytest --cov=gateway --cov-report=html
```

This will create a `htmlcov` directory with an HTML coverage report that you can view in your browser.

## Usage

### Web Interface

Access the web interface at the root URL `/` to use the IFTTT-like rule management interface:

- **Dashboard**: View gateway statistics and recent activity
- **Rules**: Manage API routing rules with an intuitive IF-THEN interface
- **Logs**: View and filter API request logs

### Admin Interface

Access the admin interface at `/admin/` to manage domains, endpoints, and transformations.

### API Endpoints

The following API endpoints are available:

- `/api/v1/domains/`: List and manage domains
- `/api/v1/endpoints/`: List and manage API endpoints
- `/api/v1/request-transformations/`: List and manage request transformations
- `/api/v1/response-transformations/`: List and manage response transformations
- `/api/v1/logs/`: View API logs

### API Documentation

API documentation is available at `/docs/`.

### Making API Requests

To make a request through the gateway, use one of the following formats:

1. Using the domain name:
   ```
   http://domain.example.com/path
   ```

2. Using the API prefix:
   ```
   http://localhost:8000/api/path
   ```

## Transformation Types

The following transformation types are supported:

- **direct**: Direct mapping from source field to target field
- **template**: Template-based transformation with placeholders
- **constant**: Set a constant value

## Example

Here's an example of how to use the API Gateway:

1. Create a domain "example.com" with base URL "https://api.example.com"
2. Create an API endpoint for "GET /users" with target URL "https://api.example.com/users"
3. Create a response transformation to map "data.users" to "users"
4. Make a request to "http://example.com/users" or "http://localhost:8000/api/users"

## Contributing

We welcome contributions to the Django API Gateway project! Please follow these guidelines when contributing:

### Branch Naming Convention

When creating a new branch, use the following naming convention:

- `feat/`: For new features or enhancements
  - Example: `feat/add-jwt-authentication`
- `fix/`: For bug fixes
  - Example: `fix/cors-headers-issue`
- `docs/`: For documentation updates
  - Example: `docs/update-installation-guide`
- `test/`: For adding or updating tests
  - Example: `test/add-endpoint-tests`
- `refactor/`: For code refactoring without changing functionality
  - Example: `refactor/improve-middleware-performance`
- `chore/`: For maintenance tasks, dependency updates, etc.
  - Example: `chore/update-django-version`

### Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification for commit messages:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types include:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semicolons, etc.)
- `refactor`: Code changes that neither fix bugs nor add features
- `test`: Adding or updating tests
- `chore`: Changes to the build process or auxiliary tools

Example:
```
feat(transformation): add support for JSON path expressions

Add the ability to use JSON path expressions in transformations
to access nested properties more easily.

Closes #123
```

### Semantic Versioning

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version when making incompatible API changes (X.y.z)
- **MINOR** version when adding functionality in a backward-compatible manner (x.Y.z)
- **PATCH** version when making backward-compatible bug fixes (x.y.Z)

### Pull Request Process

1. Create a branch using the naming convention above
2. Make your changes and commit them using conventional commit messages
3. Update documentation as needed
4. Ensure all tests pass
5. Submit a pull request to the `main` branch
6. Request a review from a maintainer

## License

This project is licensed under the MIT License.
