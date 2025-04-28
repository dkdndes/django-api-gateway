from django.test import TestCase, Client
from django.urls import reverse


class HealthCheckTestCase(TestCase):
    """Test case for the health check endpoint."""

    def setUp(self):
        """Set up the test client."""
        self.client = Client()

    def test_health_check(self):
        """Test that the health check endpoint returns a 200 OK response."""
        response = self.client.get(reverse('gateway:health_check'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Check the response content
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['service'], 'api-gateway')
        self.assertEqual(data['version'], '0.1.2')