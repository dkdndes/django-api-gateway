from rest_framework import serializers
from .models import CatBreed, CatImage, CatFavorite
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class CatBreedSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatBreed
        fields = "__all__"


class CatImageSerializer(serializers.ModelSerializer):
    breeds = CatBreedSerializer(many=True, read_only=True)

    class Meta:
        model = CatImage
        fields = "__all__"


class CatFavoriteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    image = CatImageSerializer(read_only=True)

    class Meta:
        model = CatFavorite
        fields = "__all__"

    def create(self, validated_data):
        user = self.context["request"].user
        image_id = self.context["request"].data.get("image_id")

        try:
            image = CatImage.objects.get(image_id=image_id)
        except CatImage.DoesNotExist:
            raise serializers.ValidationError({"image_id": "Image not found"})

        favorite, created = CatFavorite.objects.get_or_create(user=user, image=image)

        return favorite
