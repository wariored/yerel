from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Ad, AdUser, AdFile, Location


def categories(request):
    categories_t = Category.objects.filter(category_type='T')
    return render(request, 'ads/categories_pages/categories.html',
                  dict(categories_t=categories_t),
    )
