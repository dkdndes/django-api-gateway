import requests
import time
from django.core.management.base import BaseCommand
from cat_api.models import CatBreed, CatImage
from django.db import transaction


class Command(BaseCommand):
    help = "Load cat breeds and images from TheCatAPI"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = "ce4e6963-68ed-4df6-9d5a-40fee969ff84"
        self.base_url = "https://api.thecatapi.com/v1"
        self.headers = {"x-api-key": self.api_key}

    def add_arguments(self, parser):
        parser.add_argument(
            "--images-per-breed",
            type=int,
            default=5,
            help="Number of images to fetch per breed",
        )

        parser.add_argument(
            "--random-images",
            type=int,
            default=20,
            help="Number of random images to fetch",
        )

    def handle(self, *args, **options):
        images_per_breed = options["images_per_breed"]
        random_images = options["random_images"]

        self.stdout.write(self.style.SUCCESS("Starting to load cat data..."))

        # Load breeds
        self.load_breeds()

        # Load breed images
        self.load_breed_images(images_per_breed)

        # Load random images
        self.load_random_images(random_images)

        self.stdout.write(self.style.SUCCESS("Successfully loaded cat data!"))

    @transaction.atomic
    def load_breeds(self):
        """Load all cat breeds from the API"""
        self.stdout.write("Loading cat breeds...")

        response = requests.get(f"{self.base_url}/breeds", headers=self.headers)

        if response.status_code != 200:
            self.stdout.write(
                self.style.ERROR(f"Failed to fetch breeds: {response.status_code}")
            )
            return

        breeds = response.json()
        self.stdout.write(f"Found {len(breeds)} breeds")

        for breed_data in breeds:
            breed, created = CatBreed.objects.update_or_create(
                breed_id=breed_data["id"],
                defaults={
                    "name": breed_data.get("name", ""),
                    "origin": breed_data.get("origin", ""),
                    "temperament": breed_data.get("temperament", ""),
                    "description": breed_data.get("description", ""),
                    "life_span": breed_data.get("life_span", ""),
                    "weight_imperial": breed_data.get("weight", {}).get("imperial", ""),
                    "weight_metric": breed_data.get("weight", {}).get("metric", ""),
                    "wikipedia_url": breed_data.get("wikipedia_url", ""),
                },
            )

            if created:
                self.stdout.write(f"Created breed: {breed.name}")
            else:
                self.stdout.write(f"Updated breed: {breed.name}")

    def load_breed_images(self, images_per_breed):
        """Load images for each breed"""
        self.stdout.write("Loading breed images...")

        breeds = CatBreed.objects.all()

        for breed in breeds:
            self.stdout.write(f"Loading images for {breed.name}...")

            response = requests.get(
                f"{self.base_url}/images/search",
                params={"breed_ids": breed.breed_id, "limit": images_per_breed},
                headers=self.headers,
            )

            if response.status_code != 200:
                self.stdout.write(
                    self.style.ERROR(
                        f"Failed to fetch images for {breed.name}: {response.status_code}"
                    )
                )
                continue

            images = response.json()

            for image_data in images:
                image, created = CatImage.objects.update_or_create(
                    image_id=image_data["id"],
                    defaults={
                        "url": image_data.get("url", ""),
                        "width": image_data.get("width", 0),
                        "height": image_data.get("height", 0),
                        "breed": breed,
                    },
                )

                if created:
                    self.stdout.write(f"Created image: {image.image_id}")
                else:
                    self.stdout.write(f"Updated image: {image.image_id}")

            # Sleep to avoid rate limiting
            time.sleep(0.5)

    def load_random_images(self, count):
        """Load random cat images"""
        self.stdout.write("Loading random cat images...")

        response = requests.get(
            f"{self.base_url}/images/search",
            params={"limit": count},
            headers=self.headers,
        )

        if response.status_code != 200:
            self.stdout.write(
                self.style.ERROR(
                    f"Failed to fetch random images: {response.status_code}"
                )
            )
            return

        images = response.json()

        for image_data in images:
            # Check if the image has a breed
            breed = None
            if image_data.get("breeds") and len(image_data["breeds"]) > 0:
                breed_data = image_data["breeds"][0]
                try:
                    breed = CatBreed.objects.get(breed_id=breed_data["id"])
                except CatBreed.DoesNotExist:
                    pass

            image, created = CatImage.objects.update_or_create(
                image_id=image_data["id"],
                defaults={
                    "url": image_data.get("url", ""),
                    "width": image_data.get("width", 0),
                    "height": image_data.get("height", 0),
                    "breed": breed,
                },
            )

            if created:
                self.stdout.write(f"Created random image: {image.image_id}")
            else:
                self.stdout.write(f"Updated random image: {image.image_id}")
