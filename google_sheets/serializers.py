from rest_framework import serializers
from .models import GoogleSheet, SheetData
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'username', 'email']

class SheetDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SheetData
        fields = ['id', 'row_data', 'row_number', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class GoogleSheetSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    data = SheetDataSerializer(many=True, read_only=True)
    
    class Meta:
        model = GoogleSheet
        fields = ['id', 'user', 'sheet_id', 'name', 'description', 'created_at', 'updated_at', 'data']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        user = self.context['request'].user
        google_sheet = GoogleSheet.objects.create(user=user, **validated_data)
        return google_sheet