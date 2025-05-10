from django.core.management.base import BaseCommand
from gateway.models import (
    Domain,
    ApiEndpoint,
    RequestTransformation,
    ResponseTransformation,
)
from django.core.management import call_command


class Command(BaseCommand):
    help = "Creates test data for the API Gateway"

    def handle(self, *args, **options):
        # First create the standard test data
        # Create test domains
        self.stdout.write("Creating test domains...")

        # Example domain 1: JSONPlaceholder
        jsonplaceholder, created = Domain.objects.get_or_create(
            name="jsonplaceholder",
            defaults={
                "base_url": "https://jsonplaceholder.typicode.com",
                "description": "JSONPlaceholder is a free online REST API that you can use for testing.",
                "is_active": True,
            },
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(f"Created domain: {jsonplaceholder.name}")
            )
        else:
            self.stdout.write(f"Domain already exists: {jsonplaceholder.name}")

        # Example domain 2: Httpbin
        httpbin, created = Domain.objects.get_or_create(
            name="httpbin",
            defaults={
                "base_url": "https://httpbin.org",
                "description": "A simple HTTP Request & Response Service.",
                "is_active": True,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created domain: {httpbin.name}"))
        else:
            self.stdout.write(f"Domain already exists: {httpbin.name}")

        # Create test endpoints
        self.stdout.write("Creating test endpoints...")

        # JSONPlaceholder endpoints
        posts_endpoint, created = ApiEndpoint.objects.get_or_create(
            domain=jsonplaceholder,
            path="/posts",
            method="GET",
            defaults={
                "target_url": "https://jsonplaceholder.typicode.com/posts",
                "timeout": 30,
                "is_active": True,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created endpoint: {posts_endpoint}"))
        else:
            self.stdout.write(f"Endpoint already exists: {posts_endpoint}")

        post_endpoint, created = ApiEndpoint.objects.get_or_create(
            domain=jsonplaceholder,
            path="/posts/{id}",
            method="GET",
            defaults={
                "target_url": "https://jsonplaceholder.typicode.com/posts/{id}",
                "timeout": 30,
                "is_active": True,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created endpoint: {post_endpoint}"))
        else:
            self.stdout.write(f"Endpoint already exists: {post_endpoint}")

        create_post_endpoint, created = ApiEndpoint.objects.get_or_create(
            domain=jsonplaceholder,
            path="/posts",
            method="POST",
            defaults={
                "target_url": "https://jsonplaceholder.typicode.com/posts",
                "timeout": 30,
                "is_active": True,
            },
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(f"Created endpoint: {create_post_endpoint}")
            )
        else:
            self.stdout.write(f"Endpoint already exists: {create_post_endpoint}")

        # Httpbin endpoints
        get_endpoint, created = ApiEndpoint.objects.get_or_create(
            domain=httpbin,
            path="/get",
            method="GET",
            defaults={
                "target_url": "https://httpbin.org/get",
                "timeout": 30,
                "is_active": True,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created endpoint: {get_endpoint}"))
        else:
            self.stdout.write(f"Endpoint already exists: {get_endpoint}")

        post_endpoint, created = ApiEndpoint.objects.get_or_create(
            domain=httpbin,
            path="/post",
            method="POST",
            defaults={
                "target_url": "https://httpbin.org/post",
                "timeout": 30,
                "is_active": True,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created endpoint: {post_endpoint}"))
        else:
            self.stdout.write(f"Endpoint already exists: {post_endpoint}")

        # Create test transformations
        self.stdout.write("Creating test transformations...")

        # Request transformation for create_post_endpoint
        req_transform, created = RequestTransformation.objects.get_or_create(
            endpoint=create_post_endpoint,
            source_field="title",
            target_field="title",
            defaults={
                "transformation_type": "template",
                "transformation_value": "Transformed: ${title}",
                "is_active": True,
            },
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(f"Created request transformation: {req_transform}")
            )
        else:
            self.stdout.write(f"Request transformation already exists: {req_transform}")

        # Response transformation for post_endpoint
        resp_transform, created = ResponseTransformation.objects.get_or_create(
            endpoint=post_endpoint,
            source_field="data",
            target_field="transformed_data",
            defaults={"transformation_type": "direct", "is_active": True},
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(f"Created response transformation: {resp_transform}")
            )
        else:
            self.stdout.write(
                f"Response transformation already exists: {resp_transform}"
            )

        self.stdout.write(self.style.SUCCESS("Standard test data creation completed!"))

        # Now create The Cat API test data
        self.stdout.write("Creating The Cat API test data...")
        call_command("create_catapi_data")

        self.stdout.write(self.style.SUCCESS("All test data creation completed!"))
