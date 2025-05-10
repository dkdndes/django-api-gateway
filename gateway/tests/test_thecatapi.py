import json
import pytest
import requests
from unittest.mock import patch, MagicMock
from django.test import RequestFactory
from django.http import HttpResponse
from gateway.middleware import ApiGatewayMiddleware
from gateway.models import (
    Domain,
    ApiEndpoint,
    RequestTransformation,
    ResponseTransformation,
)


@pytest.fixture
def middleware():
    """Create a middleware instance with a mock get_response function"""
    get_response = MagicMock(return_value=HttpResponse("Default response"))
    return ApiGatewayMiddleware(get_response)


@pytest.fixture
def request_factory():
    """Create a request factory for generating test requests"""
    return RequestFactory()


@pytest.fixture
def cat_api_domain(db):
    """Create The Cat API domain"""
    return Domain.objects.create(
        name="thecatapi",
        base_url="https://api.thecatapi.com",
        description="The Cat API - A public service API all about Cats",
        is_active=True,
    )


@pytest.fixture
def cat_api_endpoint(db, cat_api_domain):
    """Create The Cat API endpoint for images/search"""
    return ApiEndpoint.objects.create(
        domain=cat_api_domain,
        path="/images/search",
        method="GET",
        target_url="https://api.thecatapi.com/v1/images/search",
        timeout=30,
        is_active=True,
    )


@pytest.fixture
def cat_api_endpoint_with_apikey(db, cat_api_domain):
    """Create The Cat API endpoint for images/search with API key in URL"""
    return ApiEndpoint.objects.create(
        domain=cat_api_domain,
        path="/images/search/with_apikey",
        method="GET",
        target_url="https://api.thecatapi.com/v1/images/search?api_key=ce4e6963-68ed-4df6-9d5a-40fee969ff84",
        timeout=30,
        is_active=True,
    )


@pytest.mark.django_db
@patch("gateway.middleware.requests.get")
def test_cat_api_request_success(
    mock_get, middleware, request_factory, cat_api_endpoint
):
    """Test successful Cat API request handling"""
    # Mock the response from the Cat API
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = [
        {
            "id": "33j",
            "url": "https://cdn2.thecatapi.com/images/33j.gif",
            "width": 499,
            "height": 316,
        }
    ]
    mock_response.text = json.dumps(
        [
            {
                "id": "33j",
                "url": "https://cdn2.thecatapi.com/images/33j.gif",
                "width": 499,
                "height": 316,
            }
        ]
    )
    mock_get.return_value = mock_response

    # Create a request that matches our cat_api_endpoint
    request = request_factory.get("/images/search")
    request.META["HTTP_HOST"] = "thecatapi"

    # Call the middleware
    response = middleware._handle_api_gateway_request(request)

    # Verify the response
    assert response.status_code == 200
    assert "application/json" in response["Content-Type"]
    assert json.loads(response.content) == [
        {
            "id": "33j",
            "url": "https://cdn2.thecatapi.com/images/33j.gif",
            "width": 499,
            "height": 316,
        }
    ]

    # Verify the external service was called correctly
    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert args[0] == "https://api.thecatapi.com/v1/images/search"
    assert "api_key" not in kwargs.get("params", {})


@pytest.mark.django_db
@patch("gateway.middleware.requests.get")
def test_cat_api_request_with_apikey_in_url(
    mock_get, middleware, request_factory, cat_api_endpoint_with_apikey
):
    """Test Cat API request handling with API key in the URL"""
    # Mock the response from the Cat API
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = [
        {
            "id": "33j",
            "url": "https://cdn2.thecatapi.com/images/33j.gif",
            "width": 499,
            "height": 316,
        }
    ]
    mock_response.text = json.dumps(
        [
            {
                "id": "33j",
                "url": "https://cdn2.thecatapi.com/images/33j.gif",
                "width": 499,
                "height": 316,
            }
        ]
    )
    mock_get.return_value = mock_response

    # Create a request that matches our cat_api_endpoint_with_apikey
    request = request_factory.get("/images/search/with_apikey")
    request.META["HTTP_HOST"] = "thecatapi"

    # Call the middleware
    response = middleware._handle_api_gateway_request(request)

    # Verify the response
    assert response.status_code == 200
    assert "application/json" in response["Content-Type"]
    assert json.loads(response.content) == [
        {
            "id": "33j",
            "url": "https://cdn2.thecatapi.com/images/33j.gif",
            "width": 499,
            "height": 316,
        }
    ]

    # Verify the external service was called correctly with the API key in the URL
    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert (
        args[0]
        == "https://api.thecatapi.com/v1/images/search?api_key=ce4e6963-68ed-4df6-9d5a-40fee969ff84"
    )


@pytest.mark.django_db
@patch("gateway.middleware.requests.get")
def test_cat_api_request_with_query_params(
    mock_get, middleware, request_factory, cat_api_endpoint
):
    """Test Cat API request handling with additional query parameters"""
    # Mock the response from the Cat API
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = [
        {
            "id": "33j",
            "url": "https://cdn2.thecatapi.com/images/33j.gif",
            "width": 499,
            "height": 316,
        }
    ]
    mock_response.text = json.dumps(
        [
            {
                "id": "33j",
                "url": "https://cdn2.thecatapi.com/images/33j.gif",
                "width": 499,
                "height": 316,
            }
        ]
    )
    mock_get.return_value = mock_response

    # Create a request with additional query parameters
    request = request_factory.get("/images/search?limit=1&size=small")
    request.META["HTTP_HOST"] = "thecatapi"

    # Call the middleware
    response = middleware._handle_api_gateway_request(request)

    # Verify the response
    assert response.status_code == 200
    assert "application/json" in response["Content-Type"]

    # Verify the external service was called with the correct query parameters
    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert args[0] == "https://api.thecatapi.com/v1/images/search"
    assert kwargs.get("params", {}).get("limit") == "1"
    assert kwargs.get("params", {}).get("size") == "small"


@pytest.mark.django_db
@patch("gateway.middleware.requests.get")
def test_cat_api_request_with_apikey_header(
    mock_get, middleware, request_factory, cat_api_endpoint
):
    """Test Cat API request handling with API key in the header"""
    # Mock the response from the Cat API
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = [
        {
            "id": "33j",
            "url": "https://cdn2.thecatapi.com/images/33j.gif",
            "width": 499,
            "height": 316,
        }
    ]
    mock_response.text = json.dumps(
        [
            {
                "id": "33j",
                "url": "https://cdn2.thecatapi.com/images/33j.gif",
                "width": 499,
                "height": 316,
            }
        ]
    )
    mock_get.return_value = mock_response

    # Create a request with API key in the header
    request = request_factory.get("/images/search")
    request.META["HTTP_HOST"] = "thecatapi"
    request.META["HTTP_X_API_KEY"] = "ce4e6963-68ed-4df6-9d5a-40fee969ff84"

    # Call the middleware
    response = middleware._handle_api_gateway_request(request)

    # Verify the response
    assert response.status_code == 200
    assert "application/json" in response["Content-Type"]

    # Verify the external service was called with the API key in the header
    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert args[0] == "https://api.thecatapi.com/v1/images/search"
    assert (
        kwargs.get("headers", {}).get("X-Api-Key")
        == "ce4e6963-68ed-4df6-9d5a-40fee969ff84"
    )
