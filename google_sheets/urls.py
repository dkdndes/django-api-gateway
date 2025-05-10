from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views

# Create a router for the API
router = DefaultRouter()
router.register(r"sheets", views.GoogleSheetViewSet, basename="sheet")

# Create a nested router for sheet data
sheets_router = routers.NestedSimpleRouter(router, r"sheets", lookup="sheet")
sheets_router.register(r"data", views.SheetDataViewSet, basename="sheet-data")

# URL patterns for the API
api_urlpatterns = [
    path("", include(router.urls)),
    path("", include(sheets_router.urls)),
]

# URL patterns for the web views
urlpatterns = [
    path("", views.GoogleSheetListView.as_view(), name="sheet-list"),
    path("<int:pk>/", views.GoogleSheetDetailView.as_view(), name="sheet-detail"),
    # API URLs
    path("api/", include(api_urlpatterns)),
]
