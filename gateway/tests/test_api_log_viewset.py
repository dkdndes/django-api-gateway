import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from gateway.models import Domain, ApiEndpoint, ApiLog


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_api_log_list(api_client):
    """Test listing API logs"""
    # Create test data
    domain = Domain.objects.create(name="test.com", is_active=True)
    endpoint = ApiEndpoint.objects.create(
        domain=domain,
        path="/test",
        method="GET",
        target_url="https://example.com/api/test",
        is_active=True
    )
    
    # Create logs
    for i in range(5):
        ApiLog.objects.create(
            endpoint=endpoint,
            request_method="GET",
            request_path=f"/test{i}",
            response_status=200,
            execution_time=0.1 * i
        )
    
    # Make the request
    url = '/api/v1/logs/'
    response = api_client.get(url)
    
    # Check response
    assert response.status_code == 200
    assert len(response.data) == 5
    
    # Check search filter
    response = api_client.get(url + '?search=/test1')
    assert response.status_code == 200
    
    # Check ordering
    response = api_client.get(url + '?ordering=execution_time')
    assert response.status_code == 200


@pytest.mark.django_db
def test_api_log_detail(api_client):
    """Test retrieving an API log"""
    # Create test data
    domain = Domain.objects.create(name="test.com", is_active=True)
    endpoint = ApiEndpoint.objects.create(
        domain=domain,
        path="/test",
        method="GET",
        target_url="https://example.com/api/test",
        is_active=True
    )
    
    # Create log
    log = ApiLog.objects.create(
        endpoint=endpoint,
        request_method="GET",
        request_path="/test",
        response_status=200,
        execution_time=0.1,
        request_headers='{"Content-Type": "application/json"}',
        response_headers='{"Content-Type": "application/json"}',
        request_body='{"test": "data"}',
        response_body='{"result": "success"}'
    )
    
    # Make the request
    url = f'/api/v1/logs/{log.id}/'
    response = api_client.get(url)
    
    # Check response
    assert response.status_code == 200
    assert response.data['id'] == log.id
    assert response.data['request_method'] == 'GET'
    assert response.data['request_path'] == '/test'
    assert response.data['response_status'] == 200
    assert float(response.data['execution_time']) == 0.1
    assert 'request_headers' in response.data
    assert 'response_headers' in response.data
    assert 'request_body' in response.data
    assert 'response_body' in response.data


@pytest.mark.django_db
def test_api_log_create_not_allowed(api_client):
    """Test that creating an API log is not allowed (read-only viewset)"""
    # Create test data
    domain = Domain.objects.create(name="test.com", is_active=True)
    endpoint = ApiEndpoint.objects.create(
        domain=domain,
        path="/test",
        method="GET",
        target_url="https://example.com/api/test",
        is_active=True
    )
    
    # Prepare data
    data = {
        'endpoint': endpoint.id,
        'request_method': 'GET',
        'request_path': '/test',
        'response_status': 200,
        'execution_time': 0.1
    }
    
    # Make the request
    url = '/api/v1/logs/'
    response = api_client.post(url, data, format='json')
    
    # Check response (should be 405 Method Not Allowed)
    assert response.status_code == 405


@pytest.mark.django_db
def test_api_log_update_not_allowed(api_client):
    """Test that updating an API log is not allowed (read-only viewset)"""
    # Create test data
    domain = Domain.objects.create(name="test.com", is_active=True)
    endpoint = ApiEndpoint.objects.create(
        domain=domain,
        path="/test",
        method="GET",
        target_url="https://example.com/api/test",
        is_active=True
    )
    
    # Create log
    log = ApiLog.objects.create(
        endpoint=endpoint,
        request_method="GET",
        request_path="/test",
        response_status=200,
        execution_time=0.1
    )
    
    # Prepare data
    data = {
        'endpoint': endpoint.id,
        'request_method': 'POST',  # Changed
        'request_path': '/test-updated',  # Changed
        'response_status': 201,  # Changed
        'execution_time': 0.2  # Changed
    }
    
    # Make the request
    url = f'/api/v1/logs/{log.id}/'
    response = api_client.put(url, data, format='json')
    
    # Check response (should be 405 Method Not Allowed)
    assert response.status_code == 405


@pytest.mark.django_db
def test_api_log_delete_not_allowed(api_client):
    """Test that deleting an API log is not allowed (read-only viewset)"""
    # Create test data
    domain = Domain.objects.create(name="test.com", is_active=True)
    endpoint = ApiEndpoint.objects.create(
        domain=domain,
        path="/test",
        method="GET",
        target_url="https://example.com/api/test",
        is_active=True
    )
    
    # Create log
    log = ApiLog.objects.create(
        endpoint=endpoint,
        request_method="GET",
        request_path="/test",
        response_status=200,
        execution_time=0.1
    )
    
    # Make the request
    url = f'/api/v1/logs/{log.id}/'
    response = api_client.delete(url)
    
    # Check response (should be 405 Method Not Allowed)
    assert response.status_code == 405