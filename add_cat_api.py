import os
import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api_gateway_project.settings")
django.setup()

from gateway.models import (
    Domain,
    ApiEndpoint,
    RequestTransformation,
    ResponseTransformation,
)

# Create TheCatAPI domain
cat_api_domain, created = Domain.objects.get_or_create(
    name="thecatapi",
    defaults={
        "base_url": "https://api.thecatapi.com/v1",
        "description": "The Cat API - A public service API all about Cats",
        "is_active": True,
    },
)

if created:
    print(f"Created new domain: {cat_api_domain.name}")
else:
    print(f"Domain already exists: {cat_api_domain.name}")

# Create endpoints for TheCatAPI

# 1. Get random cat images
random_cats_endpoint, created = ApiEndpoint.objects.get_or_create(
    domain=cat_api_domain,
    path="/cats/random",
    method="GET",
    defaults={
        "target_url": "https://api.thecatapi.com/v1/images/search",
        "timeout": 30,
        "is_active": True,
    },
)

if created:
    print(f"Created endpoint: {random_cats_endpoint}")

    # Add request transformation to add the API key
    RequestTransformation.objects.create(
        endpoint=random_cats_endpoint,
        source_field="",
        target_field="x-api-key",
        transformation_type="constant",
        transformation_value="ce4e6963-68ed-4df6-9d5a-40fee969ff84",
        is_active=True,
    )
else:
    print(f"Endpoint already exists: {random_cats_endpoint}")

# 2. Get cat breeds
breeds_endpoint, created = ApiEndpoint.objects.get_or_create(
    domain=cat_api_domain,
    path="/cats/breeds",
    method="GET",
    defaults={
        "target_url": "https://api.thecatapi.com/v1/breeds",
        "timeout": 30,
        "is_active": True,
    },
)

if created:
    print(f"Created endpoint: {breeds_endpoint}")

    # Add request transformation to add the API key
    RequestTransformation.objects.create(
        endpoint=breeds_endpoint,
        source_field="",
        target_field="x-api-key",
        transformation_type="constant",
        transformation_value="ce4e6963-68ed-4df6-9d5a-40fee969ff84",
        is_active=True,
    )
else:
    print(f"Endpoint already exists: {breeds_endpoint}")

# 3. Get cat breed by ID
breed_by_id_endpoint, created = ApiEndpoint.objects.get_or_create(
    domain=cat_api_domain,
    path="/cats/breed",
    method="GET",
    defaults={
        "target_url": "https://api.thecatapi.com/v1/breeds",
        "timeout": 30,
        "is_active": True,
    },
)

if created:
    print(f"Created endpoint: {breed_by_id_endpoint}")

    # Add request transformation to add the API key
    RequestTransformation.objects.create(
        endpoint=breed_by_id_endpoint,
        source_field="",
        target_field="x-api-key",
        transformation_type="constant",
        transformation_value="ce4e6963-68ed-4df6-9d5a-40fee969ff84",
        is_active=True,
    )
else:
    print(f"Endpoint already exists: {breed_by_id_endpoint}")

# 4. Get cat images by breed
images_by_breed_endpoint, created = ApiEndpoint.objects.get_or_create(
    domain=cat_api_domain,
    path="/cats/images/breed",
    method="GET",
    defaults={
        "target_url": "https://api.thecatapi.com/v1/images/search",
        "timeout": 30,
        "is_active": True,
    },
)

if created:
    print(f"Created endpoint: {images_by_breed_endpoint}")

    # Add request transformation to add the API key
    RequestTransformation.objects.create(
        endpoint=images_by_breed_endpoint,
        source_field="",
        target_field="x-api-key",
        transformation_type="constant",
        transformation_value="ce4e6963-68ed-4df6-9d5a-40fee969ff84",
        is_active=True,
    )
else:
    print(f"Endpoint already exists: {images_by_breed_endpoint}")

print("TheCatAPI integration completed!")
