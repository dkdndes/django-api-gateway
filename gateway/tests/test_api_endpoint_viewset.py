from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from gateway.models import Domain, ApiEndpoint, RequestTransformation, ResponseTransformation, ApiLog
from gateway.serializers import RequestTransformationSerializer, ResponseTransformationSerializer, ApiLogSerializer
import json


class ApiEndpointViewSetTestCase(TestCase):
    """Test case for the ApiEndpointViewSet."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test domain
        self.domain = Domain.objects.create(
            name="test-domain",
            base_url="https://api.test.com",
            description="Test Domain",
            is_active=True
        )
        
        # Create test endpoint
        self.endpoint = ApiEndpoint.objects.create(
            domain=self.domain,
            path="/users",
            method="GET",
            target_url="https://api.test.com/users",
            timeout=30,
            is_active=True
        )
        
        # Create test request transformations
        self.req_transform1 = RequestTransformation.objects.create(
            endpoint=self.endpoint,
            source_field="user_id",
            target_field="id",
            transformation_type="direct",
            is_active=True
        )
        
        self.req_transform2 = RequestTransformation.objects.create(
            endpoint=self.endpoint,
            source_field="username",
            target_field="name",
            transformation_type="direct",
            is_active=True
        )
        
        # Create test response transformations
        self.res_transform1 = ResponseTransformation.objects.create(
            endpoint=self.endpoint,
            source_field="id",
            target_field="user_id",
            transformation_type="direct",
            is_active=True
        )
        
        self.res_transform2 = ResponseTransformation.objects.create(
            endpoint=self.endpoint,
            source_field="name",
            target_field="username",
            transformation_type="direct",
            is_active=True
        )
        
        # Create test logs
        self.log1 = ApiLog.objects.create(
            endpoint=self.endpoint,
            request_method="GET",
            request_path="/users",
            request_headers=json.dumps({"Content-Type": "application/json"}),
            request_body="",
            response_status=200,
            response_headers=json.dumps({"Content-Type": "application/json"}),
            response_body=json.dumps({"id": 1, "name": "test"}),
            execution_time=0.1
        )
        
        self.log2 = ApiLog.objects.create(
            endpoint=self.endpoint,
            request_method="GET",
            request_path="/users/1",
            request_headers=json.dumps({"Content-Type": "application/json"}),
            request_body="",
            response_status=200,
            response_headers=json.dumps({"Content-Type": "application/json"}),
            response_body=json.dumps({"id": 1, "name": "test"}),
            execution_time=0.2
        )
    
    def test_list_endpoints(self):
        """Test that the endpoints list endpoint returns all endpoints."""
        url = reverse('gateway:apiendpoint-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['path'], self.endpoint.path)
    
    def test_retrieve_endpoint(self):
        """Test that the endpoint detail endpoint returns the correct endpoint."""
        url = reverse('gateway:apiendpoint-detail', args=[self.endpoint.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['path'], self.endpoint.path)
        self.assertEqual(response.data['method'], self.endpoint.method)
        self.assertEqual(response.data['target_url'], self.endpoint.target_url)
    
    def test_request_transformations_action(self):
        """Test the custom 'request_transformations' action on the ApiEndpointViewSet."""
        url = reverse('gateway:apiendpoint-request-transformations', args=[self.endpoint.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that the response contains the correct transformations
        self.assertEqual(len(response.data), 2)
        
        # Get the serialized data for comparison
        transformations = self.endpoint.request_transformations.all()
        serializer = RequestTransformationSerializer(transformations, many=True)
        
        # Check that the response data matches the serialized data
        self.assertEqual(response.data, serializer.data)
        
        # Verify specific transformation data
        self.assertEqual(response.data[0]['source_field'], self.req_transform1.source_field)
        self.assertEqual(response.data[0]['target_field'], self.req_transform1.target_field)
        self.assertEqual(response.data[1]['source_field'], self.req_transform2.source_field)
        self.assertEqual(response.data[1]['target_field'], self.req_transform2.target_field)
    
    def test_response_transformations_action(self):
        """Test the custom 'response_transformations' action on the ApiEndpointViewSet."""
        url = reverse('gateway:apiendpoint-response-transformations', args=[self.endpoint.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that the response contains the correct transformations
        self.assertEqual(len(response.data), 2)
        
        # Get the serialized data for comparison
        transformations = self.endpoint.response_transformations.all()
        serializer = ResponseTransformationSerializer(transformations, many=True)
        
        # Check that the response data matches the serialized data
        self.assertEqual(response.data, serializer.data)
        
        # Verify specific transformation data
        self.assertEqual(response.data[0]['source_field'], self.res_transform1.source_field)
        self.assertEqual(response.data[0]['target_field'], self.res_transform1.target_field)
        self.assertEqual(response.data[1]['source_field'], self.res_transform2.source_field)
        self.assertEqual(response.data[1]['target_field'], self.res_transform2.target_field)
    
    def test_logs_action(self):
        """Test the custom 'logs' action on the ApiEndpointViewSet."""
        url = reverse('gateway:apiendpoint-logs', args=[self.endpoint.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that the response contains the correct logs
        self.assertEqual(len(response.data), 2)
        
        # Get the serialized data for comparison
        logs = self.endpoint.logs.all().order_by('-created_at')[:100]
        serializer = ApiLogSerializer(logs, many=True)
        
        # Check that the response data matches the serialized data
        self.assertEqual(response.data, serializer.data)
        
        # Verify specific log data
        self.assertEqual(response.data[0]['request_path'], self.log2.request_path)
        self.assertEqual(response.data[1]['request_path'], self.log1.request_path)