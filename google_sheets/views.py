from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.conf import settings

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from allauth.socialaccount.models import SocialToken, SocialAccount
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from .models import GoogleSheet, SheetData
from .serializers import GoogleSheetSerializer, SheetDataSerializer

import json
import logging

logger = logging.getLogger(__name__)


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class GoogleSheetViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Google Sheets
    """

    serializer_class = GoogleSheetSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return GoogleSheet.objects.filter(user=self.request.user)

    @action(detail=True, methods=["post"])
    def sync(self, request, pk=None):
        """
        Sync data from Google Sheet
        """
        sheet = self.get_object()

        try:
            # Get Google credentials from social account
            social_account = SocialAccount.objects.get(
                user=request.user, provider="google"
            )
            social_token = SocialToken.objects.get(account=social_account)

            # Create credentials object
            credentials = Credentials(
                token=social_token.token,
                refresh_token=social_token.token_secret,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.SOCIALACCOUNT_PROVIDERS["google"]["APP"][
                    "client_id"
                ],
                client_secret=settings.SOCIALACCOUNT_PROVIDERS["google"]["APP"][
                    "secret"
                ],
                scopes=["https://www.googleapis.com/auth/spreadsheets"],
            )

            # Build the Google Sheets API service
            service = build("sheets", "v4", credentials=credentials)

            # Call the Sheets API to get data
            sheet_range = "A1:Z1000"  # Adjust range as needed
            result = (
                service.spreadsheets()
                .values()
                .get(spreadsheetId=sheet.sheet_id, range=sheet_range)
                .execute()
            )

            values = result.get("values", [])

            if not values:
                return Response(
                    {"message": "No data found in sheet"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Get headers from first row
            headers = values[0]

            # Clear existing data
            sheet.data.all().delete()

            # Save data to database
            for i, row in enumerate(values[1:], 1):  # Skip header row
                # Create a dictionary from row data
                row_dict = {}
                for j, cell in enumerate(row):
                    if j < len(headers):  # Make sure we have a header for this cell
                        row_dict[headers[j]] = cell

                # Save to database
                SheetData.objects.create(sheet=sheet, row_number=i, row_data=row_dict)

            return Response(
                {
                    "message": f"Successfully synced {len(values) - 1} rows from Google Sheet",
                    "rows_synced": len(values) - 1,
                }
            )

        except SocialAccount.DoesNotExist:
            return Response(
                {
                    "error": "Google account not connected. Please connect your Google account first."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except SocialToken.DoesNotExist:
            return Response(
                {
                    "error": "Google token not found. Please reconnect your Google account."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"Error syncing Google Sheet: {str(e)}")
            return Response(
                {"error": f"Error syncing Google Sheet: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SheetDataViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Sheet Data (read-only)
    """

    serializer_class = SheetDataSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        sheet_id = self.kwargs.get("sheet_pk")
        if sheet_id:
            return SheetData.objects.filter(
                sheet__id=sheet_id, sheet__user=self.request.user
            )
        return SheetData.objects.filter(sheet__user=self.request.user)


@method_decorator(login_required, name="dispatch")
class GoogleSheetListView(ListView):
    """
    View to list all Google Sheets for the current user
    """

    model = GoogleSheet
    template_name = "google_sheets/sheet_list.html"
    context_object_name = "sheets"

    def get_queryset(self):
        return GoogleSheet.objects.filter(user=self.request.user)


@method_decorator(login_required, name="dispatch")
class GoogleSheetDetailView(DetailView):
    """
    View to show details of a Google Sheet
    """

    model = GoogleSheet
    template_name = "google_sheets/sheet_detail.html"
    context_object_name = "sheet"

    def get_queryset(self):
        return GoogleSheet.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sheet = self.get_object()
        data = sheet.data.all()

        if data.exists():
            # Get all unique keys from all rows
            all_keys = set()
            for item in data:
                all_keys.update(item.row_data.keys())

            # Convert to list and sort
            headers = sorted(list(all_keys))

            # Create a list of rows with all headers
            rows = []
            for item in data:
                row = {"row_number": item.row_number}
                for key in headers:
                    row[key] = item.row_data.get(key, "")
                rows.append(row)

            context["headers"] = headers
            context["rows"] = rows

        return context
