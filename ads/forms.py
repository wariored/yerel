from django import forms
from .models import Category, Ad


class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ['price', 'condition', 'description', 'subcategory', 'location']
