import pytest
from io import StringIO
from django.core.management import call_command
from gateway.models import (
    Domain,
    ApiEndpoint,
    RequestTransformation,
    ResponseTransformation,
)


@pytest.mark.django_db
def test_create_test_data_command():
    """Test the create_test_data management command"""
    # Call the command
    out = StringIO()
    call_command("create_test_data", stdout=out)

    # Check the output
    output = out.getvalue()
    assert "Creating test domains" in output
    assert "Creating test endpoints" in output
    assert "Creating test transformations" in output
    assert "All test data creation completed!" in output

    # Verify the data was created
    # Check domains
    assert Domain.objects.filter(name="jsonplaceholder").exists()
    assert Domain.objects.filter(name="httpbin").exists()
    assert Domain.objects.filter(name="thecatapi").exists()

    # Check endpoints
    jsonplaceholder = Domain.objects.get(name="jsonplaceholder")
    httpbin = Domain.objects.get(name="httpbin")
    catapi = Domain.objects.get(name="thecatapi")

    assert ApiEndpoint.objects.filter(
        domain=jsonplaceholder, path="/posts", method="GET"
    ).exists()
    assert ApiEndpoint.objects.filter(
        domain=jsonplaceholder, path="/posts/{id}", method="GET"
    ).exists()
    assert ApiEndpoint.objects.filter(
        domain=jsonplaceholder, path="/posts", method="POST"
    ).exists()
    assert ApiEndpoint.objects.filter(
        domain=httpbin, path="/get", method="GET"
    ).exists()
    assert ApiEndpoint.objects.filter(
        domain=httpbin, path="/post", method="POST"
    ).exists()

    # Check Cat API endpoints
    assert ApiEndpoint.objects.filter(
        domain=catapi, path="/images/search", method="GET"
    ).exists()
    assert ApiEndpoint.objects.filter(
        domain=catapi, path="/images/search/with_apikey", method="GET"
    ).exists()
    assert ApiEndpoint.objects.filter(
        domain=catapi, path="/images/{id}", method="GET"
    ).exists()

    # Check transformations
    create_post_endpoint = ApiEndpoint.objects.get(
        domain=jsonplaceholder, path="/posts", method="POST"
    )
    post_endpoint = ApiEndpoint.objects.get(domain=httpbin, path="/post", method="POST")
    cat_images_endpoint = ApiEndpoint.objects.get(
        domain=catapi, path="/images/search", method="GET"
    )

    assert RequestTransformation.objects.filter(
        endpoint=create_post_endpoint,
        source_field="title",
        target_field="title",
        transformation_type="template",
    ).exists()

    assert ResponseTransformation.objects.filter(
        endpoint=post_endpoint,
        source_field="data",
        target_field="transformed_data",
        transformation_type="direct",
    ).exists()

    # Check Cat API transformations
    assert ResponseTransformation.objects.filter(
        endpoint=cat_images_endpoint,
        source_field="0.url",
        target_field="image_url",
        transformation_type="direct",
    ).exists()

    assert ResponseTransformation.objects.filter(
        endpoint=cat_images_endpoint,
        source_field="0",
        target_field="first_cat",
        transformation_type="direct",
    ).exists()


@pytest.mark.django_db
def test_create_test_data_command_idempotent():
    """Test that the create_test_data command is idempotent"""
    # Call the command twice
    out1 = StringIO()
    call_command("create_test_data", stdout=out1)

    out2 = StringIO()
    call_command("create_test_data", stdout=out2)

    # Check the output of the second call
    output = out2.getvalue()
    assert "Domain already exists: jsonplaceholder" in output
    assert "Domain already exists: httpbin" in output
    assert "Endpoint already exists:" in output
    assert "Request transformation already exists:" in output
    assert "Response transformation already exists:" in output

    # Verify we don't have duplicates
    assert Domain.objects.filter(name="jsonplaceholder").count() == 1
    assert Domain.objects.filter(name="httpbin").count() == 1

    jsonplaceholder = Domain.objects.get(name="jsonplaceholder")
    assert (
        ApiEndpoint.objects.filter(
            domain=jsonplaceholder, path="/posts", method="GET"
        ).count()
        == 1
    )
