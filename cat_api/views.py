import requests
import json
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.http import JsonResponse
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CatBreed, CatImage, CatFavorite
from .serializers import CatBreedSerializer, CatImageSerializer, CatFavoriteSerializer


# TheCatAPI configuration
CAT_API_KEY = 'ce4e6963-68ed-4df6-9d5a-40fee969ff84'
CAT_API_BASE_URL = 'https://api.thecatapi.com/v1'
CAT_API_HEADERS = {
    'x-api-key': CAT_API_KEY,
    'Content-Type': 'application/json'
}


class CatBreedViewSet(viewsets.ModelViewSet):
    """
    API endpoint for cat breeds
    """
    queryset = CatBreed.objects.all()
    serializer_class = CatBreedSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def sync(self, request):
        """Sync cat breeds from TheCatAPI"""
        try:
            response = requests.get(
                f"{CAT_API_BASE_URL}/breeds",
                headers=CAT_API_HEADERS
            )
            response.raise_for_status()
            
            breeds_data = response.json()
            breeds_synced = 0
            
            for breed_data in breeds_data:
                breed, created = CatBreed.objects.update_or_create(
                    breed_id=breed_data['id'],
                    defaults={
                        'name': breed_data.get('name', ''),
                        'description': breed_data.get('description', ''),
                        'temperament': breed_data.get('temperament', ''),
                        'origin': breed_data.get('origin', ''),
                        'life_span': breed_data.get('life_span', ''),
                        'wikipedia_url': breed_data.get('wikipedia_url', ''),
                        'weight_imperial': breed_data.get('weight', {}).get('imperial', ''),
                        'weight_metric': breed_data.get('weight', {}).get('metric', '')
                    }
                )
                breeds_synced += 1
                
            return Response({
                'success': True,
                'message': f'Successfully synced {breeds_synced} cat breeds'
            })
            
        except requests.exceptions.RequestException as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CatImageViewSet(viewsets.ModelViewSet):
    """
    API endpoint for cat images
    """
    queryset = CatImage.objects.all()
    serializer_class = CatImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def random(self, request):
        """Get random cat images"""
        try:
            limit = int(request.query_params.get('limit', 1))
            breed_id = request.query_params.get('breed_id', None)
            
            params = {
                'limit': min(limit, 10),  # Cap at 10 images
                'has_breeds': 1
            }
            
            if breed_id:
                params['breed_id'] = breed_id
                
            response = requests.get(
                f"{CAT_API_BASE_URL}/images/search",
                headers=CAT_API_HEADERS,
                params=params
            )
            response.raise_for_status()
            
            images_data = response.json()
            saved_images = []
            
            for image_data in images_data:
                # Save image to database
                image, created = CatImage.objects.update_or_create(
                    image_id=image_data['id'],
                    defaults={
                        'url': image_data.get('url', ''),
                        'width': image_data.get('width', 0),
                        'height': image_data.get('height', 0)
                    }
                )
                
                # Associate breeds with image
                if 'breeds' in image_data and image_data['breeds']:
                    for breed_data in image_data['breeds']:
                        breed, _ = CatBreed.objects.get_or_create(
                            breed_id=breed_data['id'],
                            defaults={
                                'name': breed_data.get('name', ''),
                                'description': breed_data.get('description', ''),
                                'temperament': breed_data.get('temperament', ''),
                                'origin': breed_data.get('origin', ''),
                                'life_span': breed_data.get('life_span', ''),
                                'wikipedia_url': breed_data.get('wikipedia_url', ''),
                                'weight_imperial': breed_data.get('weight', {}).get('imperial', ''),
                                'weight_metric': breed_data.get('weight', {}).get('metric', '')
                            }
                        )
                        image.breeds.add(breed)
                
                saved_images.append(image)
            
            serializer = self.get_serializer(saved_images, many=True)
            return Response(serializer.data)
            
        except requests.exceptions.RequestException as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class CatFavoriteViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user's favorite cat images
    """
    serializer_class = CatFavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CatFavorite.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, 
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=False, methods=['delete'])
    def remove(self, request):
        """Remove a cat image from favorites"""
        image_id = request.query_params.get('image_id')
        if not image_id:
            return Response({
                'success': False,
                'error': 'image_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            image = CatImage.objects.get(image_id=image_id)
            favorite = CatFavorite.objects.get(user=request.user, image=image)
            favorite.delete()
            return Response({
                'success': True,
                'message': 'Image removed from favorites'
            })
        except (CatImage.DoesNotExist, CatFavorite.DoesNotExist):
            return Response({
                'success': False,
                'error': 'Favorite not found'
            }, status=status.HTTP_404_NOT_FOUND)


# Web views
def cat_home(request):
    """Home page for cat API web interface"""
    return render(request, 'cat_api/home.html')


def cat_breeds(request):
    """Page to display cat breeds"""
    breeds = CatBreed.objects.all().order_by('name')
    return render(request, 'cat_api/breeds.html', {'breeds': breeds})


def cat_breed_detail(request, breed_id):
    """Page to display details of a specific cat breed"""
    breed = get_object_or_404(CatBreed, breed_id=breed_id)
    return render(request, 'cat_api/breed_detail.html', {'breed': breed})


def cat_favorites(request):
    """Page to display user's favorite cat images"""
    if not request.user.is_authenticated:
        return render(request, 'cat_api/login_required.html')
        
    favorites = CatFavorite.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'cat_api/favorites.html', {'favorites': favorites})
