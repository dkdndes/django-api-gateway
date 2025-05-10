from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from gateway.models import Domain, ApiEndpoint
from gateway.serializers import ApiEndpointSerializer


class DomainViewSetTestCase(TestCase):
    """Test case for the DomainViewSet."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create test domains
        self.domain1 = Domain.objects.create(
            name="test-domain-1",
            base_url="https://api.test1.com",
            description="Test Domain 1",
            is_active=True,
        )

        self.domain2 = Domain.objects.create(
            name="test-domain-2",
            base_url="https://api.test2.com",
            description="Test Domain 2",
            is_active=True,
        )

        # Create test endpoints for domain1
        self.endpoint1 = ApiEndpoint.objects.create(
            domain=self.domain1,
            path="/users",
            method="GET",
            target_url="https://api.test1.com/users",
            timeout=30,
            is_active=True,
        )

        self.endpoint2 = ApiEndpoint.objects.create(
            domain=self.domain1,
            path="/products",
            method="GET",
            target_url="https://api.test1.com/products",
            timeout=30,
            is_active=True,
        )

    def test_list_domains(self):
        """Test that the domains list endpoint returns all domains."""
        url = reverse("gateway:domain-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["name"], self.domain1.name)
        self.assertEqual(response.data[1]["name"], self.domain2.name)

    def test_retrieve_domain(self):
        """Test that the domain detail endpoint returns the correct domain."""
        url = reverse("gateway:domain-detail", args=[self.domain1.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.domain1.name)
        self.assertEqual(response.data["base_url"], self.domain1.base_url)
        self.assertEqual(response.data["description"], self.domain1.description)

    def test_domain_endpoints_action(self):
        """Test the custom 'endpoints' action on the DomainViewSet."""
        url = reverse("gateway:domain-endpoints", args=[self.domain1.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the response contains the correct endpoints
        self.assertEqual(len(response.data), 2)

        # Get the serialized data for comparison
        endpoints = self.domain1.endpoints.all()
        serializer = ApiEndpointSerializer(endpoints, many=True)

        # Check that the response data matches the serialized data
        self.assertEqual(response.data, serializer.data)

        # Verify specific endpoint data
        self.assertEqual(response.data[0]["path"], self.endpoint1.path)
        self.assertEqual(response.data[1]["path"], self.endpoint2.path)
