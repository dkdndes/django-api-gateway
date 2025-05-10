from django.core.management.base import BaseCommand
from gateway.models import (
    Domain,
    ApiEndpoint,
    RequestTransformation,
    ResponseTransformation,
)


class Command(BaseCommand):
    help = "Creates The Cat API test data for the API Gateway"

    def handle(self, *args, **options):
        # Create The Cat API domain
        self.stdout.write("Creating The Cat API domain...")

        cat_api, created = Domain.objects.get_or_create(
            name="thecatapi",
            defaults={
                "base_url": "https://api.thecatapi.com",
                "description": "The Cat API - A public service API all about Cats",
                "is_active": True,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created domain: {cat_api.name}"))
        else:
            self.stdout.write(f"Domain already exists: {cat_api.name}")

        # Create The Cat API endpoints
        self.stdout.write("Creating The Cat API endpoints...")

        # Standard endpoint without API key
        images_search_endpoint, created = ApiEndpoint.objects.get_or_create(
            domain=cat_api,
            path="/images/search",
            method="GET",
            defaults={
                "target_url": "https://api.thecatapi.com/v1/images/search",
                "timeout": 30,
                "is_active": True,
            },
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(f"Created endpoint: {images_search_endpoint}")
            )
        else:
            self.stdout.write(f"Endpoint already exists: {images_search_endpoint}")

        # Endpoint with API key in URL
        images_search_apikey_endpoint, created = ApiEndpoint.objects.get_or_create(
            domain=cat_api,
            path="/images/search/with_apikey",
            method="GET",
            defaults={
                "target_url": "https://api.thecatapi.com/v1/images/search?api_key=ce4e6963-68ed-4df6-9d5a-40fee969ff84",
                "timeout": 30,
                "is_active": True,
            },
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(f"Created endpoint: {images_search_apikey_endpoint}")
            )
        else:
            self.stdout.write(
                f"Endpoint already exists: {images_search_apikey_endpoint}"
            )

        # Endpoint for specific image by ID
        image_by_id_endpoint, created = ApiEndpoint.objects.get_or_create(
            domain=cat_api,
            path="/images/{id}",
            method="GET",
            defaults={
                "target_url": "https://api.thecatapi.com/v1/images/{id}",
                "timeout": 30,
                "is_active": True,
            },
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(f"Created endpoint: {image_by_id_endpoint}")
            )
        else:
            self.stdout.write(f"Endpoint already exists: {image_by_id_endpoint}")

        # Create transformations
        self.stdout.write("Creating transformations for The Cat API...")

        # Response transformation to extract the first image URL
        first_image_transform, created = ResponseTransformation.objects.get_or_create(
            endpoint=images_search_endpoint,
            source_field="0.url",
            target_field="image_url",
            defaults={"transformation_type": "direct", "is_active": True},
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created response transformation: {first_image_transform}"
                )
            )
        else:
            self.stdout.write(
                f"Response transformation already exists: {first_image_transform}"
            )

        # Response transformation to create a simplified response
        simplified_response_transform, created = (
            ResponseTransformation.objects.get_or_create(
                endpoint=images_search_endpoint,
                source_field="0",
                target_field="first_cat",
                defaults={"transformation_type": "direct", "is_active": True},
            )
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created response transformation: {simplified_response_transform}"
                )
            )
        else:
            self.stdout.write(
                f"Response transformation already exists: {simplified_response_transform}"
            )

        self.stdout.write(self.style.SUCCESS("The Cat API data creation completed!"))
