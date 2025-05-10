import pytest
from django.urls import reverse
from django.contrib.messages import get_messages
from gateway.models import (
    Domain,
    ApiEndpoint,
    RequestTransformation,
    ResponseTransformation,
    ApiLog,
)


@pytest.mark.django_db
def test_dashboard_view(client):
    """Test the dashboard view"""
    # Create some test data
    domain = Domain.objects.create(name="test.com", is_active=True)
    ApiEndpoint.objects.create(
        domain=domain,
        path="/test",
        method="GET",
        target_url="https://example.com/api/test",
        is_active=True,
    )

    # Access the dashboard
    response = client.get(reverse("gateway:dashboard"))

    # Check response
    assert response.status_code == 200
    assert "domains_count" in response.context
    assert "endpoints_count" in response.context
    assert "transformations_count" in response.context
    assert "logs_count" in response.context
    assert "recent_endpoints" in response.context
    assert "recent_logs" in response.context

    # Check counts
    assert response.context["domains_count"] == 1
    assert response.context["endpoints_count"] == 1


@pytest.mark.django_db
def test_rules_list_view(client):
    """Test the rules list view"""
    # Create some test data
    domain = Domain.objects.create(name="test.com", is_active=True)
    endpoint = ApiEndpoint.objects.create(
        domain=domain,
        path="/test",
        method="GET",
        target_url="https://example.com/api/test",
        is_active=True,
    )

    # Access the rules list
    response = client.get(reverse("gateway:rules"))

    # Check response
    assert response.status_code == 200
    assert "endpoints" in response.context
    assert len(response.context["endpoints"]) == 1
    assert response.context["endpoints"][0].id == endpoint.id


@pytest.mark.django_db
def test_logs_list_view(client):
    """Test the logs list view"""
    # Create some test data
    domain = Domain.objects.create(name="test.com", is_active=True)
    endpoint = ApiEndpoint.objects.create(
        domain=domain,
        path="/test",
        method="GET",
        target_url="https://example.com/api/test",
        is_active=True,
    )

    # Create some logs
    for i in range(25):  # Create more than one page of logs
        ApiLog.objects.create(
            endpoint=endpoint,
            request_method="GET",
            request_path="/test",
            response_status=200,
            execution_time=0.1,
        )

    # Access the logs list
    response = client.get(reverse("gateway:logs"))

    # Check response
    assert response.status_code == 200
    assert "logs" in response.context
    assert response.context["logs"].paginator.count == 25

    # Test pagination
    response = client.get(reverse("gateway:logs") + "?page=2")
    assert response.status_code == 200
    assert "logs" in response.context


@pytest.mark.django_db
def test_create_rule_get(client):
    """Test the create rule view (GET)"""
    # Create a domain
    Domain.objects.create(name="test.com", is_active=True)

    # Access the create rule form
    response = client.get(reverse("gateway:create_rule"))

    # Check response
    assert response.status_code == 200
    assert "domains" in response.context
    assert len(response.context["domains"]) == 1


@pytest.mark.django_db
def test_create_rule_post(client):
    """Test the create rule view (POST)"""
    # Create a domain
    domain = Domain.objects.create(name="test.com", is_active=True)

    # Submit the form
    data = {
        "domain": domain.id,
        "method": "GET",
        "path": "/test",
        "target_url": "https://example.com/api/test",
        "timeout": 30,
        "is_active": "on",
        "req_source_field[]": ["title"],
        "req_target_field[]": ["title"],
        "req_transform_type[]": ["direct"],
        "req_transform_value[]": [""],
        "res_source_field[]": ["data"],
        "res_target_field[]": ["transformed_data"],
        "res_transform_type[]": ["direct"],
        "res_transform_value[]": [""],
    }

    response = client.post(reverse("gateway:create_rule"), data)

    # Check redirect
    assert response.status_code == 302
    assert response.url == reverse("gateway:rules")

    # Check that the endpoint was created
    assert ApiEndpoint.objects.count() == 1
    endpoint = ApiEndpoint.objects.first()
    assert endpoint.domain == domain
    assert endpoint.path == "/test"
    assert endpoint.method == "GET"

    # Check that transformations were created
    assert RequestTransformation.objects.count() == 1
    assert ResponseTransformation.objects.count() == 1

    # Check messages
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert "Rule created successfully" in str(messages[0])


@pytest.mark.django_db
def test_edit_rule_get(client):
    """Test the edit rule view (GET)"""
    # Create test data
    domain = Domain.objects.create(name="test.com", is_active=True)
    endpoint = ApiEndpoint.objects.create(
        domain=domain,
        path="/test",
        method="GET",
        target_url="https://example.com/api/test",
        is_active=True,
    )

    # Access the edit rule form
    response = client.get(reverse("gateway:edit_rule", args=[endpoint.id]))

    # Check response
    assert response.status_code == 200
    assert "endpoint" in response.context
    assert "domains" in response.context
    assert response.context["endpoint"].id == endpoint.id


@pytest.mark.django_db
def test_edit_rule_post(client):
    """Test the edit rule view (POST)"""
    # Create test data
    domain = Domain.objects.create(name="test.com", is_active=True)
    endpoint = ApiEndpoint.objects.create(
        domain=domain,
        path="/test",
        method="GET",
        target_url="https://example.com/api/test",
        is_active=True,
    )

    # Create transformations
    req_transform = RequestTransformation.objects.create(
        endpoint=endpoint,
        source_field="title",
        target_field="title",
        transformation_type="direct",
        is_active=True,
    )

    # Submit the form with updated data
    data = {
        "domain": domain.id,
        "method": "POST",  # Changed from GET
        "path": "/test-updated",  # Changed
        "target_url": "https://example.com/api/test-updated",  # Changed
        "timeout": 60,  # Changed
        "is_active": "on",
        "req_transform_id[]": [req_transform.id],
        "req_source_field[]": ["title-updated"],  # Changed
        "req_target_field[]": ["title-updated"],  # Changed
        "req_transform_type[]": ["template"],  # Changed
        "req_transform_value[]": ["${title}"],  # Added
        "res_source_field[]": ["data"],  # New transformation
        "res_target_field[]": ["transformed_data"],  # New transformation
        "res_transform_type[]": ["direct"],  # New transformation
        "res_transform_value[]": [""],  # New transformation
    }

    response = client.post(reverse("gateway:edit_rule", args=[endpoint.id]), data)

    # Check redirect
    assert response.status_code == 302
    assert response.url == reverse("gateway:rules")

    # Check that the endpoint was updated
    endpoint.refresh_from_db()
    assert endpoint.method == "POST"
    assert endpoint.path == "/test-updated"
    assert endpoint.target_url == "https://example.com/api/test-updated"
    assert endpoint.timeout == 60

    # Check that transformations were updated
    req_transform.refresh_from_db()
    assert req_transform.source_field == "title-updated"
    assert req_transform.target_field == "title-updated"
    assert req_transform.transformation_type == "template"
    assert req_transform.transformation_value == "${title}"

    # Check that new transformation was created
    assert ResponseTransformation.objects.count() == 1

    # Check messages
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert "Rule updated successfully" in str(messages[0])


@pytest.mark.django_db
def test_toggle_rule(client):
    """Test the toggle rule view"""
    # Create test data
    domain = Domain.objects.create(name="test.com", is_active=True)
    endpoint = ApiEndpoint.objects.create(
        domain=domain,
        path="/test",
        method="GET",
        target_url="https://example.com/api/test",
        is_active=True,
    )

    # Toggle the rule
    response = client.get(reverse("gateway:toggle_rule", args=[endpoint.id]))

    # Check redirect
    assert response.status_code == 302
    assert response.url == reverse("gateway:rules")

    # Check that the endpoint was toggled
    endpoint.refresh_from_db()
    assert endpoint.is_active is False

    # Check messages
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert "Rule disabled successfully" in str(messages[0])

    # Toggle again
    response = client.get(reverse("gateway:toggle_rule", args=[endpoint.id]))
    endpoint.refresh_from_db()
    assert endpoint.is_active is True

    # Check messages
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 2  # One from before, one from now
    assert "Rule enabled successfully" in str(messages[1])


@pytest.mark.django_db
def test_delete_rule(client):
    """Test the delete rule view"""
    # Create test data
    domain = Domain.objects.create(name="test.com", is_active=True)
    endpoint = ApiEndpoint.objects.create(
        domain=domain,
        path="/test",
        method="GET",
        target_url="https://example.com/api/test",
        is_active=True,
    )

    # Delete the rule
    response = client.get(reverse("gateway:delete_rule", args=[endpoint.id]))

    # Check redirect
    assert response.status_code == 302
    assert response.url == reverse("gateway:rules")

    # Check that the endpoint was deleted
    assert ApiEndpoint.objects.count() == 0

    # Check messages
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert "Rule deleted successfully" in str(messages[0])


@pytest.mark.django_db
def test_clear_logs(client):
    """Test the clear logs view"""
    # Create test data
    domain = Domain.objects.create(name="test.com", is_active=True)
    endpoint = ApiEndpoint.objects.create(
        domain=domain,
        path="/test",
        method="GET",
        target_url="https://example.com/api/test",
        is_active=True,
    )

    # Create some logs
    for i in range(5):
        ApiLog.objects.create(
            endpoint=endpoint,
            request_method="GET",
            request_path="/test",
            response_status=200,
            execution_time=0.1,
        )

    assert ApiLog.objects.count() == 5

    # Clear the logs
    response = client.get(reverse("gateway:clear_logs"))

    # Check redirect
    assert response.status_code == 302
    assert response.url == reverse("gateway:logs")

    # Check that the logs were cleared
    assert ApiLog.objects.count() == 0

    # Check messages
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert "Logs cleared successfully" in str(messages[0])
