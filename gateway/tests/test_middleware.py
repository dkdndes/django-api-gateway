import json
import pytest
import requests
from unittest.mock import patch, MagicMock
from django.test import RequestFactory
from django.http import HttpResponse, JsonResponse
from gateway.middleware import ApiGatewayMiddleware
from gateway.models import (
    Domain,
    ApiEndpoint,
    RequestTransformation,
    ResponseTransformation,
    ApiLog,
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
def domain(db):
    """Create a test domain"""
    return Domain.objects.create(
        name="example.com",
        base_url="https://example.com",
        description="Test domain",
        is_active=True,
    )


@pytest.fixture
def api_endpoint(db, domain):
    """Create a test API endpoint"""
    return ApiEndpoint.objects.create(
        domain=domain,
        path="/test",
        method="GET",
        target_url="https://example.com/api/test",
        timeout=30,
        is_active=True,
    )


@pytest.mark.django_db
def test_should_handle_request_admin_path(middleware, request_factory):
    """Test that admin paths are not handled by the middleware"""
    request = request_factory.get("/admin/login/")
    assert middleware._should_handle_request(request) is False


@pytest.mark.django_db
def test_should_handle_request_api_path(middleware, request_factory):
    """Test that API paths are handled by the middleware"""
    request = request_factory.get("/api/test")
    assert middleware._should_handle_request(request) is True


@pytest.mark.django_db
def test_should_handle_request_with_matching_endpoint(
    middleware, request_factory, api_endpoint
):
    """Test that paths with matching endpoints are handled by the middleware"""
    # Set up the request with the correct host
    request = request_factory.get("/test")
    request.META["HTTP_HOST"] = "example.com"

    # This should match our api_endpoint fixture
    assert middleware._should_handle_request(request) is True


@pytest.mark.django_db
def test_should_handle_request_with_no_matching_endpoint(
    middleware, request_factory, domain
):
    """Test that paths without matching endpoints are not handled by the middleware"""
    request = request_factory.get("/nonexistent")
    request.META["HTTP_HOST"] = "example.com"

    # No endpoint matches this path
    assert middleware._should_handle_request(request) is False


@pytest.mark.django_db
def test_normalize_path(middleware):
    """Test path normalization"""
    assert middleware._normalize_path("/test/") == "/test"
    assert middleware._normalize_path("/test") == "/test"
    assert middleware._normalize_path("/") == "/"


@pytest.mark.django_db
@patch("gateway.middleware.requests.get")
def test_handle_api_gateway_request_success(
    mock_get, middleware, request_factory, api_endpoint
):
    """Test successful API gateway request handling"""
    # Mock the response from the external service
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"data": "test_data"}
    mock_response.text = json.dumps({"data": "test_data"})
    mock_get.return_value = mock_response

    # Create a request that matches our api_endpoint
    request = request_factory.get("/test")
    request.META["HTTP_HOST"] = "example.com"

    # Call the middleware
    response = middleware._handle_api_gateway_request(request)

    # Verify the response
    assert response.status_code == 200
    assert "application/json" in response["Content-Type"]
    assert json.loads(response.content) == {"data": "test_data"}

    # Verify the external service was called correctly
    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert args[0] == "https://example.com/api/test"


@pytest.mark.django_db
@patch("gateway.middleware.requests.get")
def test_handle_api_gateway_request_not_found(
    mock_get, middleware, request_factory, domain
):
    """Test API gateway request handling when no endpoint is found"""
    # Create a request with a path that doesn't match any endpoint
    request = request_factory.get("/nonexistent")
    request.META["HTTP_HOST"] = "example.com"

    # Call the middleware
    response = middleware._handle_api_gateway_request(request)

    # Verify the response is a 404
    assert response.status_code == 404
    assert "application/json" in response["Content-Type"]
    response_data = json.loads(response.content)
    assert response_data["error"] == "Not Found"

    # Verify no external service was called
    mock_get.assert_not_called()


@pytest.mark.django_db
@patch("gateway.middleware.requests.get")
def test_handle_api_gateway_request_error(
    mock_get, middleware, request_factory, api_endpoint
):
    """Test API gateway request handling when the external service returns an error"""
    # Mock the response from the external service to raise an exception
    mock_get.side_effect = requests.RequestException("Connection error")

    # Create a request that matches our api_endpoint
    request = request_factory.get("/test")
    request.META["HTTP_HOST"] = "example.com"

    # Call the middleware
    response = middleware._handle_api_gateway_request(request)

    # Verify the response is a 502
    assert response.status_code == 502
    assert "application/json" in response["Content-Type"]
    response_data = json.loads(response.content)
    assert response_data["error"] == "Gateway Error"

    # Verify the external service was called
    mock_get.assert_called_once()


@pytest.mark.django_db
def test_get_nested_value(middleware):
    """Test getting nested values from dictionaries"""
    data = {"a": 1, "b": {"c": 2, "d": {"e": 3}}, "f": [{"g": 4}, {"g": 5}]}

    assert middleware._get_nested_value(data, "a") == 1
    assert middleware._get_nested_value(data, "b.c") == 2
    assert middleware._get_nested_value(data, "b.d.e") == 3
    assert middleware._get_nested_value(data, "f.0.g") == 4
    assert middleware._get_nested_value(data, "f.1.g") == 5
    assert middleware._get_nested_value(data, "nonexistent") is None
    assert middleware._get_nested_value(data, "b.nonexistent") is None


@pytest.mark.django_db
def test_set_nested_value(middleware):
    """Test setting nested values in dictionaries"""
    data = {"a": 1, "b": {"c": 2}}

    # Set existing top-level key
    middleware._set_nested_value(data, "a", 10)
    assert data["a"] == 10

    # Set existing nested key
    middleware._set_nested_value(data, "b.c", 20)
    assert data["b"]["c"] == 20

    # Set new top-level key
    middleware._set_nested_value(data, "d", 30)
    assert data["d"] == 30

    # Set new nested key in existing path
    middleware._set_nested_value(data, "b.e", 40)
    assert data["b"]["e"] == 40

    # Set new nested key in new path
    middleware._set_nested_value(data, "f.g", 50)
    assert data["f"]["g"] == 50


@pytest.mark.django_db
@patch("gateway.middleware.ApiLog")
def test_log_request(mock_api_log_class, middleware, request_factory, api_endpoint):
    """Test request logging"""
    request = request_factory.get("/test")
    request.META["HTTP_HOST"] = "example.com"

    # Set up the mock ApiLog instance
    mock_api_log = MagicMock()
    mock_api_log_class.return_value = mock_api_log

    # Call the log_request method
    middleware._log_request(
        endpoint=api_endpoint,
        request=request,
        request_body={"test": "data"},
        response_status=200,
        response_headers={"Content-Type": "application/json"},
        response_body=json.dumps({"result": "success"}),
        execution_time=0.5,
    )

    # Verify the log was created with correct parameters
    mock_api_log_class.assert_called_once()
    args, kwargs = mock_api_log_class.call_args
    assert kwargs["endpoint"] == api_endpoint
    assert kwargs["request_method"] == "GET"
    assert kwargs["request_path"] == "/test"
    assert kwargs["response_status"] == 200
    assert kwargs["execution_time"] == 0.5

    # Verify set_request_headers and set_response_headers were called
    mock_api_log.set_request_headers.assert_called_once()
    mock_api_log.set_response_headers.assert_called_once()

    # Verify save was called
    mock_api_log.save.assert_called_once()
