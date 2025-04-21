# API Gateway with Django

This project implements an API Gateway using Django and Django REST Framework. It allows you to define mapping rules between domains, API endpoints, and API payloads.

## Features

- Map domains to target APIs
- Define API endpoints with transformations
- Transform request and response payloads
- Log API requests and responses
- Admin interface for managing mappings
- REST API for programmatic management

## Models

- **Domain**: Represents a domain that the gateway will handle
- **ApiEndpoint**: Represents an API endpoint with its HTTP method and target URL
- **RequestTransformation**: Defines transformations for request payloads
- **ResponseTransformation**: Defines transformations for response payloads
- **ApiLog**: Logs API requests and responses

## Installation

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

## Usage

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

## License

This project is licensed under the MIT License.