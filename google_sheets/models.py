from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class GoogleSheet(models.Model):
    """Model to store Google Sheet information."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='google_sheets')
    sheet_id = models.CharField(_('Google Sheet ID'), max_length=255)
    name = models.CharField(_('Sheet Name'), max_length=255)
    description = models.TextField(_('Description'), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Google Sheet')
        verbose_name_plural = _('Google Sheets')
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.name

class SheetData(models.Model):
    """Model to store data from Google Sheets."""
    sheet = models.ForeignKey(GoogleSheet, on_delete=models.CASCADE, related_name='data')
    row_data = models.JSONField(_('Row Data'))
    row_number = models.PositiveIntegerField(_('Row Number'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Sheet Data')
        verbose_name_plural = _('Sheet Data')
        ordering = ['row_number']
        unique_together = ['sheet', 'row_number']
    
    def __str__(self):
        return f"{self.sheet.name} - Row {self.row_number}"
