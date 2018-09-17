from rest_framework import serializers
from .models import Category, Subcategory, Ad, Location, AdFile, AdUser

#Here is the serializer view part, do not touch please, not yet
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'icon')

class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ('id', 'name', 'category')

class AdUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdUser
        fields = ('id', 'given_name', 'phone_number', 'email', 'user')

class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = ('id', 'title', 'price', 'condition', 'description', 'subcategory', 'creation_date', 'location')

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'name')

class AdFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'ad', 'media')


        