"""
URL configuration for api_gateway_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
# from rest_framework.documentation import include_docs_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("gateway.urls")),
    path("api-auth/", include("rest_framework.urls")),
    # path('docs/', include_docs_urls(title='API Gateway API')),
    # Django AllAuth URLs
    path("accounts/", include("allauth.urls")),
    # Google Sheets URLs
    path("sheets/", include("google_sheets.urls")),
    # Cat API URLs
    path("cats/", include("cat_api.urls")),
]
