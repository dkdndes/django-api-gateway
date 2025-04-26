from django.test import TestCase, Client
from django.urls import reverse
from gateway.models import Domain, ApiEndpoint, RequestTransformation, ResponseTransformation, ApiLog
import json


class WebViewsTestCase(TestCase):
    """Test case for the web interface views."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
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
        
        # Create test request transformation
        self.req_transform = RequestTransformation.objects.create(
            endpoint=self.endpoint,
            source_field="user_id",
            target_field="id",
            transformation_type="direct",
            is_active=True
        )
        
        # Create test response transformation
        self.res_transform = ResponseTransformation.objects.create(
            endpoint=self.endpoint,
            source_field="id",
            target_field="user_id",
            transformation_type="direct",
            is_active=True
        )
        
        # Create test log
        self.log = ApiLog.objects.create(
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
    
    def test_dashboard_view(self):
        """Test the dashboard view."""
        url = reverse('gateway:dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gateway/dashboard.html')
        
        # Check that the context contains the correct data
        self.assertEqual(response.context['domains_count'], 1)
        self.assertEqual(response.context['endpoints_count'], 1)
        self.assertEqual(response.context['transformations_count'], 2)  # 1 request + 1 response
        self.assertEqual(response.context['logs_count'], 1)
        
        # Check that the recent endpoints and logs are in the context
        self.assertEqual(len(response.context['recent_endpoints']), 1)
        self.assertEqual(len(response.context['recent_logs']), 1)
        self.assertEqual(response.context['recent_endpoints'][0], self.endpoint)
        self.assertEqual(response.context['recent_logs'][0], self.log)
    
    def test_rules_list_view(self):
        """Test the rules list view."""
        url = reverse('gateway:rules')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gateway/rules.html')
        
        # Check that the context contains the correct data
        self.assertEqual(len(response.context['endpoints']), 1)
        self.assertEqual(response.context['endpoints'][0], self.endpoint)
    
    def test_logs_list_view(self):
        """Test the logs list view."""
        url = reverse('gateway:logs')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gateway/logs.html')
        
        # Check that the context contains the correct data
        self.assertEqual(len(response.context['logs']), 1)
        self.assertEqual(response.context['logs'][0], self.log)
    
    def test_toggle_rule_view(self):
        """Test the toggle rule view."""
        # Check initial state
        self.assertTrue(self.endpoint.is_active)
        
        # Toggle the rule
        url = reverse('gateway:toggle_rule', args=[self.endpoint.id])
        response = self.client.get(url)
        
        # Check that we're redirected to the rules page
        self.assertRedirects(response, reverse('gateway:rules'))
        
        # Check that the endpoint is now inactive
        self.endpoint.refresh_from_db()
        self.assertFalse(self.endpoint.is_active)
        
        # Toggle it back
        response = self.client.get(url)
        self.endpoint.refresh_from_db()
        self.assertTrue(self.endpoint.is_active)
    
    def test_clear_logs_view(self):
        """Test the clear logs view."""
        # Check initial state
        self.assertEqual(ApiLog.objects.count(), 1)
        
        # Clear the logs
        url = reverse('gateway:clear_logs')
        response = self.client.get(url)
        
        # Check that we're redirected to the logs page
        self.assertRedirects(response, reverse('gateway:logs'))
        
        # Check that the logs are cleared
        self.assertEqual(ApiLog.objects.count(), 0)