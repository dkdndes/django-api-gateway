from django.contrib import admin
from .models import GoogleSheet, SheetData


@admin.register(GoogleSheet)
class GoogleSheetAdmin(admin.ModelAdmin):
    list_display = ("name", "sheet_id", "user", "created_at", "updated_at")
    list_filter = ("user", "created_at", "updated_at")
    search_fields = ("name", "sheet_id", "description", "user__username", "user__email")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"


@admin.register(SheetData)
class SheetDataAdmin(admin.ModelAdmin):
    list_display = ("sheet", "row_number", "created_at", "updated_at")
    list_filter = ("sheet", "created_at", "updated_at")
    search_fields = ("sheet__name", "row_data")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
