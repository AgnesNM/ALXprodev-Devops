# pokemon_api/models.py
from django.db import models
from django.utils import timezone
import json


class Pokemon(models.Model):
    """Model to store Pokemon data from the API"""
    pokemon_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100, unique=True)
    height = models.IntegerField()  # in decimeters
    weight = models.IntegerField()  # in hectograms
    base_experience = models.IntegerField(null=True, blank=True)
    raw_data = models.JSONField()  # Store complete API response
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['pokemon_id']

    def __str__(self):
        return f"{self.name} (#{self.pokemon_id})"

    @property
    def height_in_meters(self):
        return self.height * 0.1

    @property
    def weight_in_kg(self):
        return self.weight * 0.1

    @property
    def types(self):
        """Extract types from raw_data"""
        if self.raw_data and 'types' in self.raw_data:
            return [type_data['type']['name'] for type_data in self.raw_data['types']]
        return []

    @property
    def abilities(self):
        """Extract regular abilities from raw_data"""
        if self.raw_data and 'abilities' in self.raw_data:
            return [
                ability['ability']['name'] 
                for ability in self.raw_data['abilities'] 
                if not ability['is_hidden']
            ]
        return []

    @property
    def hidden_abilities(self):
        """Extract hidden abilities from raw_data"""
        if self.raw_data and 'abilities' in self.raw_data:
            return [
                ability['ability']['name'] 
                for ability in self.raw_data['abilities'] 
                if ability['is_hidden']
            ]
        return []

    @property
    def base_stats(self):
        """Extract base stats from raw_data"""
        if self.raw_data and 'stats' in self.raw_data:
            return {
                stat['stat']['name']: stat['base_stat'] 
                for stat in self.raw_data['stats']
            }
        return {}


class APIRequest(models.Model):
    """Model to log API requests and errors"""
    pokemon_name = models.CharField(max_length=100)
    success = models.BooleanField()
    error_message = models.TextField(blank=True)
    http_status_code = models.IntegerField(null=True, blank=True)
    request_timestamp = models.DateTimeField(auto_now_add=True)
    response_data = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-request_timestamp']

    def __str__(self):
        status = "SUCCESS" if self.success else "ERROR"
        return f"{self.pokemon_name} - {status} ({self.request_timestamp})"
