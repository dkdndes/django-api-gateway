import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from gateway.models import Domain, ApiEndpoint, RequestTransformation, ResponseTransformation


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_request_transformation_list(api_client):
    """Test listing request transformations"""
    # Create test data
    domain = Domain.objects.create(name="test.com", is_active=True)
    endpoint = ApiEndpoint.objects.create(
        domain=domain,
        path="/test",
        method="GET",
        target_url="https://example.com/api/test",
        is_active=True
    )
    
    # Create transformations
    for i in range(3):
        RequestTransformation.objects.create(
            endpoint=endpoint,
            source_field=f"source{i}",
            target_field=f"target{i}",
            transformation_type="direct",
            is_active=True
        )
    
    # Make the request
    url = '/api/v1/request-transformations/'
    response = api_client.get(url)
    
    # Check response
    assert response.status_code == 200
    assert len(response.data) == 3
    
    # Check search filter
    response = api_client.get(url + '?search=source1')
    assert response.status_code == 200
    
    # Check ordering
    response = api_client.get(url + '?ordering=-source_field')
    assert response.status_code == 200


@pytest.mark.django_db
def test_request_transformation_detail(api_client):
    """Test retrieving a request transformation"""
    # Create test data
    domain = Domain.objects.create(name="test.com", is_active=True)
    endpoint = ApiEndpoint.objects.create(
        domain=domain,
        path="/test",
        method="GET",
        target_url="https://example.com/api/test",
        is_active=True
    )
    
    # Create transformation
    transform = RequestTransformation.objects.create(
        endpoint=endpoint,
        source_field="source",
        target_field="target",
        transformation_type="direct",
        is_active=True
    )
    
    # Make the request
    url = f'/api/v1/request-transformations/{transform.id}/'
    response = api_client.get(url)
    
    # Check response
    assert response.status_code == 200
    assert response.data['id'] == transform.id
    assert response.data['source_field'] == 'source'
    assert response.data['target_field'] == 'target'
    assert response.data['transformation_type'] == 'direct'


@pytest.mark.django_db
def test_request_transformation_create(api_client):
    """Test creating a request transformation"""
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
        'source_field': 'source',
        'target_field': 'target',
        'transformation_type': 'direct',
        'is_active': True
    }
    
    # Make the request
    url = '/api/v1/request-transformations/'
    response = api_client.post(url, data, format='json')
    
    # Check response
    assert response.status_code == 201
    assert response.data['source_field'] == 'source'
    assert response.data['target_field'] == 'target'
    
    # Check that the transformation was created
    assert RequestTransformation.objects.count() == 1
    transform = RequestTransformation.objects.first()
    assert transform.source_field == 'source'
    assert transform.target_field == 'target'


@pytest.mark.django_db
def test_request_transformation_update(api_client):
    """Test updating a request transformation"""
    # Create test data
    domain = Domain.objects.create(name="test.com", is_active=True)
    endpoint = ApiEndpoint.objects.create(
        domain=domain,
        path="/test",
        method="GET",
        target_url="https://example.com/api/test",
        is_active=True
    )
    
    # Create transformation
    transform = RequestTransformation.objects.create(
        endpoint=endpoint,
        source_field="source",
        target_field="target",
        transformation_type="direct",
        is_active=True
    )
    
    # Prepare data
    data = {
        'endpoint': endpoint.id,
        'source_field': 'updated_source',
        'target_field': 'updated_target',
        'transformation_type': 'template',
        'transformation_value': '${value}',
        'is_active': True
    }
    
    # Make the request
    url = f'/api/v1/request-transformations/{transform.id}/'
    response = api_client.put(url, data, format='json')
    
    # Check response
    assert response.status_code == 200
    assert response.data['source_field'] == 'updated_source'
    assert response.data['target_field'] == 'updated_target'
    assert response.data['transformation_type'] == 'template'
    assert response.data['transformation_value'] == '${value}'
    
    # Check that the transformation was updated
    transform.refresh_from_db()
    assert transform.source_field == 'updated_source'
    assert transform.target_field == 'updated_target'
    assert transform.transformation_type == 'template'
    assert transform.transformation_value == '${value}'


@pytest.mark.django_db
def test_request_transformation_delete(api_client):
    """Test deleting a request transformation"""
    # Create test data
    domain = Domain.objects.create(name="test.com", is_active=True)
    endpoint = ApiEndpoint.objects.create(
        domain=domain,
        path="/test",
        method="GET",
        target_url="https://example.com/api/test",
        is_active=True
    )
    
    # Create transformation
    transform = RequestTransformation.objects.create(
        endpoint=endpoint,
        source_field="source",
        target_field="target",
        transformation_type="direct",
        is_active=True
    )
    
    # Make the request
    url = f'/api/v1/request-transformations/{transform.id}/'
    response = api_client.delete(url)
    
    # Check response
    assert response.status_code == 204
    
    # Check that the transformation was deleted
    assert RequestTransformation.objects.count() == 0


@pytest.mark.django_db
def test_response_transformation_list(api_client):
    """Test listing response transformations"""
    # Create test data
    domain = Domain.objects.create(name="test.com", is_active=True)
    endpoint = ApiEndpoint.objects.create(
        domain=domain,
        path="/test",
        method="GET",
        target_url="https://example.com/api/test",
        is_active=True
    )
    
    # Create transformations
    for i in range(3):
        ResponseTransformation.objects.create(
            endpoint=endpoint,
            source_field=f"source{i}",
            target_field=f"target{i}",
            transformation_type="direct",
            is_active=True
        )
    
    # Make the request
    url = '/api/v1/response-transformations/'
    response = api_client.get(url)
    
    # Check response
    assert response.status_code == 200
    assert len(response.data) == 3
    
    # Check search filter
    response = api_client.get(url + '?search=source1')
    assert response.status_code == 200


@pytest.mark.django_db
def test_response_transformation_detail(api_client):
    """Test retrieving a response transformation"""
    # Create test data
    domain = Domain.objects.create(name="test.com", is_active=True)
    endpoint = ApiEndpoint.objects.create(
        domain=domain,
        path="/test",
        method="GET",
        target_url="https://example.com/api/test",
        is_active=True
    )
    
    # Create transformation
    transform = ResponseTransformation.objects.create(
        endpoint=endpoint,
        source_field="source",
        target_field="target",
        transformation_type="direct",
        is_active=True
    )
    
    # Make the request
    url = f'/api/v1/response-transformations/{transform.id}/'
    response = api_client.get(url)
    
    # Check response
    assert response.status_code == 200
    assert response.data['id'] == transform.id
    assert response.data['source_field'] == 'source'
    assert response.data['target_field'] == 'target'
    assert response.data['transformation_type'] == 'direct'


@pytest.mark.django_db
def test_response_transformation_create(api_client):
    """Test creating a response transformation"""
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
        'source_field': 'source',
        'target_field': 'target',
        'transformation_type': 'direct',
        'is_active': True
    }
    
    # Make the request
    url = '/api/v1/response-transformations/'
    response = api_client.post(url, data, format='json')
    
    # Check response
    assert response.status_code == 201
    assert response.data['source_field'] == 'source'
    assert response.data['target_field'] == 'target'
    
    # Check that the transformation was created
    assert ResponseTransformation.objects.count() == 1
    transform = ResponseTransformation.objects.first()
    assert transform.source_field == 'source'
    assert transform.target_field == 'target'